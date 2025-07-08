import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { documentId, stage, progress, message } = await request.json();

    // Validate required fields
    if (!documentId || !stage || typeof progress !== 'number' || !message) {
      return NextResponse.json(
        { error: 'Missing required fields: documentId, stage, progress, message' },
        { status: 400 }
      );
    }

    // Validate stage values
    const validStages = ['uploading', 'parsing', 'converting', 'complete'];
    if (!validStages.includes(stage)) {
      return NextResponse.json(
        { error: 'Invalid stage. Must be one of: uploading, parsing, converting, complete' },
        { status: 400 }
      );
    }

    // Validate progress range
    if (progress < 0 || progress > 100) {
      return NextResponse.json(
        { error: 'Progress must be between 0 and 100' },
        { status: 400 }
      );
    }

    // Get the global socketServer instance
    const socketServer = global.socketServer;

    if (!socketServer) {
      return NextResponse.json(
        { error: 'Socket.IO server not initialized' },
        { status: 500 }
      );
    }

    // Emit progress event directly
    socketServer.emitDirectProgress(documentId, stage, progress, message);

    return NextResponse.json({ 
      success: true, 
      message: 'Progress updated successfully' 
    });
  } catch (error) {
    console.error('Error updating progress:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
