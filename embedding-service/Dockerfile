
FROM nexus.sogaz.ru/python:3.13.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD requirements.txt /app

RUN pip install --upgrade pip --trusted-host nexus.sogaz.ru --index-url http://nexus.sogaz.ru/repository/pypi-group/simple
RUN pip install -r requirements.txt --trusted-host nexus.sogaz.ru --index-url http://nexus.sogaz.ru/repository/pypi-group/simple
# исправить перенос всего репозитория

COPY . /app 

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]