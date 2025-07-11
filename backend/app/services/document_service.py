"""
Document service for managing document operations and database interactions.
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.core.config import get_settings
from app.services.ai_service import get_ai_service


settings = get_settings()


class DocumentService:
    """
    Service class for document management operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_document(
        self,
        filename: str,
        file_content: bytes,
        file_type: str,
        mime_type: str,
        user_id: Optional[str] = None
    ) -> Document:
        """
        Create a new document record and save file.
        
        Args:
            filename: Original filename
            file_content: File content as bytes
            file_type: File extension
            mime_type: MIME type of the file
            user_id: ID of the user who uploaded the document
            
        Returns:
            Document: Created document instance
        """
        # Generate unique filename
        doc_id = str(uuid.uuid4())
        stored_filename = f"{doc_id}{file_type}"
        file_path = os.path.join(settings.upload_dir, stored_filename)
        
        # Save file to disk
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create document record
        document = Document(
            id=doc_id,
            filename=stored_filename,
            original_filename=filename,
            file_size=len(file_content),
            file_type=file_type,
            mime_type=mime_type,
            file_path=file_path,
            user_id=user_id,
            processing_status="pending"
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document or None if not found
        """
        result = await self.db.execute(
            select(Document).where(Document.id == document_id, Document.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def list_documents(
        self,
        user_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Document]:
        """
        List documents with optional filtering.
        
        Args:
            user_id: Filter by user ID
            limit: Number of documents to return
            offset: Offset for pagination
            
        Returns:
            List of documents
        """
        query = select(Document).where(Document.is_deleted == False)
        
        if user_id:
            query = query.where(Document.user_id == user_id)
        
        query = query.order_by(Document.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_document(
        self,
        document_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Document]:
        """
        Update document fields.
        
        Args:
            document_id: Document ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated document or None if not found
        """
        # Update the document
        result = await self.db.execute(
            update(Document)
            .where(Document.id == document_id, Document.is_deleted == False)
            .values(**updates)
            .returning(Document)
        )
        
        document = result.scalar_one_or_none()
        if document:
            await self.db.commit()
            await self.db.refresh(document)
        
        return document
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Soft delete a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        document = await self.get_document(document_id)
        if not document:
            return False
        
        # Soft delete
        await self.update_document(
            document_id,
            {
                "is_deleted": True,
                "deleted_at": datetime.utcnow()
            }
        )
        
        # Remove file from disk
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception:
            pass  # File deletion failure shouldn't fail the operation
        
        return True
    
    async def process_document(
        self,
        document_id: str,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Process a document with AI analysis.
        
        Args:
            document_id: Document ID
            processing_options: Processing configuration
            
        Returns:
            True if processing was initiated successfully
        """
        document = await self.get_document(document_id)
        if not document:
            return False
        
        # Update status to processing
        await self.update_document(
            document_id,
            {
                "processing_status": "processing",
                "processing_started_at": datetime.utcnow(),
                "processing_options": processing_options or {}
            }
        )
        
        try:
            # Read file content
            with open(document.file_path, "rb") as f:
                file_content = f.read()
            
            # Convert to base64 for AI processing
            import base64
            base64_content = base64.b64encode(file_content).decode('utf-8')
            
            # Get AI service and process
            ai_service = await get_ai_service()
            description = await ai_service.describe_image(base64_content)
            
            # Update document with results
            await self.update_document(
                document_id,
                {
                    "processing_status": "completed",
                    "processing_completed_at": datetime.utcnow(),
                    "ai_description": description,
                    "extracted_text": description  # For now, use description as extracted text
                }
            )
            
            return True
            
        except Exception as e:
            # Update status to failed
            await self.update_document(
                document_id,
                {
                    "processing_status": "failed",
                    "processing_completed_at": datetime.utcnow(),
                    "processing_error": str(e)
                }
            )
            return False
    
    async def update_markdown_path(
        self,
        document_id: str,
        markdown_path: str
    ) -> Optional[Document]:
        """
        Update the markdown_path for a document.
        
        Args:
            document_id: Document ID
            markdown_path: Path to the markdown file
            
        Returns:
            Updated document or None if not found
        """
        return await self.update_document(
            document_id,
            {"markdown_path": markdown_path}
        )
    
    async def get_markdown_path(
        self,
        document_id: str
    ) -> Optional[str]:
        """
        Get the markdown_path for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Markdown path or None if not found
        """
        document = await self.get_document(document_id)
        return document.markdown_path if document else None
