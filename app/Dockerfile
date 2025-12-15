# app/Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install flask mysql-connector-python
COPY app.py .
CMD ["python", "app.py"]