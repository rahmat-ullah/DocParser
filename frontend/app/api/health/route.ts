import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { readdir } from 'fs/promises';
import { join } from 'path';
import type { ApiResponse } from '@/types/api';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  version: string;
  services: {
    database: ServiceHealth;
    storage: ServiceHealth;
    ai: ServiceHealth;
    processing: ServiceHealth;
  };
  metrics: {
    memoryUsage: NodeJS.MemoryUsage;
    requestCount: number;
    averageResponseTime: number;
    errorRate: number;
  };
  system: {
    nodeVersion: string;
    platform: string;
    arch: string;
    cpuUsage: number;
  };
}

interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency?: number;
  lastCheck: string;
  message?: string;
}

// Simple in-memory metrics store (in production, use proper metrics collection)
const metrics = {
  requestCount: 0,
  totalResponseTime: 0,
  errors: 0,
  startTime: Date.now()
};

async function checkDatabaseHealth(): Promise<ServiceHealth> {
  // Mock database health check
  // In production, this would ping your actual database
  const startTime = Date.now();
  
  try {
    // Simulate database query
    await new Promise(resolve => setTimeout(resolve, Math.random() * 10));
    
    return {
      status: 'healthy',
      latency: Date.now() - startTime,
      lastCheck: new Date().toISOString(),
      message: 'Mock database connection successful'
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      message: error instanceof Error ? error.message : 'Database connection failed'
    };
  }
}

async function checkStorageHealth(): Promise<ServiceHealth> {
  // Check if temp directory is accessible
  const startTime = Date.now();
  
  try {
    const tempDir = join(process.cwd(), 'temp');
    await readdir(tempDir).catch(async () => {
      // Directory doesn't exist, try to create it
      await require('fs/promises').mkdir(tempDir, { recursive: true });
    });
    
    return {
      status: 'healthy',
      latency: Date.now() - startTime,
      lastCheck: new Date().toISOString(),
      message: 'File system accessible'
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      message: error instanceof Error ? error.message : 'File system not accessible'
    };
  }
}

async function checkAIServiceHealth(): Promise<ServiceHealth> {
  // Mock AI service health check
  // In production, this would check OpenAI API availability
  const startTime = Date.now();
  
  try {
    // Simulate AI service ping
    await new Promise(resolve => setTimeout(resolve, Math.random() * 50));
    
    const hasApiKey = process.env.OPENAI_API_KEY !== undefined;
    
    return {
      status: hasApiKey ? 'healthy' : 'degraded',
      latency: Date.now() - startTime,
      lastCheck: new Date().toISOString(),
      message: hasApiKey ? 'AI service available' : 'AI service available but API key not configured'
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      message: error instanceof Error ? error.message : 'AI service unavailable'
    };
  }
}

async function checkProcessingServiceHealth(): Promise<ServiceHealth> {
  // Mock document processing service health
  const startTime = Date.now();
  
  try {
    // Simulate processing service check
    await new Promise(resolve => setTimeout(resolve, Math.random() * 20));
    
    return {
      status: 'healthy',
      latency: Date.now() - startTime,
      lastCheck: new Date().toISOString(),
      message: 'Document processing service operational'
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      message: error instanceof Error ? error.message : 'Processing service unavailable'
    };
  }
}

function getCPUUsage(): number {
  // Simple CPU usage estimation
  const startTime = process.hrtime();
  const startUsage = process.cpuUsage();
  
  // Busy wait for 10ms
  while (process.hrtime(startTime)[1] < 10000000) {
    // Busy wait
  }
  
  const endUsage = process.cpuUsage(startUsage);
  const totalTime = endUsage.user + endUsage.system;
  
  // Return CPU usage as percentage (rough estimation)
  return Math.min(Math.round((totalTime / 10000) * 100) / 100, 100);
}

export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<HealthStatus>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  const startTime = Date.now();
  
  try {
    // Update request metrics
    metrics.requestCount++;
    
    // Check all services in parallel
    const [databaseHealth, storageHealth, aiHealth, processingHealth] = await Promise.all([
      checkDatabaseHealth(),
      checkStorageHealth(),
      checkAIServiceHealth(),
      checkProcessingServiceHealth()
    ]);

    // Determine overall status
    const allServices = [databaseHealth, storageHealth, aiHealth, processingHealth];
    const unhealthyServices = allServices.filter(service => service.status === 'unhealthy');
    const degradedServices = allServices.filter(service => service.status === 'degraded');
    
    let overallStatus: 'healthy' | 'degraded' | 'unhealthy';
    if (unhealthyServices.length > 0) {
      overallStatus = 'unhealthy';
    } else if (degradedServices.length > 0) {
      overallStatus = 'degraded';
    } else {
      overallStatus = 'healthy';
    }

    // Calculate metrics
    const processingTime = Date.now() - startTime;
    metrics.totalResponseTime += processingTime;
    
    const uptime = Date.now() - metrics.startTime;
    const averageResponseTime = metrics.totalResponseTime / metrics.requestCount;
    const errorRate = (metrics.errors / metrics.requestCount) * 100;

    // Get system information
    const memoryUsage = process.memoryUsage();
    const cpuUsage = getCPUUsage();

    const healthStatus: HealthStatus = {
      status: overallStatus,
      timestamp,
      uptime,
      version: process.env.npm_package_version || '1.0.0',
      services: {
        database: databaseHealth,
        storage: storageHealth,
        ai: aiHealth,
        processing: processingHealth
      },
      metrics: {
        memoryUsage,
        requestCount: metrics.requestCount,
        averageResponseTime: Math.round(averageResponseTime * 100) / 100,
        errorRate: Math.round(errorRate * 100) / 100
      },
      system: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        cpuUsage
      }
    };

    // Set appropriate HTTP status code based on health
    const httpStatus = overallStatus === 'healthy' ? 200 : 
                      overallStatus === 'degraded' ? 200 : 503;

    return NextResponse.json({
      success: overallStatus !== 'unhealthy',
      data: healthStatus,
      metadata: {
        timestamp,
        requestId,
        processingTime
      }
    }, { status: httpStatus });

  } catch (error) {
    console.error('Health check error:', error);
    metrics.errors++;
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'HEALTH_CHECK_ERROR',
        message: 'Failed to perform health check.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
}

// POST /api/health - Reset metrics (admin only)
export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<{ message: string }>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    // In production, add authentication check here
    const body = await request.json();
    const action = body.action;

    if (action === 'reset-metrics') {
      metrics.requestCount = 0;
      metrics.totalResponseTime = 0;
      metrics.errors = 0;
      metrics.startTime = Date.now();

      return NextResponse.json({
        success: true,
        data: {
          message: 'Metrics have been reset successfully.'
        },
        metadata: {
          timestamp,
          requestId,
          processingTime: Date.now() - new Date(timestamp).getTime()
        }
      });
    } else {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INVALID_ACTION',
          message: 'Invalid action. Supported actions: reset-metrics',
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

  } catch (error) {
    console.error('Health action error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'HEALTH_ACTION_ERROR',
        message: 'Failed to perform health action.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
} 