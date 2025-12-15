# scraper/scraper_job.py
import asyncio
import os
import mysql.connector
from scraper import scrape

async def main():
    url = os.getenv('SCRAPE_URL')
    
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user='root',
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB')
    )
    
    data = await scrape(url)
    
    cur = conn.cursor()
    cur.execute("SELECT current_price FROM prices WHERE url = %s", (url,))
    result = cur.fetchone()
    
    if result:
        prev_price = result[0]
        sql = """
        UPDATE prices 
        SET title=%s, image_url=%s, previous_price=%s, current_price=%s,
            lowest_price=LEAST(COALESCE(lowest_price, %s), %s)
        WHERE url=%s
        """
        cur.execute(sql, (data['title'], data['image'], prev_price, data['price'], 
                         data['price'], data['price'], url))
    else:
        sql = """INSERT INTO prices(url, title, image_url, current_price, previous_price, lowest_price)
                 VALUES(%s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (url, data['title'], data['image'], data['price'], None, data['price']))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Updated price for {url}: ${data['price']}")

if __name__ == "__main__":
    asyncio.run(main())