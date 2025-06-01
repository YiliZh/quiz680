from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, uploads, chapters, questions, history, ws

app = FastAPI(title="Quiz System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
app.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"]) 