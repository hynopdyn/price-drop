# scraper/Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install beautifulsoup4 curl-cffi mysql-connector-python
COPY scraper.py .
COPY scraper_job.py .
CMD ["python", "scraper_job.py"]