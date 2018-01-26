FROM python:2.7
ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

ADD . /app



