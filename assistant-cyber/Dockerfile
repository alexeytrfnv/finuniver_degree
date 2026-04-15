FROM nexus.sogaz.ru/python:3.13.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY /certs /usr/local/share/ca-certificates
RUN update-ca-certificates

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip --trusted-host nexus.sogaz.ru --index-url http://nexus.sogaz.ru/repository/pypi-group/simple
RUN pip install -r requirements.txt --trusted-host nexus.sogaz.ru --index-url http://nexus.sogaz.ru/repository/pypi-group/simple

COPY . .

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]