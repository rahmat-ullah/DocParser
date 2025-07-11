"""
Socket.IO implementation for real-time communication.
Provides WebSocket support for progress events and real-time updates.
"""

import logging
from typing import Dict, Any, Optional

import socketio
from fastapi import FastAPI
from socketio import AsyncServer

from app.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

# Create Socket.IO server
sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*" if settings.debug else [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://yourdomain.com"
    ],
    logger=settings.debug,
    engineio_logger=settings.debug
)

# Store active connections
active_connections: Dict[str, Dict[str, Any]] = {}


@sio.event
async def connect(sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]] = None):
    """
    Handle client connection.
    """
    logger.info(f"Client connected: {sid}")
    
    # Store connection info
    active_connections[sid] = {
        "connected_at": None,
        "user_id": auth.get("user_id") if auth else None,
        "session_data": {}
    }
    
    # Send welcome message
    await sio.emit("connected", {"message": "Connected to Document Parser"}, room=sid)
    
    # Send current status
    await sio.emit("status", {"status": "ready", "message": "Ready to process documents"}, room=sid)


@sio.event
async def disconnect(sid: str):
    """
    Handle client disconnection.
    """
    logger.info(f"Client disconnected: {sid}")
    
    # Remove connection from active connections
    if sid in active_connections:
        del active_connections[sid]


@sio.event
async def ping(sid: str, data: Dict[str, Any]):
    """
    Handle ping from client.
    """
    await sio.emit("pong", {"timestamp": data.get("timestamp")}, room=sid)


@sio.event
async def join_room(sid: str, data: Dict[str, Any]):
    """
    Handle client joining a room (e.g., for document processing session).
    """
    room = data.get("room")
    if room:
        await sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room {room}")
        await sio.emit("joined_room", {"room": room}, room=sid)


@sio.event
async def leave_room(sid: str, data: Dict[str, Any]):
    """
    Handle client leaving a room.
    """
    room = data.get("room")
    if room:
        await sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room {room}")
        await sio.emit("left_room", {"room": room}, room=sid)


# Progress event functions
async def emit_progress(
    session_id: str,
    progress: float,
    message: str,
    stage: str = "processing",
    data: Optional[Dict[str, Any]] = None
):
    """
    Emit progress event to a specific session.
    
    Args:
        session_id: The session/room ID
        progress: Progress percentage (0-100)
        message: Progress message
        stage: Processing stage
        data: Additional data
    """
    progress_data = {
        "progress": progress,
        "message": message,
        "stage": stage,
        "timestamp": None,
        "data": data or {}
    }
    
    await sio.emit("progress", progress_data, room=session_id)
    logger.debug(f"Progress emitted to {session_id}: {progress}% - {message}")


async def emit_status(
    session_id: str,
    status: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
):
    """
    Emit status update to a specific session.
    
    Args:
        session_id: The session/room ID
        status: Status (success, error, processing, etc.)
        message: Status message
        data: Additional data
    """
    status_data = {
        "status": status,
        "message": message,
        "timestamp": None,
        "data": data or {}
    }
    
    await sio.emit("status", status_data, room=session_id)
    logger.debug(f"Status emitted to {session_id}: {status} - {message}")


async def emit_error(
    session_id: str,
    error: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
):
    """
    Emit error event to a specific session.
    
    Args:
        session_id: The session/room ID
        error: Error type/code
        message: Error message
        data: Additional error data
    """
    error_data = {
        "error": error,
        "message": message,
        "timestamp": None,
        "data": data or {}
    }
    
    await sio.emit("error", error_data, room=session_id)
    logger.error(f"Error emitted to {session_id}: {error} - {message}")


async def emit_document_processed(
    session_id: str,
    document_id: str,
    result: Dict[str, Any]
):
    """
    Emit document processed event.
    
    Args:
        session_id: The session/room ID
        document_id: The processed document ID
        result: Processing result
    """
    event_data = {
        "document_id": document_id,
        "result": result,
        "timestamp": None
    }
    
    await sio.emit("document_processed", event_data, room=session_id)
    logger.info(f"Document processed event emitted to {session_id}: {document_id}")


async def emit_batch_update(
    session_id: str,
    batch_id: str,
    completed: int,
    total: int,
    current_document: Optional[str] = None
):
    """
    Emit batch processing update.
    
    Args:
        session_id: The session/room ID
        batch_id: The batch processing ID
        completed: Number of completed documents
        total: Total number of documents
        current_document: Currently processing document name
    """
    progress = (completed / total) * 100 if total > 0 else 0
    
    event_data = {
        "batch_id": batch_id,
        "completed": completed,
        "total": total,
        "progress": progress,
        "current_document": current_document,
        "timestamp": None
    }
    
    await sio.emit("batch_update", event_data, room=session_id)
    logger.debug(f"Batch update emitted to {session_id}: {completed}/{total} documents")


# Utility functions
async def get_active_connections() -> Dict[str, Dict[str, Any]]:
    """Get all active connections."""
    return active_connections.copy()


async def is_client_connected(session_id: str) -> bool:
    """Check if a client is connected."""
    return session_id in active_connections


async def broadcast_to_all(event: str, data: Dict[str, Any]):
    """Broadcast an event to all connected clients."""
    await sio.emit(event, data)
    logger.debug(f"Broadcasted {event} to all clients")


# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio)


def mount_socketio(app: FastAPI):
    """
    Mount Socket.IO to FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.mount("/ws", socket_app)
    logger.info("Socket.IO mounted at /ws")
