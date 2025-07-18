#!/usr/bin/env python3
"""
Comprehensive workflow test script to trace document processing
and verify enhanced AI service usage with detailed logging.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_processor import DocumentProcessor
from app.services.enhanced_ai_service import get_enhanced_ai_service
from app.parsers.parser_factory import ParserFactory
from app.core.config import settings

class WorkflowLogger:
    """Enhanced logging for workflow tracking."""
    
    def __init__(self):
        self.log_entries = []
        self.start_time = datetime.now()
        
    def log(self, stage: str, message: str, details: dict = None):
        """Log a workflow step with timestamp."""
        timestamp = datetime.now()
        elapsed = (timestamp - self.start_time).total_seconds()
        
        entry = {
            "timestamp": timestamp.isoformat(),
            "elapsed_seconds": elapsed,
            "stage": stage,
            "message": message,
            "details": details or {}
        }
        
        self.log_entries.append(entry)
        print(f"[{elapsed:6.2f}s] {stage}: {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()
        
    def save_log(self, filepath: str):
        """Save the complete log to a file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.log_entries, f, indent=2, default=str)
        print(f"Complete workflow log saved to: {filepath}")

async def test_enhanced_ai_service():
    """Test the enhanced AI service directly."""
    logger = WorkflowLogger()
    
    try:
        logger.log("AI_SERVICE_TEST", "Testing enhanced AI service connection")
        
        # Get enhanced AI service
        ai_service = await get_enhanced_ai_service()
        logger.log("AI_SERVICE_INIT", "Enhanced AI service initialized", {
            "service_type": type(ai_service).__name__,
            "has_analyze_image_with_context": hasattr(ai_service, 'analyze_image_with_context'),
            "config_keys": list(ai_service.config.keys()) if hasattr(ai_service, 'config') else []
        })
        
        # Test health check
        health_status = await ai_service.health_check()
        logger.log("AI_SERVICE_HEALTH", "Health check completed", health_status)
        
        return ai_service, logger
        
    except Exception as e:
        logger.log("AI_SERVICE_ERROR", f"Enhanced AI service test failed: {e}")
        return None, logger

async def analyze_pdf_structure(pdf_path: str):
    """Analyze PDF structure and content."""
    logger = WorkflowLogger()
    
    try:
        logger.log("PDF_ANALYSIS_START", f"Analyzing PDF structure: {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.log("PDF_ERROR", f"PDF file not found: {pdf_path}")
            return None, logger
            
        file_size = os.path.getsize(pdf_path)
        logger.log("PDF_INFO", "PDF file found", {
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        })
        
        # Get parser
        parser_factory = ParserFactory()
        pdf_path_obj = Path(pdf_path)
        parser = parser_factory.get_parser(pdf_path_obj)
        
        logger.log("PARSER_INIT", "Parser initialized", {
            "parser_type": type(parser).__name__,
            "supported_extensions": parser_factory.get_supported_extensions()
        })
        
        # Parse the document
        logger.log("PARSING_START", "Starting document parsing")
        ast = await parser.parse(pdf_path_obj)
        
        logger.log("PARSING_COMPLETE", "Document parsing completed", {
            "text_blocks": len(ast.textBlocks),
            "images": len(ast.images),
            "tables": len(ast.tables),
            "math_blocks": len(ast.math),
            "metadata_keys": list(ast.metadata.keys()) if ast.metadata else []
        })
        
        # Analyze images in detail
        if ast.images:
            logger.log("IMAGE_ANALYSIS", f"Found {len(ast.images)} images")
            for i, image in enumerate(ast.images):
                image_details = {
                    "index": i,
                    "page": getattr(image, 'page', 'unknown'),
                    "has_data": bool(getattr(image, 'data', None)),
                    "data_length": len(getattr(image, 'data', '')) if getattr(image, 'data', None) else 0,
                    "alt_text": getattr(image, 'alt_text', 'none'),
                    "has_bbox": bool(getattr(image, 'bbox', None)),
                    "bbox": getattr(image, 'bbox', None)
                }
                logger.log(f"IMAGE_{i}", f"Image {i} details", image_details)
        else:
            logger.log("IMAGE_ANALYSIS", "No images found in document")
            
        return ast, logger
        
    except Exception as e:
        logger.log("PDF_ANALYSIS_ERROR", f"PDF analysis failed: {e}")
        return None, logger

async def test_enhanced_processing(pdf_path: str):
    """Test the complete enhanced processing workflow."""
    logger = WorkflowLogger()
    
    try:
        logger.log("WORKFLOW_START", f"Starting enhanced processing workflow for: {pdf_path}")
        
        # Test AI service first
        ai_service, ai_logger = await test_enhanced_ai_service()
        logger.log_entries.extend(ai_logger.log_entries)
        
        if not ai_service:
            logger.log("WORKFLOW_ABORT", "AI service not available, aborting workflow")
            return logger
            
        # Analyze PDF structure
        ast, pdf_logger = await analyze_pdf_structure(pdf_path)
        logger.log_entries.extend(pdf_logger.log_entries)
        
        if not ast:
            logger.log("WORKFLOW_ABORT", "PDF parsing failed, aborting workflow")
            return logger
            
        # Check logs directory
        logs_dir = Path("logs")
        log_files_before = list(logs_dir.glob("*.log")) if logs_dir.exists() else []
        logger.log("LOGS_CHECK_BEFORE", f"Log files before processing: {len(log_files_before)}")
        
        # Process with enhanced AI
        logger.log("ENHANCED_PROCESSING_START", "Starting enhanced AI processing")
        document_processor = DocumentProcessor()
        
        # Process the document
        pdf_path_obj = Path(pdf_path)
        doc_id = "test_workflow_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        
        progress_count = 0
        async for progress in document_processor.process_document(pdf_path_obj, doc_id, enable_ai_processing=True):
            progress_count += 1
            logger.log("PROGRESS", f"Processing step {progress_count}", {
                "stage": progress.stage,
                "progress": f"{progress.progress:.1%}",
                "message": progress.message,
                "details": progress.details
            })
            
            # Check for completion
            if progress.stage == "completion":
                if hasattr(progress, 'result'):
                    result_length = len(progress.result) if progress.result else 0
                    logger.log("COMPLETION", "Processing completed successfully", {
                        "result_length": result_length,
                        "markdown_path": progress.details.get("markdown_path", "none")
                    })
                break
        
        # Check logs directory after processing
        log_files_after = list(logs_dir.glob("*.log")) if logs_dir.exists() else []
        new_log_files = [f for f in log_files_after if f not in log_files_before]
        
        logger.log("LOGS_CHECK_AFTER", f"Log files after processing", {
            "total_log_files": len(log_files_after),
            "new_log_files": len(new_log_files),
            "new_files": [f.name for f in new_log_files]
        })
        
        # Analyze new log files
        for log_file in new_log_files:
            try:
                content = log_file.read_text(encoding='utf-8')
                logger.log("LLM_LOG_FOUND", f"LLM log file analysis", {
                    "filename": log_file.name,
                    "size_bytes": len(content),
                    "lines": len(content.split('\n')),
                    "contains_model": "Model:" in content,
                    "contains_response": "Response:" in content,
                    "first_100_chars": content[:100] + "..." if len(content) > 100 else content
                })
            except Exception as e:
                logger.log("LLM_LOG_ERROR", f"Error reading log file {log_file.name}: {e}")
        
        return logger
        
    except Exception as e:
        logger.log("WORKFLOW_ERROR", f"Workflow failed: {e}")
        return logger

async def main():
    """Main test function."""
    pdf_path = r"C:\Users\User\Downloads\Test.pdf"
    
    print("=" * 80)
    print("ENHANCED AI SERVICE WORKFLOW TEST")
    print("=" * 80)
    print(f"Testing with PDF: {pdf_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Settings: AI batch size = {getattr(settings, 'ai_processor_image_batch_size', 'not set')}")
    print("=" * 80)
    print()
    
    # Run the enhanced processing test
    logger = await test_enhanced_processing(pdf_path)
    
    # Save the workflow log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filepath = f"workflow_test_{timestamp}.json"
    logger.save_log(log_filepath)
    
    print("=" * 80)
    print("WORKFLOW TEST COMPLETED")
    print("=" * 80)
    print(f"Total workflow steps: {len(logger.log_entries)}")
    print(f"Total elapsed time: {(datetime.now() - logger.start_time).total_seconds():.2f} seconds")
    print(f"Detailed log saved to: {log_filepath}")
    
    # Summary of findings
    print("\nSUMMARY:")
    
    # Check if AI service was initialized
    ai_init_logs = [entry for entry in logger.log_entries if entry['stage'] == 'AI_SERVICE_INIT']
    if ai_init_logs:
        print("✅ Enhanced AI service initialized successfully")
    else:
        print("❌ Enhanced AI service failed to initialize")
    
    # Check if images were found
    image_logs = [entry for entry in logger.log_entries if 'IMAGE' in entry['stage']]
    if image_logs:
        print(f"✅ Found images in document (logged {len(image_logs)} image-related entries)")
    else:
        print("❌ No images found in document")
    
    # Check if LLM logs were created
    llm_log_entries = [entry for entry in logger.log_entries if entry['stage'] == 'LLM_LOG_FOUND']
    if llm_log_entries:
        print(f"✅ LLM response logs created ({len(llm_log_entries)} files)")
    else:
        print("❌ No LLM response logs found")
    
    # Check if processing completed
    completion_logs = [entry for entry in logger.log_entries if entry['stage'] == 'COMPLETION']
    if completion_logs:
        print("✅ Document processing completed successfully")
    else:
        print("❌ Document processing did not complete")

if __name__ == "__main__":
    asyncio.run(main())
