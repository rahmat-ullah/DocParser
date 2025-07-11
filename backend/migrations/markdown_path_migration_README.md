# Markdown Path Migration Guide

## Overview
This migration adds a `markdown_path` column to the `documents` table to store the path to markdown versions of documents.

## Changes Made

### 1. Database Migration
- Created migration file: `86ea82d35c42_add_markdown_path_column_to_documents_.py`
- Adds nullable `markdown_path VARCHAR(500)` column to `documents` table

### 2. SQLAlchemy Model Updates
- Updated `Document` model in `app/models/document.py`:
  - Added `markdown_path: Mapped[Optional[str]]` field
  - Updated `to_dict()` method to include `markdown_path`

### 3. Pydantic Schema Updates
- Updated `DocumentResponse` schema to include `markdown_path` field
- Updated `DocumentUpdate` schema to allow updating `markdown_path`
- Created new schemas in `app/schemas/markdown.py`:
  - `MarkdownPathUpdate`: For updating markdown path
  - `MarkdownPathResponse`: For returning markdown path info

### 4. Service Layer Updates
- Added methods to `DocumentService`:
  - `update_markdown_path()`: Update markdown path for a document
  - `get_markdown_path()`: Retrieve markdown path for a document

## Running the Migration

### First Time Setup (if alembic was not previously configured)
1. The alembic configuration has been initialized
2. The `alembic.ini` and `migrations/env.py` have been configured

### Apply the Migration
```bash
# Check current migration status
alembic current

# Review the migration that will be applied
alembic show 86ea82d35c42

# Apply the migration
alembic upgrade head

# Or apply specific migration
alembic upgrade 86ea82d35c42
```

### Rollback (if needed)
```bash
# Rollback to previous migration
alembic downgrade e9789268d113
```

## Usage Examples

### Using the DocumentService

```python
from app.services.document_service import DocumentService
from app.db.database import get_db

# In an async context:
async def example():
    async for db in get_db():
        doc_service = DocumentService(db)
        
        # Update markdown path
        updated_doc = await doc_service.update_markdown_path(
            document_id="123-456-789",
            markdown_path="/uploads/markdown/doc-123.md"
        )
        
        # Get markdown path
        markdown_path = await doc_service.get_markdown_path("123-456-789")
```

### API Endpoint Example

```python
from fastapi import APIRouter, Depends
from app.schemas.markdown import MarkdownPathUpdate, MarkdownPathResponse
from app.services.document_service import DocumentService

router = APIRouter()

@router.put("/documents/{document_id}/markdown-path")
async def update_markdown_path(
    document_id: str,
    markdown_update: MarkdownPathUpdate,
    doc_service: DocumentService = Depends(get_document_service)
) -> MarkdownPathResponse:
    document = await doc_service.update_markdown_path(
        document_id, 
        markdown_update.markdown_path
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return MarkdownPathResponse(
        document_id=document.id,
        markdown_path=document.markdown_path
    )
```

## Multi-versioning Consideration

If multi-versioning is needed in the future, the `markdown_path` column can be changed to a JSON field to store multiple versions:

```python
# Future enhancement example
markdown_paths = {
    "versions": [
        {
            "version": "1.0",
            "path": "/uploads/markdown/v1/doc-123.md",
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "version": "2.0",
            "path": "/uploads/markdown/v2/doc-123.md",
            "created_at": "2024-01-02T00:00:00Z"
        }
    ],
    "current_version": "2.0"
}
```

For now, the simple VARCHAR field suffices for single markdown file per document.
