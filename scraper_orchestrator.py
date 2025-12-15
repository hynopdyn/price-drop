import mysql.connector
import os
import subprocess
import yaml

MYSQL_HOST = os.getenv('CLOUD_MYSQL_HOST', '192.168.1.18')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DB = os.getenv('MYSQL_DB', 'pricedb')

def create_scraper_job(url, job_id):
    job_yaml = {
        'apiVersion': 'batch/v1',
        'kind': 'Job',
        'metadata': {'name': f'scraper-{job_id}'},
        'spec': {
            'template': {
                'spec': {
                    'containers': [{
                        'name': 'scraper',
                        'image': 'price-scraper:latest',
                        'imagePullPolicy': 'Never',
                        'env': [
                            {'name': 'SCRAPE_URL', 'value': url},
                            {'name': 'MYSQL_HOST', 'value': MYSQL_HOST},
                            {'name': 'MYSQL_PASSWORD', 'value': MYSQL_PASSWORD},
                            {'name': 'MYSQL_DB', 'value': MYSQL_DB}
                        ]
                    }],
                    'restartPolicy': 'OnFailure'
                }
            }
        }
    }
    
    with open(f'/tmp/scraper-{job_id}.yaml', 'w') as f:
        yaml.dump(job_yaml, f)
    
    subprocess.run(['kubectl', 'apply', '-f', f'/tmp/scraper-{job_id}.yaml'])
    print(f"Created scraper job {job_id} for {url}")

def main():
    conn = mysql.connector.connect(host=MYSQL_HOST, user='root', password=MYSQL_PASSWORD, database=MYSQL_DB)
    cur = conn.cursor()
    cur.execute("SELECT id, url FROM prices")
    urls = cur.fetchall()
    cur.close()
    conn.close()
    
    for job_id, url in urls:
        create_scraper_job(url, job_id)

if __name__ == "__main__":
    main()