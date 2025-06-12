# import json
# import random
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import openai
# import os
# from werkzeug.utils import secure_filename
# import PyPDF2
# import docx
# from pptx import Presentation
# import logging
# import traceback
# from dotenv import load_dotenv
# from db_utils import insert_file, insert_quiz, insert_question, get_quiz_by_id, get_all_quizzes

# # Load environment variables from .env file
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('flask_app.log')
#     ]
# )
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app, supports_credentials=True)

# # Add CORS headers to all responses
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')  # Allow all origins for development
#     response.headers.add('Access-Control-Allow-Headers', '*')
#     response.headers.add('Access-Control-Allow-Methods', '*')
#     return response

# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'ppt', 'pptx'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
# logger.debug(f"OpenAI API Key loaded: {'Present' if openai.api_key else 'Missing'}")

# if not openai.api_key:
#     logger.error("OPENAI_API_KEY environment variable is not set!")

# @app.route('/')
# def hello():
#     return jsonify({"message": "Hello, World!"})

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def extract_text_from_pdf(file_path):
#     try:
#         text = ''
#         with open(file_path, 'rb') as file:
#             reader = PyPDF2.PdfReader(file)
#             for page in reader.pages:
#                 text += page.extract_text()
#         return text
#     except Exception as e:
#         logger.error(f"Error extracting text from PDF: {str(e)}")
#         raise

# def extract_text_from_ppt(file_path):
#     try:
#         text = ''
#         presentation = Presentation(file_path)
#         for slide in presentation.slides:
#             for shape in slide.shapes:
#                 if hasattr(shape, "text"):
#                     text += shape.text + '\n'
#         return text
#     except Exception as e:
#         logger.error(f"Error extracting text from PPT: {str(e)}")
#         raise

# def extract_text_from_file(file_path):
#     try:
#         _, file_extension = os.path.splitext(file_path)
#         logger.debug(f"Extracting text from file with extension: {file_extension}")
        
#         if file_extension == '.pdf':
#             return extract_text_from_pdf(file_path)
#         elif file_extension in ['.ppt', '.pptx']:
#             return extract_text_from_ppt(file_path)
#         elif file_extension == '.docx':
#             doc = docx.Document(file_path)
#             text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
#         elif file_extension == '.txt':
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 text = file.read()
#         else:
#             raise ValueError(f"Unsupported file type: {file_extension}")
        
#         return text
#     except Exception as e:
#         logger.error(f"Error in extract_text_from_file: {str(e)}")
#         raise

# @app.route('/api/generate_questions', methods=['POST'])
# def generate_questions():
    
#     try:
#         logger.debug("Received request to generate questions")
#         logger.debug(f"Request files: {request.files}")
#         logger.debug(f"Request form data: {request.form}")
        
#         if 'file' not in request.files:
#             logger.error("No file part in request")
#             return jsonify({"error": "No file part"}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             logger.error("No selected file")
#             return jsonify({"error": "No selected file"}), 400
        
#         if not allowed_file(file.filename):
#             logger.error(f"File type not allowed: {file.filename}")
#             return jsonify({"error": "File type not allowed"}), 400

#         if not openai.api_key:
#             logger.error("OpenAI API key is not set")
#             return jsonify({"error": "OpenAI API key is not configured"}), 500

#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         logger.debug(f"Saving file to: {file_path}")
        
#         # Ensure upload directory exists
#         os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
#         file.save(file_path)
        
#         try:
#             logger.debug("Extracting text from file")
#             text = extract_text_from_file(file_path)
#             logger.debug(f"Extracted text length: {len(text)}")
            
#             # Store file information in database
#             file_size = os.path.getsize(file_path)
#             file_type = os.path.splitext(filename)[1].lower()
#             file_id = insert_file(filename, file_type, file_size, text)
            
#             # Remove the file after extraction
#             os.remove(file_path)
#             logger.debug("File removed after extraction")
            
#             # Get additional parameters from the request
#             num_questions = int(request.form.get('num_questions', 5))
#             difficulty = request.form.get('difficulty', 'mixed')
#             logger.debug(f"Generating {num_questions} questions with {difficulty} difficulty")

#             # Introduce randomness by selecting a random portion of the text
#             text_length = len(text)
#             start_index = random.randint(0, max(0, text_length - 4000))
#             selected_text = text[start_index:start_index + 4000]
#             logger.debug(f"Selected text length: {len(selected_text)}")

#             prompt = f"""Based on the following text, generate {num_questions} multiple-choice questions with {difficulty} difficulty. 
#             Your response must be a valid JSON array of objects, with no additional text before or after. Each object should have the following structure:
#             {{
#                 "qno": <question number>,
#                 "question": "<the question>",
#                 "option1": "<first option>",
#                 "option2": "<second option>",
#                 "option3": "<third option>",
#                 "option4": "<fourth option>",
#                 "answer": "<correct option>",
#                 "difficulty": "<easy/medium/hard>"
#             }}
#             Ensure that:
#             1. The "answer" field contains the exact text of the correct option.
#             2. The "difficulty" field is one of "easy", "medium", or "hard".
#             3. The questions are appropriate for the requested difficulty level.
#             4. Your entire response is a valid JSON array, starting with '[' and ending with ']'.
#             5. Do not include any explanations, comments, or additional text outside the JSON structure.

#             Text: {selected_text}
#             """

#             logger.debug("Sending request to OpenAI API")
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant that generates quiz questions based on provided text."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 max_tokens=2000
#             )

#             content = response.choices[0].message.content.strip()
#             logger.debug("Received response from OpenAI API")

#             if not content:
#                 logger.error("Empty response from API")
#                 return jsonify({"error": "Empty response from API"}), 500

#             try:
#                 # Try to clean the content before parsing
#                 cleaned_content = content.replace('\n', '').replace('\r', '').strip()
#                 questions = json.loads(cleaned_content)
#                 logger.debug(f"Successfully parsed {len(questions)} questions")

#                 # Store quiz in database
#                 quiz_id = insert_quiz(file_id, num_questions, difficulty)

#                 # Store questions in database
#                 for q in questions:
#                     insert_question(
#                         quiz_id=quiz_id,
#                         question_number=q['qno'],
#                         question_text=q['question'],
#                         option1=q['option1'],
#                         option2=q['option2'],
#                         option3=q['option3'],
#                         option4=q['option4'],
#                         correct_answer=q['answer'],
#                         difficulty=q['difficulty']
#                     )

#                 return jsonify({
#                     "quiz_id": quiz_id,
#                     "questions": questions
#                 })
                
#             except json.JSONDecodeError as json_error:
#                 logger.error(f"JSON parsing error: {str(json_error)}")
#                 logger.error(f"Raw response: {content}")
#                 logger.error(f"Cleaned response: {cleaned_content}")
#                 return jsonify({
#                     "error": "Failed to parse ChatGPT response as JSON",
#                     "raw_response": content,
#                     "cleaned_response": cleaned_content,
#                     "json_error": str(json_error)
#                 }), 500

#         except Exception as e:
#             logger.error(f"Error processing file: {str(e)}")
#             logger.error(f"Traceback: {traceback.format_exc()}")
#             return jsonify({"error": str(e), "type": str(type(e))}), 500
            
#     except Exception as e:
#         logger.error(f"Unexpected error in generate_questions: {str(e)}")
#         logger.error(f"Traceback: {traceback.format_exc()}")
#         return jsonify({"error": str(e), "type": str(type(e))}), 500
