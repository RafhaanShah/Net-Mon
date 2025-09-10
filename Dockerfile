FROM python:3-alpine

LABEL org.opencontainers.image.source="https://github.com/RafhaanShah/Net-Mon"

# https://pkgs.alpinelinux.org/package/edge/main/x86_64/nmap
ENV NMAP_VERSION="7.97-r0"

RUN apk update && apk add \
    nmap=${NMAP_VERSION} \
    && rm -rf /var/cache/apk/*

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# needs to run as root for nmap to get mac addresses
ENTRYPOINT ["python", "app.py"]
