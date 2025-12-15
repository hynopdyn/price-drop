#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <TFT_eSPI.h>
#include <TJpg_Decoder.h>

TFT_eSPI tft = TFT_eSPI();
const char* ssid = "ssid";
const char* password = "pass";
const char* api_url = "http://192.168.1.18:5000/prices";

bool tft_output(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t* bitmap) {
  if (y >= tft.height()) return 0;
  tft.pushImage(x, y, w, h, bitmap);
  return 1;
}

void replace_substring(char *str, const char *from, const char *to) {
    size_t from_len = strlen(from);
    size_t to_len   = strlen(to);

    char *p = strstr(str, from);
    if (!p) return;

    // Only safe if to_len <= from_len (true for _FMjpg_)
    memmove(p + to_len, p + from_len, strlen(p + from_len) + 1);
    memcpy(p, to, to_len);
}

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.setSwapBytes(true);
  TJpgDec.setJpgScale(1);
  TJpgDec.setCallback(tft_output);
  WiFi.begin(ssid, password);

  Serial.println("Connecting WiFi");
  tft.println("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    tft.print(".");
  }
  Serial.println("\nWiFi connected");
}

bool downloadAndDrawJpg(const char* url, int x, int y) {
  HTTPClient http;
  http.begin(url);
  int httpCode = http.GET();
  
  if (httpCode != 200) {
    Serial.printf("Image download failed: %d\n", httpCode);
    http.end();
    return false;
  }
  
  // Get image size
  int len = http.getSize();
  Serial.printf("Image size: %d bytes\n", len);
  
  if (len <= 0 || len > 30000) {  // Sanity check
    Serial.println("Invalid image size");
    http.end();
    return false;
  }
  
  // Allocate memory for buffer
  uint8_t* buf = (uint8_t*)malloc(len);
  if (!buf) {
    Serial.println("Memory allocation failed");
    http.end();
    return false;
  }
  
  WiFiClient* stream = http.getStreamPtr();
  int bytesRead = 0;
  
  // Read all bytes properly
  while (http.connected() && bytesRead < len) {
    size_t available = stream->available();
    if (available) {
      int c = stream->readBytes(buf + bytesRead, min((int)available, len - bytesRead));
      bytesRead += c;
    } else {
      delay(1);
    }
  }
  
  Serial.printf("Read %d bytes\n", bytesRead);
  
  // Draw the JPEG
  uint16_t w, h;
  TJpgDec.getJpgSize(&w, &h, buf, bytesRead);
  Serial.printf("JPEG dimensions: %dx%d\n", w, h);
  
  int result = TJpgDec.drawJpg(x, y, buf, bytesRead);
  
  free(buf);
  http.end();
  
  if (result != 0) {
    Serial.printf("JPEG decode failed: %d\n", result);
    return false;
  }
  
  return true;
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_url);
    int code = http.GET();
    
    if (code == 200) {
      DynamicJsonDocument doc(8192);
      DeserializationError error = deserializeJson(doc, http.getString());
      
      if (error) {
        Serial.print("JSON parse failed: ");
        Serial.println(error.c_str());
        http.end();
        delay(30000);
        return;
      }
      
      tft.fillScreen(TFT_BLACK);
      tft.setTextSize(1);
      int y = 5;
      
      for (JsonObject item : doc.as<JsonArray>()) {
        //const char* img_url = item["image_url"];
        char img_url[256];
        strncpy(img_url, item["image_url"], sizeof(img_url));
        img_url[sizeof(img_url) - 1] = '\0';

        // Remove WebP tag
        replace_substring(img_url, "_AC_SY300_SX300_QL70_FMwebp_", "_AC_SY50_QL70_FMjpg_");

        // Draw image
        if (img_url) {
          Serial.printf("Downloading: %s\n", img_url);
          bool success = downloadAndDrawJpg(img_url, 5, y);
          if (!success) {
            Serial.println("Failed to display image");
          }
        }
        
        // Print title
        tft.setCursor(70, y + 5);
        tft.setTextColor(item["drop"].as<float>() > 0 ? TFT_GREEN : TFT_WHITE, TFT_BLACK);
        tft.printf("%.65s", item["title"].as<const char*>());
        
        // Print currnet and previous prices
        tft.setCursor(70, y + 20);
        tft.printf("$%.2f", item["current_price"].as<float>());
        if (!item["previous_price"].isNull()) {
          tft.printf(" was $%.2f", item["previous_price"].as<float>());
        }
        
        // Print all-time low
        tft.setCursor(70, y + 35);
        tft.printf("All-time low:$%.2f", item["lowest_price"].as<float>());

        tft.drawLine(0, y + 55, 480, y + 55, TFT_DARKGREY);
        
        y += 60;
        if (y > 220) break;
      }
    } else {
      Serial.printf("HTTP GET failed: %d\n", code);
    }
    http.end();
  }
  
  delay(30000);
}