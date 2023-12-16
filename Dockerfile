FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install pip-tools
COPY requirements.txt /app/

RUN pip3 install -r requirements.txt 

COPY ./django_blog /app/

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]