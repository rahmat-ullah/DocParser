"""
Progress Emitter Service - Emits processing progress via Redis pub/sub for real-time updates.
"""

import json
import asyncio
import logging
from typing import Optional, Dict, Any
from ..parsers.ast_models import ParseProgress
from ..core.config import Settings

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ProgressEmitter:
    """
    Service for emitting progress updates via Redis pub/sub or direct HTTP calls.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the progress emitter."""
        self.settings = settings or Settings()
        self.redis_client: Optional[redis.Redis] = None
        self.frontend_base_url = getattr(self.settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        
    async def initialize_redis(self):
        """Initialize Redis connection for pub/sub."""
        if not REDIS_AVAILABLE:
            logger.info("Redis not available. Progress updates will use HTTP fallback")
            self.redis_client = None
            return
            
        try:
            self.redis_client = redis.Redis(
                host=getattr(self.settings, 'REDIS_HOST', 'localhost'),
                port=getattr(self.settings, 'REDIS_PORT', 6379),
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for progress updates")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to HTTP updates")
            self.redis_client = None

    async def emit_progress_redis(
        self, 
        document_id: str, 
        progress: ParseProgress
    ) -> bool:
        """
        Emit progress via Redis pub/sub.
        
        Args:
            document_id: Unique identifier for the document being processed
            progress: ParseProgress object containing progress information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            progress_data = {
                'documentId': document_id,
                'stage': self._map_stage_to_frontend(progress.stage),
                'progress': min(100, max(0, progress.progress * 100)),  # Convert to 0-100 range
                'message': progress.message,
                'timestamp': progress.timestamp,
                'details': progress.details or {}
            }

            await self.redis_client.publish(
                'document-progress', 
                json.dumps(progress_data)
            )
            
            logger.debug(f"Progress emitted via Redis for document {document_id}: {progress.stage}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to emit progress via Redis: {e}")
            return False

    def emit_progress_http(
        self, 
        document_id: str, 
        progress: ParseProgress
    ) -> bool:
        """
        Emit progress via HTTP API call to frontend.
        
        Args:
            document_id: Unique identifier for the document being processed
            progress: ParseProgress object containing progress information
            
        Returns:
            True if successful, False otherwise
        """
        if not REQUESTS_AVAILABLE:
            logger.debug(f"HTTP requests not available. Progress logged for document {document_id}: {progress.stage}")
            return True  # Consider it successful for development
            
        try:
            progress_data = {
                'documentId': document_id,
                'stage': self._map_stage_to_frontend(progress.stage),
                'progress': min(100, max(0, progress.progress * 100)),  # Convert to 0-100 range
                'message': progress.message
            }

            response = requests.post(
                f"{self.frontend_base_url}/api/progress",
                json=progress_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"Progress emitted via HTTP for document {document_id}: {progress.stage}")
                return True
            else:
                logger.warning(f"HTTP progress update failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to emit progress via HTTP: {e}")
            return False

    async def emit_progress(
        self, 
        document_id: str, 
        progress: ParseProgress
    ) -> bool:
        """
        Emit progress using the best available method (Redis preferred, HTTP fallback).
        
        Args:
            document_id: Unique identifier for the document being processed
            progress: ParseProgress object containing progress information
            
        Returns:
            True if successful, False otherwise
        """
        # Try Redis first
        if self.redis_client:
            success = await self.emit_progress_redis(document_id, progress)
            if success:
                return True

        # Fallback to HTTP
        return self.emit_progress_http(document_id, progress)

    def _map_stage_to_frontend(self, backend_stage: str) -> str:
        """
        Map backend stage names to frontend stage names.
        
        Args:
            backend_stage: Stage name from backend processing
            
        Returns:
            Mapped stage name for frontend
        """
        stage_mapping = {
            'initialization': 'uploading',
            'parsing': 'parsing',
            'ai_processing': 'converting',
            'markdown_generation': 'converting',
            'completion': 'complete',
            'error': 'error'
        }
        
        return stage_mapping.get(backend_stage, 'parsing')

    async def close(self):
        """Clean up resources."""
        if self.redis_client:
            await self.redis_client.close()


# Global instance for easy access
_progress_emitter: Optional[ProgressEmitter] = None

async def get_progress_emitter() -> ProgressEmitter:
    """Get or create the global progress emitter instance."""
    global _progress_emitter
    if _progress_emitter is None:
        _progress_emitter = ProgressEmitter()
        await _progress_emitter.initialize_redis()
    return _progress_emitter

async def emit_document_progress(document_id: str, progress: ParseProgress) -> bool:
    """
    Convenience function to emit progress for a document.
    
    Args:
        document_id: Unique identifier for the document
        progress: ParseProgress object
        
    Returns:
        True if successful, False otherwise
    """
    emitter = await get_progress_emitter()
    return await emitter.emit_progress(document_id, progress)
