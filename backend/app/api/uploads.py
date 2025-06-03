import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import traceback
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models.upload import Upload as UploadModel
from app.models.chapter import Chapter as ChapterModel
from app.models.user import User
from app.schemas import UploadSchema, UploadCreateSchema, ChapterSchema
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

class UploadResponseSchema(BaseModel):
    upload: UploadSchema
    chapters: List[ChapterSchema]

@router.post("/", response_model=UploadResponseSchema)
async def create_upload(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF file and process it immediately"""
    print(f"\n=== Upload Request Started ===")
    print(f"User ID: {current_user.id}")
    print(f"File: {file.filename}")
    
    logger.info(f"Upload request received from user {current_user.id} for file: {file.filename}")
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        print("Error: Not a PDF file")
        logger.warning(f"Invalid file type attempted: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size (50MB limit)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    file_size = 0
    try:
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of 50MB"
            )
    except Exception as e:
        logger.error(f"Error checking file size: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error validating file size"
        )
    
    file_path = None
    try:
        # Prepare file path with sanitized filename
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (' ', '-', '_', '.'))
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
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
        
        upload = UploadModel(
            filename=safe_filename,
            title=title or safe_filename.replace('.pdf', ''),
            description=description,
            user_id=current_user.id,
            status="processing",  # Start processing immediately
            file_path=file_path
        )
        
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        print(f"Upload record created with ID: {upload.id}")
        logger.info(f"Upload record created successfully with ID: {upload.id}")
        
        # Process the PDF immediately
        try:
            logger.info(f"Starting PDF processing for upload {upload.id}")
            await process_pdf(file_path, upload.id, db)
            
            # Update status to completed
            upload.status = "completed"
            db.commit()
            
            # Get the processed chapters
            logger.info(f"Fetching chapters for upload {upload.id}")
            chapters = db.query(ChapterModel).filter(ChapterModel.upload_id == upload.id).all()
            logger.info(f"Found {len(chapters)} chapters for upload {upload.id}")
            
            # Log chapter details for debugging
            for chapter in chapters:
                logger.info(f"Chapter details - ID: {chapter.id}, Chapter No: {chapter.chapter_no}, Title: {chapter.title}")
            
            response = UploadResponseSchema(upload=upload, chapters=chapters)
            logger.info("Successfully created UploadResponse")
            return response
            
        except Exception as process_error:
            logger.error(f"Error processing PDF: {str(process_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            upload.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing PDF: {str(process_error)}"
            )
        
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
        uploads = db.query(UploadModel).filter(UploadModel.user_id == current_user.id).all()
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
        upload = db.query(UploadModel).filter(
            UploadModel.id == upload_id,
            UploadModel.user_id == current_user.id
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

@router.post("/{upload_id}/process", response_model=UploadSchema)
async def process_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process a pending upload to extract chapters and generate questions"""
    logger.info(f"Processing upload {upload_id} for user {current_user.id}")
    
    # Get the upload
    upload = db.query(UploadModel).filter(
        UploadModel.id == upload_id,
        UploadModel.user_id == current_user.id
    ).first()
    
    if not upload:
        logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    if upload.status != "pending":
        logger.warning(f"Upload {upload_id} is not in pending state. Current status: {upload.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload is not in pending state. Current status: {upload.status}"
        )
    
    try:
        # Update status to processing
        upload.status = "processing"
        db.commit()
        
        # Process the PDF
        logger.info(f"Starting PDF processing for upload {upload_id}")
        await process_pdf(upload.file_path, upload.id, db)
        
        # Update status to completed
        upload.status = "completed"
        db.commit()
        
        logger.info(f"Successfully processed upload {upload_id}")
        return upload
        
    except Exception as e:
        logger.error(f"Error processing upload {upload_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Update status to failed
        upload.status = "failed"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )

@router.get("/{upload_id}/chapters", response_model=List[ChapterSchema])
def get_upload_chapters(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chapters for a specific upload"""
    logger.info(f"Fetching chapters for upload {upload_id}")
    
    # Get the upload
    upload = db.query(UploadModel).filter(
        UploadModel.id == upload_id,
        UploadModel.user_id == current_user.id
    ).first()
    
    if not upload:
        logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    # Get chapters
    chapters = db.query(ChapterModel).filter(ChapterModel.upload_id == upload_id).all()
    logger.info(f"Found {len(chapters)} chapters for upload {upload_id}")
    
    return chapters

@router.get("/{upload_id}/chapters/summary", response_model=List[ChapterSchema])
def get_chapter_summaries(
    upload_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chapter summaries for a specific upload with pagination"""
    logger.info(f"Fetching chapter summaries for upload {upload_id} with pagination: skip={skip}, limit={limit}")
    logger.info(f"User ID: {current_user.id}")
    
    try:
        # Get the upload and verify ownership
        upload = db.query(UploadModel).filter(
            UploadModel.id == upload_id,
            UploadModel.user_id == current_user.id
        ).first()
        
        if not upload:
            logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        logger.info(f"Found upload: id={upload.id}, filename={upload.filename}, status={upload.status}")
        
        # Get chapters with pagination
        chapters = db.query(ChapterModel)\
            .filter(ChapterModel.upload_id == upload_id)\
            .order_by(ChapterModel.chapter_no)\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        logger.info(f"Found {len(chapters)} chapters for upload {upload_id}")
        for chapter in chapters:
            logger.info(f"Chapter details - ID: {chapter.id}, Chapter No: {chapter.chapter_no}, Title: {chapter.title}")
        
        return chapters
        
    except Exception as e:
        logger.error(f"Error fetching chapter summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching chapter summaries: {str(e)}"
        )

@router.get("/{upload_id}/pdf")
async def get_pdf(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the PDF file for a specific upload"""
    logger.info(f"Fetching PDF for upload {upload_id} for user {current_user.id}")
    
    try:
        # Get the upload and verify ownership
        upload = db.query(UploadModel).filter(
            UploadModel.id == upload_id,
            UploadModel.user_id == current_user.id
        ).first()
        
        if not upload:
            logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        logger.info(f"Found upload: id={upload.id}, filename={upload.filename}, file_path={upload.file_path}")
        
        if not upload.file_path:
            logger.error(f"No file path found for upload {upload_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file path not found"
            )
        
        if not os.path.exists(upload.file_path):
            logger.error(f"PDF file not found at path: {upload.file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF file not found at path: {upload.file_path}"
            )
        
        # Check file permissions
        if not os.access(upload.file_path, os.R_OK):
            logger.error(f"No read permission for file: {upload.file_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to read PDF file"
            )
        
        logger.info(f"Serving PDF file: {upload.file_path}")
        return FileResponse(
            upload.file_path,
            media_type="application/pdf",
            filename=upload.filename,
            headers={
                "Content-Disposition": f"inline; filename={upload.filename}",
                "Cache-Control": "no-cache",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving PDF for upload {upload_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving PDF file: {str(e)}"
        ) 