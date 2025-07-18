"""
PDF Viewer API endpoints for streaming PDF files inline.
Serves PDFs with proper headers to enable in-browser viewing without downloads.
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer

from app.core.config import get_settings
from app.db.database import get_db
from app.models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()
settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_document_file_path(document_id: str, file_type: str, db: AsyncSession) -> Path:
    """
    Get the file path for a document.
    
    Args:
        document_id: The document ID
        file_type: Either 'original' or 'parsed'
        db: Database session
        
    Returns:
        Path to the document file
        
    Raises:
        HTTPException: If document not found or file doesn't exist
    """
    # Get document from database
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Determine file path based on type
    if file_type == "original":
        # Use the stored file_path from database
        file_path = Path(document.file_path)
    elif file_type == "parsed":
        # Check if parsed markdown file exists
        if document.markdown_path and Path(document.markdown_path).exists():
            # Try to find corresponding parsed PDF
            parsed_pdf_path = Path(settings.markdown_dir) / f"{document_id}.parsed.pdf"
            if parsed_pdf_path.exists():
                file_path = parsed_pdf_path
            else:
                # Fall back to original if no parsed PDF
                file_path = Path(document.file_path)
        else:
            # Fall back to original file if no parsed version
            file_path = Path(document.file_path)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'original' or 'parsed'")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return file_path


def create_pdf_response(file_path: Path, filename: str, request: Request) -> StreamingResponse:
    """
    Create a streaming response for PDF files with proper headers.
    
    Args:
        file_path: Path to the PDF file
        filename: Name for the PDF file
        request: FastAPI request object
        
    Returns:
        StreamingResponse with PDF content and inline headers
    """
    def generate():
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(8192)  # 8KB chunks
                if not chunk:
                    break
                yield chunk
    
    # Get file size for Content-Length header
    file_size = file_path.stat().st_size
    
    # Headers for inline PDF viewing
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f'inline; filename="{filename}"',
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
        "Access-Control-Allow-Origin": "*",  # Will be handled by CORS middleware
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        "Access-Control-Allow-Headers": "Range, Content-Range, Content-Length",
    }
    
    # Handle range requests for PDF.js
    range_header = request.headers.get("Range")
    if range_header:
        # Parse range header
        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Ensure valid range
        if start >= file_size or end >= file_size or start > end:
            raise HTTPException(status_code=416, detail="Range not satisfiable")
        
        # Update headers for partial content
        headers.update({
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Length": str(end - start + 1),
        })
        
        # Generator for partial content
        def generate_range():
            with open(file_path, "rb") as file:
                file.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        return StreamingResponse(
            generate_range(),
            status_code=206,  # Partial Content
            headers=headers,
            media_type="application/pdf"
        )
    
    return StreamingResponse(
        generate(),
        status_code=200,
        headers=headers,
        media_type="application/pdf"
    )


@router.get("/original/{document_id}")
async def stream_original_pdf(
    document_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream the original PDF file for inline viewing.
    
    Args:
        document_id: The document ID
        request: FastAPI request object
        db: Database session
        
    Returns:
        StreamingResponse with PDF content and inline headers
    """
    try:
        file_path = await get_document_file_path(document_id, "original", db)
        filename = f"original_{document_id}.pdf"
        
        return create_pdf_response(file_path, filename, request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming PDF: {str(e)}")


@router.get("/parsed/{document_id}")
async def stream_parsed_pdf(
    document_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream the parsed/processed PDF file for inline viewing.
    Falls back to original if parsed version doesn't exist.
    
    Args:
        document_id: The document ID
        request: FastAPI request object
        db: Database session
        
    Returns:
        StreamingResponse with PDF content and inline headers
    """
    try:
        file_path = await get_document_file_path(document_id, "parsed", db)
        filename = f"parsed_{document_id}.pdf"
        
        return create_pdf_response(file_path, filename, request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming PDF: {str(e)}")


@router.get("/compare/{document_id}")
async def get_pdf_comparison_urls(
    document_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get URLs for comparing original and parsed PDFs.
    
    Args:
        document_id: The document ID
        request: FastAPI request object
        db: Database session
        
    Returns:
        Dict with original and parsed PDF URLs
    """
    try:
        # Check if document exists
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get base URL from request
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        # Check if files exist
        original_path = Path(document.file_path)
        parsed_path = Path(settings.markdown_dir) / f"{document_id}.parsed.pdf"
        
        urls = {
            "original": f"{base_url}/api/v1/pdf/original/{document_id}",
            "parsed": f"{base_url}/api/v1/pdf/parsed/{document_id}",
            "original_exists": original_path.exists(),
            "parsed_exists": parsed_path.exists(),
            "document_name": document.original_filename,
            "document_status": document.processing_status
        }
        
        return urls
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PDF URLs: {str(e)}")


@router.head("/original/{document_id}")
async def head_original_pdf(
    document_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HEAD request for original PDF (for pre-flight checks).
    
    Args:
        document_id: The document ID
        request: FastAPI request object
        db: Database session
        
    Returns:
        Response with headers but no body
    """
    try:
        file_path = await get_document_file_path(document_id, "original", db)
        file_size = file_path.stat().st_size
        
        headers = {
            "Content-Type": "application/pdf",
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        }
        
        return Response(headers=headers)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking PDF: {str(e)}")


@router.head("/parsed/{document_id}")
async def head_parsed_pdf(
    document_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HEAD request for parsed PDF (for pre-flight checks).
    
    Args:
        document_id: The document ID
        request: FastAPI request object
        db: Database session
        
    Returns:
        Response with headers but no body
    """
    try:
        file_path = await get_document_file_path(document_id, "parsed", db)
        file_size = file_path.stat().st_size
        
        headers = {
            "Content-Type": "application/pdf",
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        }
        
        return Response(headers=headers)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking PDF: {str(e)}")
