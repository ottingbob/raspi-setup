FROM python:3.9.5-slim-buster

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

CMD FLASK_ENV=development flask run --host=0.0.0.0 --port=5000
