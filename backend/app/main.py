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

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(ws.router, prefix="/api/ws", tags=["websocket"]) 