FROM python:3.8.1

COPY kafka-producer /kafka-producer
WORKDIR /kafka-producer

RUN pip install --upgrade pip && pip install pipenv==2018.11.26
RUN pipenv install --system --deploy --ignore-pipfile

EXPOSE 7778

ENTRYPOINT [ "gunicorn", "-c", "config/gunicorn.conf.py", "--preload", "app:app" ]
