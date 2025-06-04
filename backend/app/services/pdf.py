import logging
import asyncio
from typing import List, Dict
import PyPDF2
from sqlalchemy.orm import Session
from app.models import Chapter, Upload
from app.services.quiz import generate_questions
from app.core.config import settings
import os
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_summary(text: str, max_length: int = 500) -> str:
    """Extract a summary from the text by taking the first paragraph"""
    # Split into paragraphs and get the first non-empty one
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        return text[:max_length] if text else "No summary available"
    
    # Get the first paragraph
    summary = paragraphs[0]
    
    # If it's too long, truncate it
    if len(summary) > max_length:
        # Try to find a good breaking point
        break_point = summary.rfind('.', 0, max_length)
        if break_point > 0:
            summary = summary[:break_point + 1]
        else:
            summary = summary[:max_length] + '...'
    
    return summary

async def process_pdf(file_path: str, upload_id: int, db: Session):
    """Process a PDF file and extract chapters"""
    print(f"\n=== PDF Processing Started ===")
    print(f"File: {file_path}")
    print(f"Upload ID: {upload_id}")
    
    logger.info(f"Starting PDF processing for file: {file_path}, upload_id: {upload_id}")
    
    # Get the upload record
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise Exception(f"Upload {upload_id} not found")
    
    # Initialize logs
    logs = []
    def add_log(message: str):
        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        logs.append(log_message)
        print(log_message)
        logger.info(message)
        # Update logs in database
        upload.processing_logs = "\n".join(logs)
        db.commit()
    
    if not os.path.exists(file_path):
        add_log(f"Error: File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Open and read the PDF
        add_log("Opening PDF file...")
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                add_log(f"PDF opened successfully. Total pages: {num_pages}")
                
                if num_pages == 0:
                    add_log("Error: PDF file is empty")
                    raise ValueError("PDF file is empty")
                
                # Extract text from each page
                chapters = []
                current_chapter = []
                chapter_number = 1
                all_text = []
                
                for page_num in range(num_pages):
                    add_log(f"Processing page {page_num + 1}/{num_pages}")
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text:
                            add_log(f"Warning: No text extracted from page {page_num + 1}")
                            continue
                        
                        all_text.append(text)  # Add to all text
                        
                        # Simple chapter detection (you might want to improve this)
                        if "Chapter" in text or "CHAPTER" in text:
                            if current_chapter:
                                # Save previous chapter
                                chapter_text = "\n".join(current_chapter)
                                if chapter_text.strip():  # Only create chapter if there's content
                                    add_log(f"Creating chapter {chapter_number} with {len(chapter_text)} characters")
                                    
                                    # Create chapter using SQLAlchemy ORM
                                    chapter = Chapter(
                                        upload_id=upload_id,
                                        chapter_no=chapter_number,
                                        title=f"Chapter {chapter_number}",
                                        content=chapter_text,
                                        summary=extract_summary(chapter_text),
                                        keywords=",".join(extract_keywords(chapter_text))
                                    )
                                    chapters.append(chapter)
                                    chapter_number += 1
                                current_chapter = []
                        
                        current_chapter.append(text)
                    except Exception as page_error:
                        add_log(f"Error processing page {page_num + 1}: {str(page_error)}")
                        continue
                
                # Save the last chapter
                if current_chapter:
                    chapter_text = "\n".join(current_chapter)
                    if chapter_text.strip():  # Only create chapter if there's content
                        add_log(f"Creating final chapter {chapter_number} with {len(chapter_text)} characters")
                        
                        chapter = Chapter(
                            upload_id=upload_id,
                            chapter_no=chapter_number,
                            title=f"Chapter {chapter_number}",
                            content=chapter_text,
                            summary=extract_summary(chapter_text),
                            keywords=",".join(extract_keywords(chapter_text))
                        )
                        chapters.append(chapter)
                
                if not chapters:
                    add_log("Warning: No chapters were extracted from the PDF")
                    # Create a single chapter with all content
                    all_text_combined = "\n".join(all_text)
                    if all_text_combined.strip():  # Only create chapter if there's content
                        chapter = Chapter(
                            upload_id=upload_id,
                            chapter_no=1,
                            title="Document",
                            content=all_text_combined,
                            summary=extract_summary(all_text_combined),
                            keywords=",".join(extract_keywords(all_text_combined))
                        )
                        chapters.append(chapter)
                    else:
                        raise ValueError("No text content could be extracted from the PDF")
                
                # Save all chapters to database
                add_log(f"Saving {len(chapters)} chapters to database")
                try:
                    for chapter in chapters:
                        db.add(chapter)
                    db.commit()
                    add_log("Chapters saved successfully")
                except Exception as db_error:
                    add_log(f"Error saving chapters to database: {str(db_error)}")
                    db.rollback()
                    raise
                
                # Update upload status
                add_log("Updating upload status to completed")
                upload.status = "completed"
                db.commit()
                add_log("Upload status updated successfully")
                
                add_log("=== PDF Processing Completed Successfully ===")
                return chapters
                
        except Exception as pdf_error:
            if "PDF" in str(pdf_error) or "cannot" in str(pdf_error).lower() or "not a PDF" in str(pdf_error).lower():
                add_log(f"Error reading PDF file: {str(pdf_error)}")
                raise ValueError(f"Invalid PDF file: {str(pdf_error)}")
            else:
                raise
            
    except Exception as e:
        add_log(f"Error processing PDF: {str(e)}")
        # Update upload status to failed
        try:
            upload.status = "failed"
            db.commit()
            add_log("Upload status updated to failed")
        except Exception as status_error:
            add_log(f"Error updating upload status: {str(status_error)}")
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
    """Extract keywords from text - improved version"""
    try:
        # Simple but more effective keyword extraction
        import re
        
        # Clean the text: remove extra whitespace and special characters
        cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = cleaned_text.split()
        
        # More comprehensive stop words list
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their', 'what',
            'which', 'who', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
            'now', 'here', 'there', 'then', 'also', 'about', 'after', 'before',
            'through', 'during', 'above', 'below', 'up', 'down', 'out', 'off',
            'over', 'under', 'again', 'further', 'once', 'page', 'chapter'
        }
        
        # Filter words: length > 3, not in stop words, and contains letters
        keywords = []
        word_freq = {}
        
        for word in words:
            if (len(word) > 3 and 
                word not in stop_words and 
                re.search(r'[a-zA-Z]', word) and  # Contains at least one letter
                not word.isdigit()):  # Not just numbers
                
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 15 unique keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_keywords[:15]]
        
        return keywords
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []