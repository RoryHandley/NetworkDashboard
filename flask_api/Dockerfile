FROM python:3.11-slim

WORKDIR /app

COPY flask_api/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY flask_api/ .

EXPOSE 8000

CMD ["python3", "app.py"]
