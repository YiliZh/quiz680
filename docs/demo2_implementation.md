# Demo 2: Enhanced Implementation Details

## 1. System Architecture

### 1.1 Overview
```
Frontend (React) → Backend (FastAPI) → Cache (Redis) → Database (PostgreSQL)
```

### 1.2 Technology Stack
- **Frontend**: React 18.2.0, Material-UI 5.14.0, Redux Toolkit
- **Backend**: FastAPI 0.104.0, Python 3.8+
- **Database**: PostgreSQL 15.0
- **Cache**: Redis 7.0
- **Authentication**: JWT, RBAC
- **PDF Processing**: pdfminer.six, pdfplumber
- **NLP**: NLTK, spaCy

## 2. Enhanced Components

### 2.1 Role-Based Access Control
```python
class RBACManager:
    def __init__(self):
        self.roles = {
            "admin": ["read", "write", "delete", "manage_users"],
            "teacher": ["read", "write", "manage_content"],
            "student": ["read", "take_quiz"]
        }

    def check_permission(self, user_role: str, required_permission: str) -> bool:
        return required_permission in self.roles.get(user_role, [])

    def get_user_permissions(self, user_role: str) -> List[str]:
        return self.roles.get(user_role, [])
```

### 2.2 Advanced PDF Processing
```python
class EnhancedPDFProcessor:
    def __init__(self):
        self.layout_analyzer = LayoutAnalyzer()
        self.chapter_detector = ChapterDetector()
        self.text_extractor = TextExtractor()

    async def process_pdf(self, file: UploadFile) -> Dict[str, Any]:
        # Extract text with layout preservation
        text_with_layout = await self.text_extractor.extract_with_layout(file)
        
        # Detect chapters and sections
        chapters = self.chapter_detector.detect_chapters(text_with_layout)
        
        # Analyze layout structure
        layout = self.layout_analyzer.analyze(text_with_layout)
        
        return {
            "content": text_with_layout,
            "chapters": chapters,
            "layout": layout,
            "metadata": self._extract_metadata(file)
        }

class LayoutAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        # Implementation for layout analysis
        pass

class ChapterDetector:
    def detect_chapters(self, text: str) -> List[Dict[str, Any]]:
        # Implementation for chapter detection
        pass
```

### 2.3 Domain-Specific Question Generation
```python
class DomainQuestionGenerator:
    def __init__(self):
        self.domain_patterns = {
            "computer_science": {
                "algorithms": [
                    "What is the time complexity of {algorithm}?",
                    "Which data structure would be most efficient for {scenario}?"
                ],
                "programming": [
                    "How would you implement {concept} in {language}?",
                    "What is the output of this code snippet?"
                ]
            },
            "mathematics": {
                "algebra": [
                    "Solve for x in the equation: {equation}",
                    "What is the derivative of {function}?"
                ],
                "geometry": [
                    "Calculate the area of {shape} with dimensions {dimensions}",
                    "What is the volume of {solid}?"
                ]
            }
        }
        self.nlp = spacy.load("en_core_web_sm")

    def generate_questions(self, content: str, domain: str, num_questions: int = 5) -> List[Dict]:
        # Implementation for domain-specific question generation
        pass
```

### 2.4 Enhanced Database Schema
```sql
-- Enhanced Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    preferences JSONB
);

-- Enhanced PDFs Table
CREATE TABLE pdfs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    content TEXT,
    chapters JSONB,
    layout JSONB,
    metadata JSONB,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(20)
);

-- Enhanced Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    pdf_id INTEGER REFERENCES pdfs(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,
    domain VARCHAR(50),
    difficulty VARCHAR(20),
    options JSONB,
    correct_answer VARCHAR(255) NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Progress Table
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question_id INTEGER REFERENCES questions(id),
    is_correct BOOLEAN,
    time_taken INTEGER,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Caching Implementation

### 3.1 Redis Cache Manager
```python
class RedisCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=0
        )
        self.default_ttl = 3600  # 1 hour

    async def get_cached_data(self, key: str) -> Optional[Any]:
        data = await self.redis_client.get(key)
        return json.loads(data) if data else None

    async def set_cached_data(self, key: str, value: Any, ttl: int = None) -> None:
        await self.redis_client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(value)
        )
```

### 3.2 Cache Strategies
```python
class CacheStrategy:
    def __init__(self, cache_manager: RedisCacheManager):
        self.cache = cache_manager

    async def get_or_set(self, key: str, getter_func: Callable, ttl: int = None) -> Any:
        cached_data = await self.cache.get_cached_data(key)
        if cached_data:
            return cached_data

        data = await getter_func()
        await self.cache.set_cached_data(key, data, ttl)
        return data
```

## 4. Advanced API Features

### 4.1 Rate Limiting
```python
class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_limit = 100
        self.default_window = 3600  # 1 hour

    async def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        key = f"rate_limit:{endpoint}:{user_id}"
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, self.default_window)
        return current <= self.default_limit
```

### 4.2 API Versioning
```python
# api/v1/endpoints.py
router = APIRouter(prefix="/v1")

@router.get("/pdfs")
async def list_pdfs_v1():
    # V1 implementation

# api/v2/endpoints.py
router = APIRouter(prefix="/v2")

@router.get("/pdfs")
async def list_pdfs_v2():
    # V2 implementation with enhanced features
```

## 5. Enhanced Frontend Features

### 5.1 State Management
```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import pdfReducer from './pdfSlice';
import quizReducer from './quizSlice';
import userReducer from './userSlice';

export const store = configureStore({
    reducer: {
        pdf: pdfReducer,
        quiz: quizReducer,
        user: userReducer,
    },
});

// store/pdfSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

const pdfSlice = createSlice({
    name: 'pdf',
    initialState: {
        pdfs: [],
        currentPdf: null,
        loading: false,
        error: null,
    },
    reducers: {
        // Reducer implementations
    },
});
```

### 5.2 Advanced Components
```typescript
// components/pdf/PDFViewer.tsx
const PDFViewer: React.FC<PDFViewerProps> = ({ pdfId }) => {
    const [pdf, setPdf] = useState<PDF | null>(null);
    const [selectedChapter, setSelectedChapter] = useState<string | null>(null);

    useEffect(() => {
        const loadPDF = async () => {
            const data = await api.getPDF(pdfId);
            setPdf(data);
        };
        loadPDF();
    }, [pdfId]);

    return (
        <div className="pdf-viewer">
            <ChapterList
                chapters={pdf?.chapters}
                onSelect={setSelectedChapter}
            />
            <PDFContent
                content={pdf?.content}
                chapter={selectedChapter}
            />
        </div>
    );
};
```

## 6. Testing and Quality Assurance

### 6.1 Enhanced Testing
```python
# tests/test_pdf_processing.py
class TestPDFProcessing:
    @pytest.mark.asyncio
    async def test_chapter_detection(self):
        # Test implementation

    @pytest.mark.asyncio
    async def test_layout_analysis(self):
        # Test implementation

# tests/test_question_generation.py
class TestQuestionGeneration:
    @pytest.mark.asyncio
    async def test_domain_specific_questions(self):
        # Test implementation

    @pytest.mark.asyncio
    async def test_difficulty_adjustment(self):
        # Test implementation
```

### 6.2 Performance Testing
```python
# tests/performance/test_api_performance.py
class TestAPIPerformance:
    @pytest.mark.asyncio
    async def test_pdf_upload_performance(self):
        # Test implementation

    @pytest.mark.asyncio
    async def test_question_generation_performance(self):
        # Test implementation
```

## 7. Monitoring and Logging

### 7.1 Enhanced Logging
```python
class EnhancedLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_api_request(self, request: Request, response: Response, duration: float):
        self.logger.info(
            f"API Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.2f}s"
        )
```

### 7.2 Performance Monitoring
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "api_requests": Counter(),
            "response_times": Histogram(),
            "error_rates": Counter(),
        }

    def record_api_request(self, endpoint: str, duration: float, status: int):
        self.metrics["api_requests"].inc()
        self.metrics["response_times"].observe(duration)
        if status >= 400:
            self.metrics["error_rates"].inc()
```

## 8. Security Enhancements

### 8.1 Advanced Authentication
```python
class EnhancedAuthManager:
    def __init__(self):
        self.jwt_manager = JWTManager()
        self.rbac_manager = RBACManager()

    async def authenticate_user(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        user = await self._verify_credentials(credentials)
        if not user:
            raise AuthenticationError("Invalid credentials")

        permissions = self.rbac_manager.get_user_permissions(user.role)
        token = self.jwt_manager.create_access_token({
            "sub": user.id,
            "role": user.role,
            "permissions": permissions
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "permissions": permissions
        }
```

### 8.2 Security Middleware
```python
class SecurityMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
```

## 9. Deployment and DevOps

### 9.1 Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/quiz_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=quiz_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 9.2 CI/CD Pipeline
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deployment steps
```

## 10. Documentation

### 10.1 API Documentation
```python
# Using FastAPI's automatic documentation
app = FastAPI(
    title="Quiz Platform API",
    description="Enhanced API for the Quiz Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Example endpoint with detailed documentation
@router.post("/pdfs/upload")
async def upload_pdf(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload and process a PDF file.
    
    Args:
        file: The PDF file to upload
        current_user: The authenticated user
        
    Returns:
        Dict containing the processed PDF information
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    # Implementation
```

### 10.2 Code Documentation
```python
class PDFProcessor:
    """
    Enhanced PDF processing class that handles file upload, text extraction,
    and layout analysis.
    
    Attributes:
        layout_analyzer: Analyzes PDF layout structure
        chapter_detector: Detects chapters and sections
        text_extractor: Extracts text while preserving layout
        
    Methods:
        process_pdf: Main method for processing PDF files
        _extract_metadata: Extracts PDF metadata
    """
    
    def __init__(self):
        """Initialize the PDF processor with required components."""
        self.layout_analyzer = LayoutAnalyzer()
        self.chapter_detector = ChapterDetector()
        self.text_extractor = TextExtractor()
``` 