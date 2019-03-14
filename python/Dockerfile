FROM python:3.6.8-alpine3.9

RUN apk --no-cache add bash linux-headers g++ librdkafka librdkafka-dev 
ADD requirements.txt /requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8089 5557 5558

ENTRYPOINT ["/usr/local/bin/locust"]