# Running the DocParser Platform

This guide provides step-by-step instructions for running the complete DocParser platform, including both backend and frontend components.

## Prerequisites

- Python 3.8 or higher
- Node.js 18.x or 20.x
- npm or yarn
- Git

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd D:\Projects\DocParser\backend
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate

# Or for Command Prompt
venv\Scripts\activate.bat
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory with the following content:

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

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 5. Run Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Frontend Setup

### 1. Open a New Terminal and Navigate to Frontend

```bash
cd D:\Projects\DocParser\frontend
```

### 2. Install Frontend Dependencies

```bash
npm install
```

### 3. Configure Frontend Environment

The `.env.local` file should already exist with:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# WebSocket Configuration  
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

If it doesn't exist, create it with the above content.

### 4. Run Frontend Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Using the Platform

### 1. Access the Application

Open your web browser and navigate to http://localhost:3000

### 2. Upload and Process Documents

1. Click on the upload area or drag and drop a document
2. Supported formats: PDF, DOCX, XLSX, PPT, TXT, PNG, JPG
3. The document will be:
   - Uploaded to the backend
   - Processed using AI (if OpenAI API key is configured)
   - Converted to Markdown format
   - Displayed in the viewer

### 3. Features

- **Document Upload**: Drag-and-drop or click to upload
- **AI Processing**: Automatic text extraction and analysis
- **Markdown Conversion**: Documents are converted to Markdown format
- **Real-time Progress**: See processing progress in real-time
- **Document History**: View previously processed documents
- **Markdown Editor**: Edit the generated Markdown content

## Troubleshooting

### Backend Issues

1. **Port 8000 already in use**
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill the process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

2. **OpenAI API errors**
   - Ensure your API key is valid
   - Check your OpenAI account has credits
   - Verify the API key starts with 'sk-'

3. **Database errors**
   - Delete `docparser.db` and restart to recreate
   - Run migrations if available

### Frontend Issues

1. **Cannot connect to backend**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend `.env`
   - Verify `NEXT_PUBLIC_API_BASE_URL` in frontend `.env.local`

2. **Upload fails**
   - Check file size (max 10MB by default)
   - Ensure file format is supported
   - Check browser console for errors

3. **Processing timeout**
   - Large files may take longer to process
   - Check backend logs for errors
   - Ensure OpenAI API is responsive

### Common Errors and Solutions

1. **"old.filter is not a function"**
   - This has been fixed in the latest code
   - Clear browser cache and restart frontend

2. **CORS errors**
   - Ensure frontend URL is in backend CORS_ORIGINS
   - Restart backend after changing .env

3. **File not found errors**
   - Ensure upload, temp, and markdown directories exist
   - Backend creates them automatically on startup

## Development Tips

### Running in Production Mode

Backend:
```bash
# Use production WSGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

Frontend:
```bash
# Build and run production server
npm run build
npm run start
```

### Monitoring Logs

Backend logs are stored in `backend/logs/app.log`

To watch logs in real-time:
```bash
# Windows PowerShell
Get-Content -Path "logs/app.log" -Wait -Tail 10
```

### API Testing

Use the Swagger UI at http://localhost:8000/docs to test API endpoints directly.

## Security Considerations

1. **Never commit `.env` files** to version control
2. **Use strong secret keys** in production
3. **Restrict CORS origins** in production
4. **Enable HTTPS** when deploying
5. **Regularly update dependencies**

## Next Steps

1. Configure a proper database (PostgreSQL recommended for production)
2. Set up proper logging and monitoring
3. Implement user authentication if needed
4. Configure a reverse proxy (nginx) for production deployment
5. Set up CI/CD pipelines for automated testing and deployment
