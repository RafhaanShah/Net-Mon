FROM python:3.9-alpine

LABEL org.opencontainers.image.source https://github.com/RafhaanShah/Net-Mon

RUN apk update && apk add \
    nmap=7.80-r2 \
    && rm -rf /var/cache/apk/*

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# needs to run as root for nmap to get mac addresses
ENTRYPOINT ["python", "app.py"]
