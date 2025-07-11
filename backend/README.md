# Document Parser Backend

A comprehensive FastAPI-based backend for document processing and AI-powered analysis.

## Features

- **Document Upload & Management**: Secure file upload with validation and storage
- **AI-Powered Analysis**: OpenAI Vision API integration for document description and analysis
- **Image & Diagram Context Parsing**: Extract context from images and diagrams using GPT-4o Vision model
- **OCR Fallback**: Tesseract OCR integration as backup when AI processing fails
- **Async Processing**: Fully asynchronous implementation with retry logic
- **Database Integration**: SQLAlchemy with async support for document metadata storage
- **Health Monitoring**: Comprehensive health checks for all services
- **Clean Architecture**: Well-structured codebase with separation of concerns

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes and endpoints
│   │   └── v1/
│   │       ├── endpoints/      # Individual endpoint modules
│   │       └── router.py       # Main API router
│   ├── core/                   # Core configuration and setup
│   │   ├── config.py          # Application configuration
│   │   ├── logging.py         # Logging configuration
│   │   └── security.py        # Security utilities
│   ├── db/                     # Database configuration
│   │   └── database.py        # Database setup and connections
│   ├── models/                 # SQLAlchemy models
│   │   ├── document.py        # Document model
│   │   ├── user.py            # User model
│   │   └── processing_job.py  # Processing job model
│   ├── schemas/                # Pydantic schemas
│   │   ├── document.py        # Document schemas
│   │   ├── user.py            # User schemas
│   │   └── common.py          # Common schemas
│   ├── services/               # Business logic services
│   │   ├── ai_service.py      # AI processing service
│   │   └── document_service.py # Document management service
│   ├── utils/                  # Utility functions
│   │   └── file_utils.py      # File handling utilities
│   └── main.py                # FastAPI application entry point
├── tests/                      # Test suite
├── migrations/                 # Database migrations
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **OpenAI**: AI processing and vision analysis
- **Tesseract**: OCR fallback processing
- **Pillow**: Image processing
- **httpx**: Async HTTP client
- **pytest**: Testing framework
- **respx**: HTTP mocking for tests

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd DocParser/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**:
   Create a `.env` file in the backend directory:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_VISION_MODEL=gpt-4o  # GPT-4o model for image/diagram analysis
   
   # Application Settings
   DEBUG=true
   SECRET_KEY=your_secret_key_here
   
   # Database
   DATABASE_URL=sqlite:///./docparser.db
   
   # File Upload
   MAX_UPLOAD_SIZE=10485760  # 10MB
   UPLOAD_DIR=./uploads
   TEMP_DIR=./temp
   
   # CORS
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   
   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=logs/app.log
   
   # OCR Settings (Optional - for fallback)
   OCR_FALLBACK_ENABLED=true
   TESSERACT_PATH=  # Leave empty to use system PATH
   ```

## Usage

1. **Start the development server**:
   ```bash
   python -m app.main
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Health check**:
   ```bash
   curl http://localhost:8000/health
   ```

## API Endpoints

### Health Monitoring
- `GET /health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check with component status

### Document Management
- `GET /api/v1/documents/` - List documents
- `POST /api/v1/documents/` - Create document
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

### File Upload
- `POST /api/v1/upload/` - Upload file for processing

### Document Processing
- `POST /api/v1/processing/{document_id}` - Process document with AI

### User Management
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## Configuration

The application uses environment variables for configuration. Key settings:

- **OPENAI_API_KEY**: Required for AI processing
- **OPENAI_VISION_MODEL**: Model for image/diagram analysis (default: gpt-4o)
- **DATABASE_URL**: Database connection string
- **MAX_UPLOAD_SIZE**: Maximum file upload size (bytes)
- **ALLOWED_FILE_TYPES**: Comma-separated list of allowed file extensions
- **OCR_FALLBACK_ENABLED**: Enable/disable OCR fallback (default: true)

## Image and Diagram Context Parsing

The backend automatically extracts context from images and diagrams within documents using OpenAI's GPT-4o Vision model:

### Features:
- **Automatic Detection**: Images and diagrams are automatically detected during document processing
- **Context Extraction**: Detailed descriptions of visual content including:
  - Text within images
  - Tables and charts
  - Diagrams and flowcharts
  - Visual elements and their relationships
- **Smart Fallback**: If Vision API fails, the system falls back to OCR for text extraction
- **Integration**: Extracted context is included in the final Markdown output

### Example Output:
```markdown
![Image](image_path.png)

AI Description: This diagram shows a system architecture with three main components:
1. Frontend (React/Next.js)
2. Backend API (FastAPI)
3. Database (PostgreSQL)
The components are connected via REST API calls...
```

## Development

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting

Run code quality checks:
```bash
black app/
isort app/
ruff check app/
```

### Database Migrations
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Production Deployment

1. **Set production environment variables**:
   ```env
   DEBUG=false
   SECRET_KEY=strong_production_secret
   DATABASE_URL=postgresql://user:password@localhost/docparser
   ```

2. **Use production WSGI server**:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Configure reverse proxy** (nginx/Apache) for static files and SSL

## Security Considerations

- API keys are loaded from environment variables
- File uploads are validated for type and size
- CORS is configurable for cross-origin requests
- Trusted host middleware in production
- SQL injection protection via SQLAlchemy ORM

## Monitoring

The application provides comprehensive health checks:
- Database connectivity
- AI service availability
- OCR service status
- File system access

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Use type hints and docstrings
5. Run code quality checks before committing

## License

[Your License Here]
