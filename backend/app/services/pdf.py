import logging
import asyncio
from typing import List, Dict
import PyPDF2
from sqlalchemy.orm import Session
from app.models import Chapter, Upload
from app.services.quiz import generate_questions
from app.core.config import settings
import os

logger = logging.getLogger(__name__)

async def process_pdf(file_path: str, upload_id: int, db: Session):
    """Process PDF file and extract chapters"""
    try:
        logger.info(f"Starting PDF processing for file: {file_path}")
        
        # Verify file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Extract text from PDF
        chapters = extract_chapters(file_path)
        logger.info(f"Extracted {len(chapters)} chapters from PDF")
        
        # Save chapters to database
        for chapter in chapters:
            db_chapter = Chapter(
                title=chapter["title"],
                content=chapter["content"],
                page_number=chapter["page_number"],
                upload_id=upload_id,
                keywords=chapter.get("keywords", [])
            )
            db.add(db_chapter)
        
        db.commit()
        
        # Generate questions for each chapter
        for chapter in db.query(Chapter).filter(Chapter.upload_id == upload_id).all():
            await generate_questions(chapter.id, db)
        
        # Update upload status
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if upload:
            upload.status = "completed"
            upload.chapters = chapters
            db.commit()
            logger.info(f"Successfully processed PDF and updated upload record {upload_id}")
            
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        # Update upload status to failed
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if upload:
            upload.status = "failed"
            db.commit()
        raise

def extract_chapters(file_path: str) -> List[dict]:
    """Extract chapters from PDF file"""
    try:
        logger.info(f"Extracting chapters from: {file_path}")
        chapters = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {total_pages} pages")
            
            for page_num in range(total_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        chapters.append({
                            "title": f"Chapter {page_num + 1}",
                            "content": text,
                            "page_number": page_num + 1,
                            "keywords": extract_keywords(text)
                        })
                        logger.debug(f"Processed page {page_num + 1}")
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    continue
        
        logger.info(f"Successfully extracted {len(chapters)} chapters")
        return chapters
        
    except Exception as e:
        logger.error(f"Error extracting chapters: {str(e)}", exc_info=True)
        raise

def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text"""
    try:
        # Simple keyword extraction - can be improved
        words = text.lower().split()
        # Remove common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))[:10]  # Return top 10 unique keywords
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return [] 