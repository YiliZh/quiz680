# Demo 1: Foundation Implementation Details

## 1. System Architecture

### 1.1 Overview
```
Frontend (React) → Backend (FastAPI) → Database (PostgreSQL)
```

### 1.2 Technology Stack
- **Frontend**: React 18.2.0, Material-UI 5.14.0
- **Backend**: FastAPI 0.104.0, Python 3.8+
- **Database**: PostgreSQL 15.0
- **Authentication**: JWT, bcrypt
- **API Documentation**: Swagger UI

## 2. Core Components Implementation

### 2.1 Authentication System
```python
# JWT Implementation
class JWTManager:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

# Password Hashing
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

### 2.2 PDF Processing
```python
class PDFProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    async def process_pdf(self, file: UploadFile) -> Dict[str, Any]:
        if not self._validate_file(file):
            raise ValueError("Invalid file format or size")
        
        content = await self._extract_text(file)
        return {
            "content": content,
            "metadata": self._extract_metadata(file)
        }

    def _extract_text(self, file: UploadFile) -> str:
        # Basic text extraction using PyPDF2
        text = ""
        with open(file.filename, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
```

### 2.3 Question Generation
```python
class BasicQuestionGenerator:
    def __init__(self):
        self.question_templates = {
            "multiple_choice": [
                "What is {concept}?",
                "Which of the following describes {concept}?",
                "What is the main purpose of {concept}?"
            ],
            "true_false": [
                "{statement} (True/False)",
                "Is it true that {statement}?",
                "Does {concept} {action}? (True/False)"
            ]
        }

    def generate_questions(self, content: str, num_questions: int = 5) -> List[Dict]:
        questions = []
        concepts = self._extract_concepts(content)
        
        for _ in range(num_questions):
            question_type = random.choice(["multiple_choice", "true_false"])
            template = random.choice(self.question_templates[question_type])
            concept = random.choice(concepts)
            
            question = {
                "type": question_type,
                "text": template.format(concept=concept),
                "options": self._generate_options(concept, question_type)
            }
            questions.append(question)
        
        return questions
```

### 2.4 Database Schema
```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PDFs Table
CREATE TABLE pdfs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    content TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    pdf_id INTEGER REFERENCES pdfs(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,
    options JSONB,
    correct_answer VARCHAR(255) NOT NULL
);
```

## 3. API Endpoints

### 3.1 Authentication Endpoints
```python
@router.post("/register")
async def register(user: UserCreate):
    # Implementation details

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm):
    # Implementation details

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    # Implementation details
```

### 3.2 PDF Endpoints
```python
@router.post("/upload")
async def upload_pdf(file: UploadFile, current_user: User = Depends(get_current_user)):
    # Implementation details

@router.get("/pdfs")
async def list_pdfs(current_user: User = Depends(get_current_user)):
    # Implementation details

@router.get("/pdfs/{pdf_id}")
async def get_pdf(pdf_id: int, current_user: User = Depends(get_current_user)):
    # Implementation details
```

### 3.3 Question Endpoints
```python
@router.post("/generate-questions")
async def generate_questions(pdf_id: int, num_questions: int = 5):
    # Implementation details

@router.get("/questions/{pdf_id}")
async def get_questions(pdf_id: int):
    # Implementation details
```

## 4. Frontend Implementation

### 4.1 Component Structure
```
src/
├── components/
│   ├── auth/
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── pdf/
│   │   ├── PDFUpload.tsx
│   │   └── PDFList.tsx
│   └── quiz/
│       ├── QuestionList.tsx
│       └── Quiz.tsx
├── services/
│   ├── api.ts
│   └── auth.ts
└── App.tsx
```

### 4.2 Key Components
```typescript
// PDFUpload.tsx
const PDFUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);

    const handleUpload = async () => {
        if (!file) return;
        
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            await api.uploadPDF(formData);
            // Handle success
        } catch (error) {
            // Handle error
        } finally {
            setUploading(false);
        }
    };

    return (
        // Component JSX
    );
};
```

## 5. Error Handling

### 5.1 Backend Error Handling
```python
class APIError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )
```

### 5.2 Frontend Error Handling
```typescript
// Error handling utility
const handleApiError = (error: any) => {
    if (error.response) {
        // Handle API error
        const message = error.response.data.message;
        // Show error notification
    } else {
        // Handle network error
    }
};
```

## 6. Testing

### 6.1 Backend Tests
```python
# test_auth.py
def test_user_registration():
    # Test implementation

def test_user_login():
    # Test implementation

# test_pdf.py
def test_pdf_upload():
    # Test implementation

def test_pdf_processing():
    # Test implementation
```

### 6.2 Frontend Tests
```typescript
// PDFUpload.test.tsx
describe('PDFUpload', () => {
    it('should handle file upload', () => {
        // Test implementation
    });

    it('should show error on invalid file', () => {
        // Test implementation
    });
});
```

## 7. Deployment

### 7.1 Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Environment Variables
```env
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

## 8. Performance Considerations

### 8.1 Database Optimization
- Indexed fields for frequent queries
- Connection pooling
- Query optimization

### 8.2 API Optimization
- Response compression
- Caching headers
- Pagination for large datasets

## 9. Security Measures

### 9.1 Authentication Security
- Password hashing with bcrypt
- JWT token expiration
- Secure password requirements

### 9.2 API Security
- CORS configuration
- Rate limiting
- Input validation

## 10. Monitoring

### 10.1 Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### 10.2 Basic Metrics
- Request count
- Response time
- Error rate
- User activity 