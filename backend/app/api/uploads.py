import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models import Upload
from app.schemas import Upload as UploadSchema

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=UploadSchema)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    db_upload = Upload(filename=file.filename, stored_path=file_path, user_id=1)  # Hardcoded user_id for now
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    return db_upload

@router.get("/", response_model=List[UploadSchema])
def get_uploads(db: Session = Depends(get_db)):
    uploads = db.query(Upload).all()
    return uploads 