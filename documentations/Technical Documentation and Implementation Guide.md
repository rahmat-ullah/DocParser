# Technical Documentation and Implementation Guide

This document provides a technical deep-dive into the implementation details of the Document Parsing Web Application. It serves as a guide for developers, covering environment setup, project structure, and detailed explanations of core functionalities.

## 1. Development Environment Setup

To set up the development environment, ensure you have the following prerequisites installed:

*   **Node.js (LTS version):** Required for Next.js and frontend development.
*   **Python 3.9+:** Required for the Document Processing Service.
*   **Git:** For version control.
*   **Docker (Optional but Recommended):** For containerizing the Document Processing Service and ensuring consistent environments.

### 1.1. Frontend Setup (Next.js)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd document-parser-app/frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    # or yarn install
    ```
3.  **Environment Variables:** Create a `.env.local` file in the `frontend` directory and add the following:
    ```
    NEXT_PUBLIC_BACKEND_URL=http://localhost:3001/api
    ```
    (Adjust the URL if your backend runs on a different port or domain.)
4.  **Run the development server:**
    ```bash
    npm run dev
    # or yarn dev
    ```
    The frontend application will be accessible at `http://localhost:3000`.

### 1.2. Backend Setup (Next.js API Routes)

The backend API routes are part of the Next.js application. No separate setup is required beyond the frontend setup.

### 1.3. Document Processing Service Setup (Flask/Python)

1.  **Navigate to the service directory:**
    ```bash
    cd document-parser-app/backend/document-processor
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (The `requirements.txt` file will contain entries for `Flask`, `PyMuPDF`, `python-docx`, `openpyxl`, `python-pptx`, `Pillow`, `openai`, `latexify-py`, etc.)
4.  **Environment Variables:** Create a `.env` file in the `document-processor` directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
5.  **Run the Flask application:**
    ```bash
    flask run --port 5000
    ```
    The document processing service will run on `http://localhost:5000`.

## 2. Project Structure

```
document-parser-app/
├── frontend/                  # Next.js application
│   ├── public/
│   ├── src/
│   │   ├── app/               # Next.js App Router (pages, layouts, API routes)
│   │   │   ├── api/           # Backend API routes
│   │   │   │   ├── upload/route.ts
│   │   │   │   └── process/route.ts
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/        # Reusable React components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── FileUpload.tsx
│   │   │   ├── DocumentViewer.tsx
│   │   │   ├── MarkdownEditor.tsx
│   │   │   ├── HistorySidebar.tsx
│   │   │   └── ...
│   │   ├── lib/               # Utility functions, hooks, state management
│   │   │   ├── store.ts       # Zustand store
│   │   │   ├── utils.ts
│   │   │   └── ...
│   │   └── styles/            # Tailwind CSS configuration
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
└── backend/
    └── document-processor/    # Flask/Python Document Processing Service
        ├── app.py             # Flask application entry point
        ├── parsers/           # Modules for different file type parsers
        │   ├── pdf_parser.py
        │   ├── docx_parser.py
        │   ├── xlsx_parser.py
        │   ├── pptx_parser.py
        │   ├── txt_parser.py
        │   ├── image_parser.py
        │   └── __init__.py
        ├── utils/             # Utility functions for AI, math, tables
        │   ├── openai_vision.py
        │   ├── math_converter.py
        │   ├── table_extractor.py
        │   └── __init__.py
        ├── requirements.txt
        └── .env
```

## 3. Core Feature Implementation Details

### 3.1. File Upload Functionality

**Frontend (`frontend/src/components/FileUpload.tsx`):**

*   Utilize `react-dropzone` to create the drag-and-drop area. This component simplifies handling file selection and drag events.
*   Implement client-side validation for file types and sizes before uploading. Display immediate feedback to the user for invalid files.
*   Use `useState` and `useEffect` hooks to manage upload state (e.g., `isUploading`, `uploadProgress`).
*   When a file is selected, initiate an API call to the Next.js API route (`/api/upload`).

```typescript
// frontend/src/components/FileUpload.tsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      setError('No files selected or file type not supported.');
      return;
    }

    const file = acceptedFiles[0];
    setError(null);
    setUploading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('document', file);

    try {
      // Simulate upload progress (replace with actual upload logic)
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setProgress(i);
      }

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Upload successful:', data);
      // Trigger document processing or update state

    } catch (err: any) {
      setError(err.message);
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpeg', '.jpg'],
    },
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed p-8 text-center cursor-pointer
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}`}
    >
      <input {...getInputProps()} />
      {
        isDragActive ?
          <p>Drop the files here ...</p> :
          <p>Drag 'n' drop a document here, or click to select one</p>
      }
      {uploading && <p>Uploading: {progress}%</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
    </div>
  );
};

export default FileUpload;
```

**Backend (Next.js API Route - `frontend/src/app/api/upload/route.ts`):**

*   Handle the incoming `multipart/form-data` request.
*   Temporarily save the uploaded file to a designated directory on the server.
*   Initiate the document processing by making an HTTP request to the Python Flask service.
*   Return a response to the frontend indicating success or failure.

```typescript
// frontend/src/app/api/upload/route.ts
import { NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import path from 'path';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('document') as File | null;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded.' }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const filename = Date.now() + '-' + file.name.replace(/ /g, '_');
    const tempFilePath = path.join(process.cwd(), 'tmp', filename);

    // Ensure the 'tmp' directory exists
    await require('fs/promises').mkdir(path.join(process.cwd(), 'tmp'), { recursive: true });
    await writeFile(tempFilePath, buffer);

    console.log(`File saved temporarily at: ${tempFilePath}`);

    // TODO: Send file to Python Document Processing Service
    // For now, simulate a response
    const simulatedProcessingResult = {
      markdown: `# Document: ${file.name}\n\nThis is a simulated markdown conversion.`, 
      json: { fileName: file.name, type: file.type, size: file.size },
    };

    return NextResponse.json({
      message: 'File uploaded and processing initiated (simulated).',
      data: simulatedProcessingResult,
    });

  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json({ error: 'Failed to upload file.' }, { status: 500 });
  }
}
```

**Document Processing Service (Flask/Python - `backend/document-processor/app.py`):**

*   Set up a Flask endpoint to receive file uploads from the Next.js backend.
*   Use `request.files` to access the uploaded file.
*   Dispatch the file to the appropriate parser based on its MIME type or extension.

```python
# backend/document-processor/app.py
from flask import Flask, request, jsonify
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from parsers.xlsx_parser import parse_xlsx
from parsers.pptx_parser import parse_pptx
from parsers.txt_parser import parse_txt
from parsers.image_parser import parse_image
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_document():
    if 'document' not in request.files:
        return jsonify({'error': 'No document file provided'}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_extension = os.path.splitext(file.filename)[1].lower()
    
    markdown_content = ""
    json_content = {}

    try:
        if file_extension == '.pdf':
            markdown_content, json_content = parse_pdf(file)
        elif file_extension == '.docx':
            markdown_content, json_content = parse_docx(file)
        elif file_extension == '.xlsx':
            markdown_content, json_content = parse_xlsx(file)
        elif file_extension == '.pptx':
            markdown_content, json_content = parse_pptx(file)
        elif file_extension == '.txt':
            markdown_content, json_content = parse_txt(file)
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            markdown_content, json_content = parse_image(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_extension}'}), 400

        return jsonify({
            'markdown': markdown_content,
            'json': json_content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

### 3.2. Document Parsing Libraries (Python)

This section details the usage of various Python libraries for parsing different document formats. Each parser will return a tuple of `(markdown_string, json_object)`.

**`backend/document-processor/parsers/pdf_parser.py`:**

```python
import fitz  # PyMuPDF
from utils.openai_vision import describe_image
from utils.table_extractor import extract_table_from_pdf
from utils.math_converter import convert_math_to_latex
import io

def parse_pdf(file_stream):
    markdown_output = []
    json_output = {"pages": []}

    doc = fitz.open(stream=file_stream.read(), filetype="pdf")

    for page_num, page in enumerate(doc):
        page_text = page.get_text("text")
        markdown_output.append(f"\n## Page {page_num + 1}\n")
        markdown_output.append(page_text)
        json_output["pages"].append({"page_number": page_num + 1, "text": page_text})

        # Extract images
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Simulate saving image for Vision API (in real app, send bytes directly)
            # For simplicity, we'll just describe the image bytes directly
            description = describe_image(image_bytes, image_ext)
            markdown_output.append(f"\n![Image {img_index + 1}: {description}](embedded_image_{page_num}_{img_index}.{image_ext})\n")
            json_output["pages"][page_num].setdefault("images", []).append({"index": img_index + 1, "description": description, "extension": image_ext})

        # TODO: Implement robust table and math extraction for PDF
        # For now, a placeholder for table extraction
        # tables = extract_table_from_pdf(page)
        # for table_md in tables:
        #     markdown_output.append(f"\n{table_md}\n")

        # For now, a placeholder for math extraction
        # math_equations = find_math_in_pdf(page_text) # This would be complex
        # for math_eq in math_equations:
        #     latex_eq = convert_math_to_latex(math_eq)
        #     markdown_output.append(f"\n$$\n{latex_eq}\n$$\n")

    return "\n".join(markdown_output), json_output
```

**`backend/document-processor/parsers/docx_parser.py`:**

```python
from docx import Document
from utils.openai_vision import describe_image
from utils.table_extractor import extract_table_from_docx
import io

def parse_docx(file_stream):
    markdown_output = []
    json_output = {"content": []}

    document = Document(file_stream)

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            # Basic markdown formatting for paragraphs
            if paragraph.style.name.startswith('Heading'):
                level = int(paragraph.style.name.replace('Heading ', ''))
                markdown_output.append(f"{'#' * level} {text}\n")
            else:
                markdown_output.append(f"{text}\n")
            json_output["content"].append({"type": "paragraph", "text": text})

    for table in document.tables:
        table_md, table_data = extract_table_from_docx(table)
        markdown_output.append(f"\n{table_md}\n")
        json_output["content"].append({"type": "table", "data": table_data})

    # TODO: Extract images from DOCX (more complex, often requires saving to temp files)
    # For images, python-docx doesn't directly expose image bytes easily. 
    # You'd typically need to extract the document.xml and media files from the .docx zip archive.
    # For a full implementation, consider a library like 'docx2txt' or manual zip extraction.

    return "\n".join(markdown_output), json_output
```

**`backend/document-processor/parsers/xlsx_parser.py`:**

```python
import openpyxl

def parse_xlsx(file_stream):
    markdown_output = []
    json_output = {"sheets": []}

    workbook = openpyxl.load_workbook(file_stream)

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        markdown_output.append(f"\n## Sheet: {sheet_name}\n")
        json_sheet_data = {"name": sheet_name, "rows": []}

        # Get header row
        header = [cell.value for cell in sheet[1]]
        if header:
            markdown_output.append("|" + "|".join(str(h) if h is not None else '' for h in header) + "|")
            markdown_output.append("|" + "--|" * len(header))

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2)):
            row_values = [cell.value for cell in row]
            markdown_output.append("|" + "|".join(str(v) if v is not None else '' for v in row_values) + "|")
            json_sheet_data["rows"].append(row_values)
        
        json_output["sheets"].append(json_sheet_data)

    return "\n".join(markdown_output), json_output
```

**`backend/document-processor/parsers/pptx_parser.py`:**

```python
from pptx import Presentation
from utils.openai_vision import describe_image
import io

def parse_pptx(file_stream):
    markdown_output = []
    json_output = {"slides": []}

    prs = Presentation(file_stream)

    for slide_num, slide in enumerate(prs.slides):
        markdown_output.append(f"\n## Slide {slide_num + 1}\n")
        json_slide_data = {"slide_number": slide_num + 1, "content": []}

        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                text = shape.text.strip()
                markdown_output.append(f"{text}\n")
                json_slide_data["content"].append({"type": "text", "text": text})
            elif shape.shape_type == 13: # Picture
                # This is a simplified way to get image data, might need refinement
                image_bytes = None
                image_ext = "png" # Default, try to infer better
                if shape.image.blob:
                    image_bytes = shape.image.blob
                    # Attempt to get actual extension from content_type
                    if 'jpeg' in shape.image.content_type: image_ext = 'jpeg'
                    elif 'png' in shape.image.content_type: image_ext = 'png'

                if image_bytes:
                    description = describe_image(image_bytes, image_ext)
                    markdown_output.append(f"\n![Image: {description}](embedded_slide_image_{slide_num}.{image_ext})\n")
                    json_slide_data["content"].append({"type": "image", "description": description, "extension": image_ext})

        json_output["slides"].append(json_slide_data)

    return "\n".join(markdown_output), json_output
```

**`backend/document-processor/parsers/txt_parser.py`:**

```python
def parse_txt(file_stream):
    content = file_stream.read().decode('utf-8')
    markdown_output = content
    json_output = {"text": content}
    return markdown_output, json_output
```

**`backend/document-processor/parsers/image_parser.py`:**

```python
from PIL import Image
from utils.openai_vision import describe_image
import io

def parse_image(file_stream):
    # Read image bytes
    image_bytes = file_stream.read()
    
    # Determine image extension (Pillow can infer, but explicit is better)
    try:
        img = Image.open(io.BytesIO(image_bytes))
        image_ext = img.format.lower()
    except Exception:
        image_ext = "png" # Fallback

    description = describe_image(image_bytes, image_ext)
    markdown_output = f"![Image: {description}](uploaded_image.{image_ext})\n"
    json_output = {"type": "image", "description": description, "extension": image_ext}
    return markdown_output, json_output
```

### 3.3. AI-Powered Content Extraction (OpenAI Vision API)

**`backend/document-processor/utils/openai_vision.py`:**

*   This module handles communication with the OpenAI Vision API to describe images and diagrams.

```python
import base64
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def describe_image(image_bytes, image_ext):
    base64_image = encode_image(image_bytes)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image or diagram in detail, focusing on its content, context, and any data presented. Provide a comprehensive description that would allow someone to understand the figure without seeing it."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_ext};base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error describing image with OpenAI Vision API: {e}")
        return "[Failed to describe image using AI]"
```

### 3.4. Table Extraction

**`backend/document-processor/utils/table_extractor.py`:**

*   This module will contain functions to extract tables from different document types and convert them into Markdown table format.
*   For PDF, this is particularly challenging and often requires advanced layout analysis or dedicated libraries (e.g., `camelot-py`, `tabula-py`). For this guide, a simplified approach is shown for DOCX.

```python
def extract_table_from_docx(table_obj):
    markdown_table = []
    table_data = []

    # Extract header
    header_cells = [cell.text.strip() for cell in table_obj.rows[0].cells]
    markdown_table.append("|" + "|".join(header_cells) + "|")
    markdown_table.append("|" + "--|" * len(header_cells))
    table_data.append(header_cells)

    # Extract rows
    for row in table_obj.rows[1:]:
        row_cells = [cell.text.strip() for cell in row.cells]
        markdown_table.append("|" + "|".join(row_cells) + "|")
        table_data.append(row_cells)

    return "\n".join(markdown_table), table_data

# TODO: Implement extract_table_from_pdf, extract_table_from_pptx etc.
# These would be significantly more complex and might require external libraries
# or advanced image processing combined with OCR for image-based tables.
```

### 3.5. Math Content Conversion

**`backend/document-processor/utils/math_converter.py`:**

*   This module will handle the conversion of identified mathematical expressions into LaTeX format.
*   Identifying mathematical expressions within general text (especially in PDFs or images) is a complex task that often requires machine learning models (e.g., Pix2Text, Mathpix).
*   `latexify-py` is primarily for converting Python functions to LaTeX, not for parsing arbitrary math expressions from text. For real-world parsing, a dedicated math OCR/parser would be needed.

```python
# This is a placeholder. Real-world math parsing from documents is complex.
# It would typically involve: 
# 1. Math detection (identifying regions containing math)
# 2. Math OCR (converting image of math to LaTeX)
# 3. Parsing embedded math objects (e.g., MathML in DOCX)

def convert_math_to_latex(math_expression_text):
    # This function would ideally use a dedicated library or API
    # For demonstration, we'll just wrap it in LaTeX math delimiters
    return f"\\text{{{math_expression_text}}}"

# Example of how latexify-py works (not for parsing arbitrary text)
# from latexify import latexify
# @latexify(math_mode=True)
# def solve_quadratic(a, b, c):
#     return (-b + (b**2 - 4*a*c)**0.5) / (2*a)
# print(solve_quadratic)
```

### 3.6. Real-time Markdown Preview and Bi-directional Synchronization

**Frontend (`frontend/src/components/MarkdownEditor.tsx` and `frontend/src/components/DocumentViewer.tsx`):**

*   **Markdown Editor:** Use a library like `react-markdown` for rendering Markdown. For editing, a simple `textarea` or a more advanced editor like `CodeMirror` or `Monaco Editor` can be used.
*   **Real-time Preview:** The `react-markdown` component will re-render automatically as the Markdown content state changes.
*   **Bi-directional Synchronization:** This is the most complex part. It requires:
    1.  **Mapping:** During document parsing, create a mapping between sections/elements in the original document and their corresponding Markdown output. This could involve storing line numbers, page numbers, or unique identifiers.
    2.  **Scroll Event Listeners:** Attach scroll event listeners to both the document viewer and the Markdown editor.
    3.  **Calculation:** When one panel scrolls, calculate the corresponding scroll position in the other panel based on the mapping.
    4.  **Programmatic Scrolling:** Programmatically scroll the other panel to the calculated position.
*   **Click-to-Highlight:** Similar to synchronization, this relies on the mapping. When a user clicks a Markdown element, identify its corresponding original document element from the map and highlight it (e.g., by changing its background color or applying a border).

```typescript
// frontend/src/components/MarkdownEditor.tsx
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownEditorProps {
  initialMarkdown: string;
  onMarkdownChange: (markdown: string) => void;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ initialMarkdown, onMarkdownChange }) => {
  const [markdown, setMarkdown] = useState(initialMarkdown);
  const [isPreviewMode, setIsPreviewMode] = useState(false);

  useEffect(() => {
    setMarkdown(initialMarkdown);
  }, [initialMarkdown]);

  const handleEditorChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMarkdown(e.target.value);
    onMarkdownChange(e.target.value);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center p-2 border-b">
        <h3 className="text-lg font-semibold">Markdown Editor</h3>
        <label className="inline-flex items-center cursor-pointer">
          <input 
            type="checkbox" 
            value="" 
            className="sr-only peer" 
            checked={isPreviewMode}
            onChange={() => setIsPreviewMode(!isPreviewMode)}
          />
          <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          <span className="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">Preview Mode</span>
        </label>
      </div>
      <div className="flex-grow overflow-auto p-4">
        {isPreviewMode ? (
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={dracula}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {markdown}
          </ReactMarkdown>
        ) : (
          <textarea
            className="w-full h-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={markdown}
            onChange={handleEditorChange}
            placeholder="Your Markdown will appear here..."
          />
        )}
      </div>
    </div>
  );
};

export default MarkdownEditor;
```

**Frontend (`frontend/src/components/DocumentViewer.tsx`):**

*   This component will dynamically render the original document based on its type.
*   For PDFs, consider using `react-pdf` or embedding a Google Docs Viewer.
*   For DOCX, XLSX, PPTX, a viewer like `mammoth.js` (for DOCX to HTML) or `sheetjs` (for XLSX to HTML) might be used, or rely on embedding external viewers.
*   For images, a simple `<img>` tag.
*   For TXT, a `<pre>` tag.

```typescript
// frontend/src/components/DocumentViewer.tsx
import React from 'react';

interface DocumentViewerProps {
  fileType: string;
  fileUrl: string; // URL to the original uploaded file (e.g., from temp storage)
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ fileType, fileUrl }) => {
  const renderContent = () => {
    if (!fileUrl) {
      return <p className="text-center text-gray-500">Upload a document to view it here.</p>;
    }

    switch (fileType) {
      case 'application/pdf':
        // For PDFs, you might use react-pdf or an iframe to Google Docs Viewer
        return (
          <iframe
            src={`https://docs.google.com/gview?url=${encodeURIComponent(fileUrl)}&embedded=true`}
            className="w-full h-full border-0"
            title="PDF Viewer"
          ></iframe>
        );
      case 'image/png':
      case 'image/jpeg':
        return <img src={fileUrl} alt="Original Document" className="max-w-full max-h-full object-contain mx-auto" />;
      case 'text/plain':
        // For TXT, fetch content and display
        return (
          <pre className="whitespace-pre-wrap font-mono text-sm p-4">
            {/* You'd fetch the text content here or pass it as a prop */}
            Loading text content...
          </pre>
        );
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
      case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return (
          <p className="text-center text-gray-500 p-4">
            Viewing for {fileType} is not directly supported in this demo. 
            Consider using dedicated libraries or external viewers for full fidelity.
            <br/>
            <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">Download original file</a>
          </p>
        );
      default:
        return <p className="text-center text-gray-500">Unsupported file type for direct viewing: {fileType}</p>;
    }
  };

  return (
    <div className="flex flex-col h-full border-r">
      <h3 className="text-lg font-semibold p-2 border-b">Original Document</h3>
      <div className="flex-grow overflow-auto flex items-center justify-center">
        {renderContent()}
      </div>
    </div>
  );
};

export default DocumentViewer;
```

### 3.7. Persistent History System

**Frontend (`frontend/src/lib/store.ts` and `frontend/src/components/HistorySidebar.tsx`):**

*   Use `localForage` for client-side persistent storage. This is an asynchronous storage wrapper that uses IndexedDB or WebSQL behind the scenes, providing a `localStorage`-like API.
*   Integrate `localForage` with Zustand for state management, ensuring that the history is loaded on app startup and updated whenever a new document is processed.

```typescript
// frontend/src/lib/store.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import localforage from 'localforage';

interface DocumentHistoryEntry {
  id: string;
  fileName: string;
  fileType: string;
  uploadDate: string;
  markdownContent: string;
  jsonContent: any;
  originalFileUrl?: string; // Temporary URL for viewing
}

interface AppState {
  documentHistory: DocumentHistoryEntry[];
  addDocumentToHistory: (entry: DocumentHistoryEntry) => void;
  clearHistory: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      documentHistory: [],
      addDocumentToHistory: (entry) => {
        set((state) => ({
          documentHistory: [entry, ...state.documentHistory.slice(0, 9)], // Keep last 10 entries
        }));
      },
      clearHistory: () => set({ documentHistory: [] }),
    }),
    {
      name: 'document-parser-history-storage', // name of the item in storage (must be unique)
      storage: createJSONStorage(() => localforage), // Use localforage as the storage backend
    }
  )
);
```

```typescript
// frontend/src/components/HistorySidebar.tsx
import React from 'react';
import { useAppStore } from '../lib/store';

interface HistorySidebarProps {
  onSelectDocument: (docId: string) => void;
}

const HistorySidebar: React.FC<HistorySidebarProps> = ({ onSelectDocument }) => {
  const { documentHistory, clearHistory } = useAppStore();

  return (
    <div className="w-64 bg-gray-100 p-4 border-r h-full overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">History</h2>
      {documentHistory.length === 0 ? (
        <p className="text-gray-500">No documents processed yet.</p>
      ) : (
        <ul className="space-y-2">
          {documentHistory.map((doc) => (
            <li 
              key={doc.id} 
              className="p-2 bg-white rounded-md shadow-sm cursor-pointer hover:bg-gray-50"
              onClick={() => onSelectDocument(doc.id)}
            >
              <p className="font-medium text-gray-800 truncate">{doc.fileName}</p>
              <p className="text-sm text-gray-600">{doc.fileType.split('/')[1].toUpperCase()} - {new Date(doc.uploadDate).toLocaleDateString()}</p>
            </li>
          ))}
        </ul>
      )}
      {documentHistory.length > 0 && (
        <button 
          onClick={clearHistory} 
          className="mt-4 w-full bg-red-500 text-white py-2 rounded-md hover:bg-red-600"
        >
          Clear History
        </button>
      )}
    </div>
  );
};

export default HistorySidebar;
```

### 3.8. Export Functionality

**Frontend:**

*   Implement buttons for 



exporting Markdown and JSON. When clicked, these buttons will trigger a client-side download.

```typescript
// Example in a component where markdown and json are available
const handleExportMarkdown = (markdownContent: string, fileName: string) => {
  const blob = new Blob([markdownContent], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${fileName.split('.')[0]}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const handleExportJson = (jsonData: any, fileName: string) => {
  const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${fileName.split('.')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
```

### 3.9. Search Functionality

**Frontend:**

*   Integrate a client-side search library (e.g., `lunr.js` or a custom implementation) to index the Markdown content.
*   Implement a search input field. As the user types, filter and highlight results in the Markdown preview.
*   For the original document viewer, if it's an embedded PDF viewer, it might have its own search functionality. For other document types, you might need to implement custom highlighting based on text positions.

### 3.10. Auto-save Functionality

**Frontend:**

*   Use `useEffect` hooks with debouncing to automatically save the Markdown content to `localForage` at regular intervals (e.g., every 5 seconds) or after a period of inactivity.

```typescript
// Example in MarkdownEditor.tsx or a parent component
import { useEffect, useRef } from 'react';
import { useAppStore } from '../lib/store';

// ... inside your component
const { addDocumentToHistory, documentHistory } = useAppStore();
const currentDocId = 'some-id'; // Get the ID of the currently active document

const saveMarkdown = useRef(
  debounce((markdown: string) => {
    const docIndex = documentHistory.findIndex(doc => doc.id === currentDocId);
    if (docIndex !== -1) {
      const updatedHistory = [...documentHistory];
      updatedHistory[docIndex] = { ...updatedHistory[docIndex], markdownContent: markdown };
      // This is a simplified update. In a real app, you'd have a specific action to update an entry.
      // For now, we'll just re-add it, which will put it at the top and remove the old one if it's beyond the limit.
      addDocumentToHistory({ ...updatedHistory[docIndex], markdownContent: markdown });
    }
    console.log('Markdown auto-saved!');
  }, 5000) // Save every 5 seconds of inactivity
).current;

useEffect(() => {
  // Call saveMarkdown whenever the markdown content changes
  // This would be triggered by the onMarkdownChange callback from the editor
  // saveMarkdown(currentMarkdownContent);
}, [currentMarkdownContent]); // currentMarkdownContent would be the state holding the editor's content

// Utility for debouncing (can be in lib/utils.ts)
function debounce<T extends (...args: any[]) => any>(func: T, delay: number): T {
  let timeout: NodeJS.Timeout;
  return ((...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), delay);
  }) as T;
}
```

### 3.11. Keyboard Shortcuts

**Frontend:**

*   Implement global event listeners for `keydown` events.
*   Map specific key combinations to common actions (e.g., `Ctrl+S` for save, `Ctrl+E` for export, `Ctrl+P` for toggle preview).

```typescript
// Example in a main layout component or a custom hook
import { useEffect } from 'react';

const useKeyboardShortcuts = (actions: { [key: string]: () => void }) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Example: Ctrl+S for save
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault(); // Prevent browser's default save action
        actions.save?.();
      }
      // Example: Ctrl+E for export
      if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
        event.preventDefault();
        actions.export?.();
      }
      // Add more shortcuts as needed
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [actions]);
};

// Usage in a component:
// useKeyboardShortcuts({
//   save: () => console.log('Saving via shortcut'),
//   export: () => console.log('Exporting via shortcut'),
// });
```

## 4. Error Handling

*   **Frontend:** Display user-friendly error messages for failed uploads, unsupported file types, or processing errors. Use toast notifications or dedicated error display areas.
*   **Backend (Next.js API Routes):** Implement robust `try-catch` blocks to gracefully handle errors during file upload, temporary storage, and communication with the Python service. Return appropriate HTTP status codes and error messages to the frontend.
*   **Document Processing Service (Flask/Python):** Catch exceptions during file parsing, AI calls, and content extraction. Log detailed error information for debugging and return concise error messages to the Next.js backend.

## 5. Deployment Considerations

*   **Frontend (Next.js):** Can be deployed to Vercel, Netlify, or any static hosting provider. Server-side rendering and API routes will require a Node.js environment.
*   **Document Processing Service (Flask/Python):** Can be deployed as a separate microservice using Docker containers on platforms like AWS ECS, Google Cloud Run, or Kubernetes. Ensure proper environment variable management for API keys.
*   **Scalability:** Consider using a message queue (e.g., RabbitMQ, Kafka) between the Next.js backend and the Python processing service for asynchronous processing of large files and to handle high loads more gracefully.

This guide provides a foundational understanding and initial code snippets for implementing the core features. Further development will involve refining these implementations, adding comprehensive testing, and optimizing for production environments.

