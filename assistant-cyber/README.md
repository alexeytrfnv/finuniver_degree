# assistant-pd-template
Шаблонный сервис ai помощника

## Переменные окружения
в .env.example пример данных, которые нужно заполнить

### Токен поискового сервиса
``` 
TOKEN=SECRET
```

``` 
SEARCH_SERVICE_URL=http://backend:8000 # путь к поисковому сервису
BASE_COLLECTION_NAME=inspection_collection # основная коллекция
```

### Доступ к llm
``` 
BASE_MODEL_URL=http://s00-0000-ai08.sogaz.ru/ai24-llm-gpu
BASE_MODEL_NAME=sogaz_ai

RESERVE_MODEL_URL=http://s00-0000-ai08.sogaz.ru/2-gpu-llm-worker-oss
RESERVE_MODEL_NAME=gpt-oss-F16:20b
```

### Доступ к базе
``` 
DB_NAME=test
DB_USER=test
DB_PASS=test
DB_HOST=postgres
DB_PORT=5432
```

## Деплой
```
docker compose -f compose/docker-compose.yml --env-file .env up --build -d
```