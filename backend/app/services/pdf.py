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

logger = logging.getLogger(__name__)

async def process_pdf(file_path: str, upload_id: int, db: Session):
    """Process a PDF file and extract chapters"""
    print(f"\n=== PDF Processing Started ===")
    print(f"File: {file_path}")
    print(f"Upload ID: {upload_id}")
    
    logger.info(f"Starting PDF processing for file: {file_path}, upload_id: {upload_id}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Open and read the PDF
        print("\nOpening PDF file...")
        logger.info("Opening PDF file")
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                print(f"PDF opened successfully. Total pages: {num_pages}")
                logger.info(f"PDF opened successfully. Total pages: {num_pages}")
                
                if num_pages == 0:
                    print("Error: PDF file is empty")
                    logger.error("PDF file is empty")
                    raise ValueError("PDF file is empty")
                
                # Extract text from each page
                chapters = []
                current_chapter = []
                chapter_number = 1
                all_text = []  # Store all text for fallback
                
                for page_num in range(num_pages):
                    print(f"\nProcessing page {page_num + 1}/{num_pages}")
                    logger.info(f"Processing page {page_num + 1}/{num_pages}")
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text:
                            print(f"Warning: No text extracted from page {page_num + 1}")
                            logger.warning(f"No text extracted from page {page_num + 1}")
                            continue
                        
                        all_text.append(text)  # Add to all text
                        
                        # Simple chapter detection (you might want to improve this)
                        if "Chapter" in text or "CHAPTER" in text:
                            if current_chapter:
                                # Save previous chapter
                                chapter_text = "\n".join(current_chapter)
                                if chapter_text.strip():  # Only create chapter if there's content
                                    print(f"Creating chapter {chapter_number} with {len(chapter_text)} characters")
                                    logger.info(f"Creating chapter {chapter_number} with {len(chapter_text)} characters")
                                    chapter = Chapter(
                                        upload_id=upload_id,
                                        chapter_no=chapter_number,
                                        title=f"Chapter {chapter_number}",
                                        summary=chapter_text[:500] if chapter_text else "No summary available"
                                    )
                                    chapters.append(chapter)
                                    chapter_number += 1
                                current_chapter = []
                        
                        current_chapter.append(text)
                    except Exception as page_error:
                        print(f"Error processing page {page_num + 1}: {str(page_error)}")
                        logger.error(f"Error processing page {page_num + 1}: {str(page_error)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        continue
                
                # Save the last chapter
                if current_chapter:
                    chapter_text = "\n".join(current_chapter)
                    if chapter_text.strip():  # Only create chapter if there's content
                        print(f"Creating final chapter {chapter_number} with {len(chapter_text)} characters")
                        logger.info(f"Creating final chapter {chapter_number} with {len(chapter_text)} characters")
                        chapter = Chapter(
                            upload_id=upload_id,
                            chapter_no=chapter_number,
                            title=f"Chapter {chapter_number}",
                            summary=chapter_text[:500] if chapter_text else "No summary available"
                        )
                        chapters.append(chapter)
                
                if not chapters:
                    print("Warning: No chapters were extracted from the PDF")
                    logger.warning("No chapters were extracted from the PDF")
                    # Create a single chapter with all content
                    all_text_combined = "\n".join(all_text)
                    if all_text_combined.strip():  # Only create chapter if there's content
                        chapter = Chapter(
                            upload_id=upload_id,
                            chapter_no=1,
                            title="Document",
                            summary=all_text_combined[:500] if all_text_combined else "No summary available"
                        )
                        chapters.append(chapter)
                    else:
                        raise ValueError("No text content could be extracted from the PDF")
                
                # Save all chapters to database
                print(f"\nSaving {len(chapters)} chapters to database")
                logger.info(f"Saving {len(chapters)} chapters to database")
                try:
                    for chapter in chapters:
                        db.add(chapter)
                    db.commit()
                    print("Chapters saved successfully")
                    logger.info("Chapters saved successfully")
                except Exception as db_error:
                    print(f"Error saving chapters to database: {str(db_error)}")
                    logger.error(f"Error saving chapters to database: {str(db_error)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise
                
                # Update upload status
                print("\nUpdating upload status to completed")
                logger.info("Updating upload status to completed")
                upload = db.query(Upload).filter(Upload.id == upload_id).first()
                if upload:
                    upload.status = "completed"
                    db.commit()
                    print("Upload status updated successfully")
                    logger.info("Upload status updated successfully")
                else:
                    print(f"Error: Upload {upload_id} not found when updating status")
                    logger.error(f"Upload {upload_id} not found when updating status")
                    raise Exception(f"Upload {upload_id} not found")
                
                print("\n=== PDF Processing Completed Successfully ===")
                logger.info("PDF processing completed successfully")
                return chapters
        except PyPDF2.PdfReadError as pdf_error:
            print(f"Error reading PDF file: {str(pdf_error)}")
            logger.error(f"Error reading PDF file: {str(pdf_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Invalid PDF file: {str(pdf_error)}")
            
    except Exception as e:
        print(f"\nError processing PDF: {str(e)}")
        logger.error(f"Error processing PDF: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Update upload status to failed
        try:
            upload = db.query(Upload).filter(Upload.id == upload_id).first()
            if upload:
                upload.status = "failed"
                db.commit()
                print("Upload status updated to failed")
                logger.info("Upload status updated to failed")
        except Exception as status_error:
            print(f"Error updating upload status: {str(status_error)}")
            logger.error(f"Error updating upload status: {str(status_error)}")
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