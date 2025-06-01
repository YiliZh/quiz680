## How to start it
```
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
```

## Run PostgreSQL:
```
    docker-compose -f docker-compose.windows.yml up -d
```

## Run migrations (once Alembic is set up):
```
alembic init migrations
   alembic upgrade head
```
