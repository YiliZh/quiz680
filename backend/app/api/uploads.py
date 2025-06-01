import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models import User, Upload
from app.schemas import Upload as UploadSchema, UploadCreate
from app.services.pdf import process_pdf

router = APIRouter()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=UploadSchema)
async def create_upload(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create upload record
    upload = Upload(
        filename=file.filename,
        title=title or file.filename,
        description=description,
        user_id=current_user.id,
        status="processing"
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    
    # Save file and process
    try:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process PDF in background
        await process_pdf(file_path, upload.id, db)
        
        return upload
    except Exception as e:
        upload.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[UploadSchema])
def get_uploads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all uploads for current user"""
    return db.query(Upload).filter(Upload.user_id == current_user.id).all()

@router.get("/{upload_id}", response_model=UploadSchema)
def get_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific upload"""
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload 