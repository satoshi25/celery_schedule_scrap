FROM python:3.8

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["celery", "-A", "src.service.celery_worker", "worker", "--loglevel=info", "-E", "--logfile=./logfile.log"]