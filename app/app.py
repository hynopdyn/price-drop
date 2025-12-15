from flask import Flask, request, jsonify
import mysql.connector
import os
import time
import hashlib

app = Flask(__name__)

config = {
    'user': 'root',
    'password': os.getenv('db_root_password', 'root'),
    'host': os.getenv('MYSQL_SERVICE_HOST', 'db'),
    'port': int(os.getenv('MYSQL_SERVICE_PORT', '3306')),
    'database': os.getenv('db_name', 'pricedb')
}

OAUTH_SECRET = os.getenv('OAUTH_SECRET', 'secret123')

def check_auth():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return hashlib.sha256(token.encode()).hexdigest() == hashlib.sha256(OAUTH_SECRET.encode()).hexdigest()

@app.route("/")
def index():
    return "Flask app is active!"

@app.route('/dash')
def dashboard():
    # if not check_auth():
    #     return {'error': 'Unauthorized'}, 401
    start = time.time()
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    sql = """
        SELECT title, image_url, current_price, previous_price, url
        FROM prices
        ORDER BY id ASC
    """
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    print(f"/dash endpoint called - returned {len(data)} products in {time.time() - start:.2f}s")
    return {'data': data, 'latency': time.time() - start}

@app.route('/prices')
def get_prices():
    start = time.time()
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    sql = """
        SELECT title, image_url, current_price, previous_price,
            CASE
                WHEN previous_price IS NOT NULL THEN previous_price - current_price
                ELSE 0
            END AS `drop`
        FROM prices
        ORDER BY `drop` DESC, id ASC
    """
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    print(f"/prices endpoint called - returned {len(data)} products in {time.time() - start:.2f}s")
    return jsonify([{
        'title': row[0],
        'image_url': row[1],
        'current_price': float(row[2]) if row[2] else 0,
        'previous_price': float(row[3]) if row[3] else 0,
        'drop': float(row[4]) if row[4] else 0
    } for row in data])

@app.route('/track', methods=['POST'])
def add_url():
    if not check_auth():
        return {'error': 'Unauthorized'}, 401
    start = time.time()
    url = request.json['url']
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    sql = "INSERT INTO prices(url, title, image_url, current_price, previous_price) VALUES(%s, %s, %s, %s, %s)"
    data = (url, "", "", 0.0, 0.0)
    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"New product tracked: {url}")
    return {'url': url, 'latency': time.time() - start}

if __name__ == '__main__':
    print("Flask app started on port 5000\n")
    app.run(host='0.0.0.0', port=5000)

@app.route('/remove', methods=['POST'])
def rm_url():
    if not check_auth():
        return {'error': 'Unauthorized'}, 401
    start = time.time()
    url = request.json['url']
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()

    if url == "all":
        cur.execute("DELETE FROM prices")
    else:
        cur.execute("DELETE FROM prices WHERE url = %s", (url,))
    conn.commit()
    cur.close()
    conn.close()

    print(f"Product removed: {url}")
    return {"url": url, 'latency': time.time() - start}