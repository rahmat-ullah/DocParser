"""
Endpoints for image metadata retrieval and management.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import DocumentService
from app.schemas.image_metadata import ImageMetadata, ImageMetadataList
import json

router = APIRouter()


@router.get("/documents/{document_id}/images", response_model=ImageMetadataList)
async def get_document_images(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all image metadata for a specific document.
    
    Args:
        document_id: The ID of the document
        
    Returns:
        ImageMetadataList containing all images in the document
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document has been processed
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=409, 
            detail=f"Document processing not completed. Current status: {document.processing_status}"
        )
    
    # Extract image metadata from analysis results
    analysis_results = document.analysis_results or {}
    images_data = analysis_results.get("images", [])
    
    # Convert to ImageMetadata objects
    images = []
    for img_data in images_data:
        try:
            # If the data is already structured metadata, use it directly
            if isinstance(img_data, dict) and "id" in img_data:
                images.append(ImageMetadata(**img_data))
            # Otherwise, create a basic metadata structure
            else:
                images.append(ImageMetadata(
                    id=f"img-{len(images)}",
                    type="image",
                    title="",
                    caption="",
                    source={
                        "filename": document.original_filename,
                        "page": 0,
                        "documentSection": ""
                    },
                    description=str(img_data),
                    contextualSummary="",
                    linkedEntities=[],
                    textReferences=[],
                    semanticTags=[],
                    aiAnnotations={
                        "objectsDetected": [],
                        "ocrText": "",
                        "language": "en",
                        "explanationGenerated": ""
                    },
                    relations={"explains": [], "referencedBy": []}
                ))
        except Exception as e:
            # Skip invalid image data
            continue
    
    return ImageMetadataList(
        images=images,
        documentId=document_id,
        totalImages=len(images)
    )


@router.get("/documents/{document_id}/images/{image_id}", response_model=ImageMetadata)
async def get_image_metadata(
    document_id: str, 
    image_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve metadata for a specific image in a document.
    
    Args:
        document_id: The ID of the document
        image_id: The ID of the image
        
    Returns:
        ImageMetadata for the specified image
    """
    # First get all images
    images_list = await get_document_images(document_id, db)
    
    # Find the specific image
    for image in images_list.images:
        if image.id == image_id:
            return image
    
    raise HTTPException(status_code=404, detail="Image not found in document")


@router.post("/documents/{document_id}/analyze-images")
async def analyze_document_images(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    force_reanalysis: bool = False
):
    """
    Trigger image analysis for a document.
    
    Args:
        document_id: The ID of the document
        force_reanalysis: Whether to reanalyze already analyzed images
        
    Returns:
        Status message
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if already analyzed
    if not force_reanalysis and document.analysis_results and "images" in document.analysis_results:
        return {"message": "Images already analyzed", "image_count": len(document.analysis_results["images"])}
    
    # TODO: Implement image analysis trigger
    # This would typically queue a job to process images
    
    return {
        "message": "Image analysis queued",
        "document_id": document_id,
        "status": "pending"
    }
