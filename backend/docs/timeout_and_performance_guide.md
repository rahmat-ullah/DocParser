# Timeout and Performance Guide

## Overview

This guide explains the timeout handling and performance optimizations implemented in the DocParser application to prevent processing timeouts and improve user experience.

## Timeout Issues Fixed

### Frontend Timeout
- **Previous**: 60-second timeout (60 attempts × 1 second)
- **Current**: 5-minute timeout (300 attempts × 1 second)
- **Reason**: Table extraction with OCR and LLM can take longer than 60 seconds

### Backend Optimizations
- **Async OCR Processing**: OCR operations now run in executor to prevent blocking
- **Configurable Timeouts**: OpenAI API calls use configurable timeout settings
- **Batch Processing**: Images are processed in configurable batches
- **Graceful Fallbacks**: Processing continues even if table extraction fails

## Configuration Settings

### Table Extraction Control
```python
# In app/core/config.py
extract_tables_from_images_enabled: bool = False  # Disabled by default for faster processing
```

**To enable table extraction:**
1. Set environment variable: `EXTRACT_TABLES_FROM_IMAGES_ENABLED=true`
2. Or modify config.py: `extract_tables_from_images_enabled: bool = True`

### Performance Settings
```python
# OpenAI settings
openai_timeout: int = 30  # 30 seconds timeout for API calls
openai_max_retries: int = 3  # Retry failed API calls
ai_processor_image_batch_size: int = 3  # Process 3 images concurrently
```

## Processing Flow

### Fast Mode (Default)
1. **Document Upload**: File uploaded to server
2. **Basic Parsing**: Extract text, images, basic tables
3. **AI Enhancement**: Generate image descriptions (if images present)
4. **Markdown Generation**: Create markdown output
5. **Completion**: Return results to frontend

**Typical Time**: 10-30 seconds

### Full Table Extraction Mode
1. **Document Upload**: File uploaded to server
2. **Basic Parsing**: Extract text, images, basic tables
3. **OCR Processing**: Extract text from images using Tesseract
4. **LLM Analysis**: Use OpenAI to identify and format tables
5. **AI Enhancement**: Generate image descriptions
6. **Markdown Generation**: Create markdown with extracted tables
7. **Completion**: Return results to frontend

**Typical Time**: 30-180 seconds (depending on number of images)

## Error Handling

### Timeout Scenarios
- **OCR Timeout**: If Tesseract takes too long, processing continues without table extraction
- **LLM Timeout**: If OpenAI API times out, table extraction is skipped
- **Overall Timeout**: If processing takes longer than 5 minutes, frontend shows timeout error

### Fallback Behavior
- **Table Extraction Fails**: Document processing continues, tables are skipped
- **AI Processing Fails**: Basic parsing results are still returned
- **Partial Failures**: Document is processed with available content

## Troubleshooting

### Common Issues

1. **Processing Timeout**
   - **Cause**: Large documents with many images
   - **Solution**: Enable table extraction only when needed, or process smaller documents

2. **OCR Not Working**
   - **Cause**: Tesseract not installed or not in PATH
   - **Solution**: Install Tesseract or disable table extraction

3. **OpenAI API Errors**
   - **Cause**: Invalid API key or rate limits
   - **Solution**: Check API key configuration and usage limits

### Performance Tips

1. **For Fast Processing**:
   - Keep `extract_tables_from_images_enabled = False`
   - Use smaller image files
   - Process documents with fewer images

2. **For Table Extraction**:
   - Enable table extraction only when needed
   - Use high-quality images for better OCR results
   - Ensure OpenAI API key is configured

3. **For Large Documents**:
   - Consider splitting large documents
   - Process during off-peak hours
   - Monitor API usage limits

## Monitoring

### Progress Tracking
The application provides real-time progress updates:
- **Upload**: 0-20%
- **Parsing**: 20-40%
- **AI Processing**: 40-80%
- **Markdown Generation**: 80-90%
- **Completion**: 90-100%

### Logging
Check logs for detailed processing information:
- OCR processing times
- API call durations
- Error messages and fallbacks

## Configuration Examples

### Development Environment
```python
# Fast processing for development
extract_tables_from_images_enabled = False
openai_timeout = 10
ai_processor_image_batch_size = 1
```

### Production Environment
```python
# Balanced performance for production
extract_tables_from_images_enabled = True
openai_timeout = 30
ai_processor_image_batch_size = 3
```

### High-Performance Environment
```python
# Maximum performance
extract_tables_from_images_enabled = True
openai_timeout = 60
ai_processor_image_batch_size = 5
openai_max_retries = 5
```

## Summary

The timeout and performance optimizations ensure that:
- ✅ Documents process reliably without timeouts
- ✅ Table extraction is optional and configurable
- ✅ Processing continues even if some steps fail
- ✅ Users get feedback on processing progress
- ✅ Performance can be tuned for different environments

The default configuration prioritizes speed over table extraction, but users can enable full table extraction when needed. 