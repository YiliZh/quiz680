# Quiz System

A system for uploading PDF learning materials, extracting chapters, generating quizzes, and tracking quiz attempts.

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 15+
- Microsoft Visual C++ Build Tools (for Windows)

## Backend Setup

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Configure PostgreSQL:
   - Make sure PostgreSQL is installed and running
   - Create a database named "quiz2":
     ```sql
     CREATE DATABASE quiz2;
     ```
   - Update database settings in `backend/app/core/config.py` if needed:
     ```python
     POSTGRES_USER = "postgres"
     POSTGRES_PASSWORD = "123456"
     POSTGRES_DB = "quiz2"
     ```

3. Run database migrations (only needed first time or after model changes):
   ```bash
   # Initialize Alembic (only needed first time)
   alembic init migrations

   # Create initial migration (only needed first time or after model changes)
   alembic revision --autogenerate -m "Initial migration"

   # Apply migrations (only needed first time or after model changes)
   alembic upgrade head
   ```

4. Run the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

The backend will be available at http://localhost:8000

## Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:3000

## Features

- PDF upload and chapter extraction
- Chapter summarization and tagging
- Quiz generation
- Quiz taking with immediate feedback
- History tracking
- User authentication

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for the interactive API documentation.

## Development

- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React, Material UI, TanStack Query
- PDF Processing: pdfplumber
- AI/ML: LangChain, KeyBERT 