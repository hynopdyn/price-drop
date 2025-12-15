# price-drop
Get price drop alerts on your WT32-SC01 desktop display on products you're watching.

## Web app
To install web app, `docker build -t price-drop-app:latest app` and `docker-compose up -d`.

To add URLs to track:
```
curl -X POST http://localhost:5000/track \
-H "Content-Type: application/json" \
-H "Authorization: Bearer secret123" \
-d '{"url":"<YOUR_URL_HERE>"}'
```
making sure that URLs are formatted like: `https://www.amazon.com/gp/aw/d/XXXXXXXXXX/`

Other endpoints:
```
/       # For testing
/dash   # For website
/prices # For WT32-SC01
/remove # Specify URL or "all" will delete URLs
```

## Scraper
Then, to use scraper: `docker build -t price-scraper:latest scraper`,
`minikube image load price-scraper:latest`,
and run `scraper_orchestrator.py`.

## Desktop display
Finally, on Arduino IDE, install TFT_eSPI, ArduinoJSON, TJpg_Decoder libraries, and load /display.c onto WT32-SC01 using Arduino IDE.

## WIP functionality
To have the scraper run every 6 hours, `kubectl create job --from=cronjob/price-scraper scraper-1`. (Need to fix kubernetes/scraper-cronjob.yaml)
`kubectl apply -f kubernetes/scraper-cronjob.yaml`