import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import traceback

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models import User, Upload
from app.schemas import Upload as UploadSchema, UploadCreate
from app.services.pdf import process_pdf

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Create upload directory if it doesn't exist
try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory created/verified at: {settings.UPLOAD_DIR}")
    
    # Check directory permissions
    if not os.access(settings.UPLOAD_DIR, os.W_OK):
        logger.error(f"No write permission for directory: {settings.UPLOAD_DIR}")
        raise PermissionError(f"No write permission for directory: {settings.UPLOAD_DIR}")
    logger.info(f"Upload directory permissions verified")
except Exception as e:
    logger.error(f"Failed to setup upload directory: {str(e)}")
    raise

@router.post("/", response_model=UploadSchema)
async def create_upload(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF file"""
    print(f"\n=== Upload Request Started ===")
    print(f"User ID: {current_user.id}")
    print(f"File: {file.filename}")
    
    logger.info(f"Upload request received from user {current_user.id} for file: {file.filename}")
    
    if not file.filename.lower().endswith('.pdf'):
        print("Error: Not a PDF file")
        logger.warning(f"Invalid file type attempted: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    file_path = None
    try:
        # Prepare file path
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        logger.info(f"Prepared file path: {file_path}")
        
        # Save the file first
        print(f"\nSaving file to: {file_path}")
        logger.info(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("File saved successfully")
        logger.info(f"File saved successfully at: {file_path}")
        
        # Create upload record
        print("\nCreating upload record...")
        logger.info(f"Creating upload record in database for file: {file.filename}")
        
        upload = Upload(
            filename=file.filename,
            title= file.filename.replace('.pdf', ''),
            description=description,
            user_id=current_user.id,
            status="pending",  # Changed from "processing" to "pending"
            file_path=file_path
        )
        
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        print(f"Upload record created with ID: {upload.id}")
        logger.info(f"Upload record created successfully with ID: {upload.id}")
        
        return upload
        
    except Exception as e:
        print(f"\nError in upload process: {str(e)}")
        logger.error(f"Error in upload process: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Clean up the file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up file: {file_path}")
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as cleanup_error:
                print(f"Error cleaning up file: {str(cleanup_error)}")
                logger.error(f"Error cleaning up file: {str(cleanup_error)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in upload process: {str(e)}"
        )

@router.get("/", response_model=List[UploadSchema])
def get_uploads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all uploads for current user"""
    logger.info(f"Fetching uploads for user {current_user.id}")
    try:
        uploads = db.query(Upload).filter(Upload.user_id == current_user.id).all()
        logger.info(f"Found {len(uploads)} uploads for user {current_user.id}")
        return uploads
    except Exception as e:
        logger.error(f"Error fetching uploads: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching uploads"
        )

@router.get("/{upload_id}", response_model=UploadSchema)
def get_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific upload"""
    logger.info(f"Fetching upload {upload_id} for user {current_user.id}")
    try:
        upload = db.query(Upload).filter(
            Upload.id == upload_id,
            Upload.user_id == current_user.id
        ).first()
        if not upload:
            logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        logger.info(f"Successfully retrieved upload {upload_id}")
        return upload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upload {upload_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching upload"
        ) 