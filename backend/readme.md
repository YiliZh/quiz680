## How to start it
```
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload

   python -m uvicorn app.main:app --reload --log-level debug

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

## Dump database
```
   pg_dump -U postgres -h localhost -p 5432 -d quiz2 --schema-only -f C:\cims\code\yl\quiz680\docs\quiz2_0603.sql
   123456
```