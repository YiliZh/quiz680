import asyncio
from typing import List
import PyPDF2
from sqlalchemy.orm import Session
from app.models import Chapter, Upload
from app.services.quiz import generate_questions

async def process_pdf(file_path: str, upload_id: int, db: Session):
    """Process PDF file and extract chapters"""
    try:
        # Extract text from PDF
        chapters = extract_chapters(file_path)
        
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
            db.commit()
            
    except Exception as e:
        # Update upload status to failed
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if upload:
            upload.status = "failed"
            db.commit()
        raise e

def extract_chapters(file_path: str) -> List[dict]:
    """Extract chapters from PDF file"""
    chapters = []
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Simple chapter detection - can be improved
            if text.strip():
                chapters.append({
                    "title": f"Chapter {page_num + 1}",
                    "content": text,
                    "page_number": page_num + 1,
                    "keywords": extract_keywords(text)
                })
    
    return chapters

def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text - placeholder for more sophisticated implementation"""
    # TODO: Implement proper keyword extraction
    return [] 