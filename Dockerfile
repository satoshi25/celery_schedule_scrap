FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir -p /app/logs && chmod a+w /app/logs

COPY . .

CMD ["celery", "-A", "src.service.celery_worker", "worker", -B "--loglevel=info", "--logfile=./logs/logfile.log"]