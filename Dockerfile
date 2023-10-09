FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN mkdir -p /app/logs

CMD ["python", "main.py"]
