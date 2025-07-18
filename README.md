# DocParser - AI-Powered Document Processing Platform

A comprehensive web application for parsing and converting multiple document formats to Markdown using AI-powered analysis. The platform supports PDF, DOCX, XLSX, PPTX, TXT, and various image formats with advanced features like table extraction, image analysis, and mathematical content processing.

## 🚀 Features

### Core Functionality
- **Multi-format Support**: PDF, DOCX, XLSX, PPTX, TXT, Markdown, PNG, JPG, GIF, BMP, TIFF, WebP
- **AI-Powered Processing**: OpenAI Vision model integration for intelligent document analysis
- **Advanced Content Recognition**: Tables, images, diagrams, mathematical content, and complex data structures
- **Markdown Conversion**: High-quality conversion with preserved formatting and structure
- **Real-time Processing**: Live progress tracking with WebSocket integration
- **Dual-panel Interface**: Original document viewer with synchronized Markdown preview

### AI Capabilities
- **Image Analysis**: Descriptive analysis of figures, diagrams, and visual content
- **Table Extraction**: Formatted Markdown tables with preserved structure
- **Mathematical Content**: LaTeX format output for equations and formulas
- **Contextual Understanding**: AI-powered content interpretation and description
- **Multi-modal Analysis**: Combined text and visual content processing

### User Experience
- **Drag-and-drop Upload**: Intuitive file upload with validation
- **Real-time Preview**: Live Markdown preview with syntax highlighting
- **Document History**: Persistent storage of processed documents
- **Export Functionality**: Download in Markdown and JSON formats
- **Responsive Design**: Optimized for various screen sizes
- **Search & Navigation**: Document search with click-to-highlight functionality

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── api/v1/endpoints/     # REST API endpoints
│   ├── core/                 # Configuration & logging
│   ├── db/                   # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic validation
│   ├── services/            # Business logic
│   ├── parsers/             # Document parsing
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── requirements.txt         # Dependencies
└── start_server.py         # Server startup
```

### Frontend (Next.js + TypeScript)
```
frontend/
├── app/                    # Next.js app router
├── components/             # React components
├── hooks/                  # Custom React hooks
├── lib/                    # Utility functions
├── types/                  # TypeScript definitions
└── __tests__/              # Test files
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **OpenAI API**: AI-powered document analysis
- **Pillow**: Image processing
- **PyPDF2**: PDF parsing
- **python-docx**: DOCX processing
- **openpyxl**: Excel file handling

### Frontend
- **Next.js 13**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first styling
- **Radix UI**: Accessible components
- **Socket.IO**: Real-time communication
- **React Query**: Data fetching and caching

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 18.x or 20.x
- npm or yarn
- Git
- OpenAI API key (for AI features)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/rahmat-ullah/DocParser.git
cd DocParser
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Environment is pre-configured for local development
```

### 4. Run the Application
```bash
# Terminal 1: Start backend (from backend directory)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend (from frontend directory)
cd frontend
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ⚙️ Configuration

### Backend Environment Variables
Create a `.env` file in the backend directory:

```env
# OpenAI Configuration (REQUIRED for AI processing)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
DEBUG=true
SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=sqlite:///./docparser.db

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
MARKDOWN_DIR=./markdown

# CORS (allows frontend to connect)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Frontend Environment
The frontend is pre-configured with:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

## 📚 API Endpoints

### Core Endpoints
- `GET /health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health status

### File Management
- `POST /api/v1/upload/` - Upload single file
- `POST /api/v1/upload/multiple` - Upload multiple files
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

### Processing
- `POST /api/v1/processing/{id}` - Start processing
- `GET /api/v1/processing/{id}/status` - Get status
- `GET /api/v1/processing/{id}/result` - Get results

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run unit tests
pytest tests/parsers/test_markdown_generator_saving.py -v

# Run integration tests
pytest tests/integration/test_upload_to_markdown_flow.py -v

# Run all tests with coverage
pytest --cov=app --cov-report=html tests/
```

### Frontend Tests
```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run Cypress E2E tests
npm run cypress:open
npm run cypress:run
```

### CI/CD Pipeline
The project includes comprehensive CI/CD with:
- **Type Checking**: TypeScript validation
- **Linting**: ESLint code quality checks
- **Testing**: Unit and integration tests
- **E2E Testing**: Cypress automated testing
- **Security**: Dependency vulnerability scanning

## 🎨 UI/UX Design

### Color Palette
- **Primary**: Dark Blue (#1a237e)
- **Secondary**: White (#ffffff)
- **Accent**: Black (#000000)

### Key Features
- **Dual-panel Interface**: Original document and Markdown preview
- **Toggle Switch**: Markdown/preview mode switching
- **Drag-and-drop**: Intuitive file upload
- **History Sidebar**: Organized document history
- **Loading States**: Progress indicators for processing
- **Responsive Design**: Mobile-friendly interface

## 🔧 Development

### Available Scripts

#### Backend
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest tests/ -v
pytest --cov=app tests/

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"
```

#### Frontend
```bash
# Development
npm run dev              # Start development server
npm run build           # Build for production
npm run start           # Start production server

# Code Quality
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues
npm run type-check      # Run TypeScript type checking

# Testing
npm run test            # Run tests
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Run tests with coverage

# CI/CD
npm run ci:all          # Run all CI checks
```

### Branch Strategy
- `main`: Production-ready code
- `feat/frontend-refactor`: Active refactor work
- Feature branches: Individual feature development

## 🚀 Deployment

### Production Setup
```bash
# Backend (using Gunicorn)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
npm run start
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t docparser .
docker run -p 8000:8000 docparser
```

## 🔒 Security

- **Input Validation**: Comprehensive validation for all inputs
- **File Upload Security**: Type and size validation
- **API Key Protection**: Secure handling of OpenAI API keys
- **CORS Configuration**: Proper cross-origin resource sharing
- **Dependency Auditing**: Regular security updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Ensure all tests pass: `npm run ci:all` (frontend) or `pytest` (backend)
5. Submit a pull request

### Development Standards
- **Code Coverage**: Minimum 80% test coverage
- **Type Safety**: Full TypeScript coverage for frontend
- **Linting**: ESLint and Pylint compliance
- **Documentation**: Comprehensive inline documentation

## 📊 Performance Targets

- **Core Web Vitals**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **Bundle Size**: < 500KB gzipped
- **Test Coverage**: > 80%
- **Accessibility**: WCAG 2.1 AA compliance

## 🐛 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **OpenAI API errors**
   - Verify API key is valid and has credits
   - Check API key starts with 'sk-'

3. **CORS errors**
   - Ensure frontend URL is in backend CORS_ORIGINS
   - Restart backend after changing .env

4. **File upload fails**
   - Check file size (max 10MB by default)
   - Verify supported file format
   - Check browser console for errors

### Getting Help
- Check the [API Documentation](http://localhost:8000/docs)
- Review existing issues on GitHub
- Create a new issue with detailed description

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- OpenAI for providing the AI models
- FastAPI community for the excellent web framework
- Next.js team for the React framework
- All contributors and maintainers

---

**Ready to start processing documents?** Follow the Quick Start guide above to get the DocParser platform running in minutes! 🚀
