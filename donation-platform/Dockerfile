FROM python:3.8.1
LABEL version="0.0.1"

COPY donation-platform /donation-platform
WORKDIR /donation-platform

RUN pip install --upgrade pip && pip install pipenv==2018.11.26
RUN pipenv install --system --deploy --ignore-pipfile

EXPOSE 7777

ENTRYPOINT [ "gunicorn", "-c", "config/gunicorn.conf.py", "app:app" ]
