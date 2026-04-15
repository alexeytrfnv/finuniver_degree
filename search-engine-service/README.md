# search-engine-service

Сервис для поиска информации в документах, необходим для работы ии помощников


## Переменные окружения
в .env.example пример данных, которые нужно заполнить

### токен сервиса
```
TOKEN=SECRET
```
 Нужно сгенерировать токен, для доступа к ручкам сервиса
```
openssl rand -hex 32
```

### qdrant
```
QDRANT_API_KEY=SECRET
QDRANT_BASE_URL=http://qdrant:6333
```
доступ к qdrant должен быть с токеном

### redis
```
REDIS_URL=redis://redis:6379
```
доступ к redis

### embeding service (Сервис для работы с текстом)
```
EMBEDDING_SERVICE=http://s00-0000-ai08.sogaz.ru/ai29-embedding-service
EMBEDDING_SERVICE_TOKEN=SECRET
```

### настройка llm

```
PRIORITY_LLM_INTERFACE=ollama # ollama or openai

OPENAI_LLM_BASE_URL=http://s00-0000-ai08.sogaz.ru/h100-vllm/v1
OPENAI_LLM_MODEL_NAME=t-tech-lora-ui-kit

OLLAMA_LLM_BASE_URL=http://s00-0000-ai08.sogaz.ru/2-gpu-llm-worker-oss
OLLAMA_LLM_MODEL_NAME=gpt-oss-F16:20b
```

## Деплой compose

```
docker compose -f compose/compose.yml --env-file .env up --build -d
```