import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, uploads, chapters, questions, history, ws, exam_history

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quiz System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Log startup
logger.info("Starting Quiz System API")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(exam_history.router, prefix="/api/exam-history", tags=["exam-history"])
app.include_router(ws.router, prefix="/api/ws", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete") 