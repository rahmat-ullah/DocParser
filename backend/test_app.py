#!/usr/bin/env python3
"""
Minimal FastAPI app for testing the document processing SSE endpoint.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from app.api.v1.endpoints.processing import router as processing_router

app = FastAPI(title="Document Parser Test API")

# Include the processing router
app.include_router(processing_router, prefix="/api/v1/processing")

@app.get("/", response_class=HTMLResponse)
async def test_page():
    """Test page with SSE client."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Parser SSE Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #progress { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
            .progress-item { margin: 5px 0; padding: 5px; background: #f0f0f0; }
            .error { background: #ffcccc; }
            .complete { background: #ccffcc; }
        </style>
    </head>
    <body>
        <h1>Document Parser SSE Test</h1>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div>
                <label>Select document:</label>
                <input type="file" id="fileInput" accept=".txt,.md,.pdf,.docx" required>
            </div>
            <div>
                <label>
                    <input type="checkbox" id="aiProcessing" checked>
                    Enable AI Processing
                </label>
            </div>
            <button type="submit">Process Document</button>
        </form>
        
        <h2>Progress:</h2>
        <div id="progress"></div>
        
        <h2>Result:</h2>
        <pre id="result"></pre>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const fileInput = document.getElementById('fileInput');
                const aiProcessing = document.getElementById('aiProcessing').checked;
                const progressDiv = document.getElementById('progress');
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('Please select a file');
                    return;
                }
                
                // Clear previous results
                progressDiv.innerHTML = '';
                resultDiv.textContent = '';
                
                // Create form data
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                try {
                    // Send POST request and handle SSE response
                    const response = await fetch(`/api/v1/processing/process?enable_ai_processing=${aiProcessing}`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    const progressItem = document.createElement('div');
                                    progressItem.className = 'progress-item';
                                    progressItem.textContent = `[${data.stage}] ${(data.progress * 100).toFixed(0)}% - ${data.message}`;
                                    progressDiv.appendChild(progressItem);
                                    progressDiv.scrollTop = progressDiv.scrollHeight;
                                    
                                    // Handle final result
                                    if (data.markdown) {
                                        resultDiv.textContent = data.markdown;
                                    }
                                } catch (e) {
                                    console.error('Error parsing SSE data:', e);
                                }
                            } else if (line.startsWith('event: ')) {
                                const event = line.slice(7);
                                if (event === 'error') {
                                    const progressItem = document.createElement('div');
                                    progressItem.className = 'progress-item error';
                                    progressItem.textContent = 'ERROR occurred';
                                    progressDiv.appendChild(progressItem);
                                } else if (event === 'complete') {
                                    const progressItem = document.createElement('div');
                                    progressItem.className = 'progress-item complete';
                                    progressItem.textContent = 'PROCESSING COMPLETE';
                                    progressDiv.appendChild(progressItem);
                                }
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error:', error);
                    const progressItem = document.createElement('div');
                    progressItem.className = 'progress-item error';
                    progressItem.textContent = `Error: ${error.message}`;
                    progressDiv.appendChild(progressItem);
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
