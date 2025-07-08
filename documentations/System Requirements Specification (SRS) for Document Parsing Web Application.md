# System Requirements Specification (SRS) for Document Parsing Web Application

## 1. Introduction

### 1.1. Purpose

This System Requirements Specification (SRS) document details the functional and non-functional requirements for a web-based document parsing application. The application aims to provide users with a seamless experience for converting various file formats (PDF, DOCX, XLSX, PPT, TXT, PNG, JPG) into Markdown, offering real-time preview, AI-powered content extraction, and persistent history management.

### 1.2. Scope

The scope of this project encompasses the development of a full-stack web application, including the frontend user interface, backend API services, and a dedicated document processing microservice. It will support file uploads, conversion to Markdown, dual-panel viewing, bi-directional synchronization, click-to-highlight functionality, export options, and a persistent history system. Advanced features include AI-driven image/diagram description, LaTeX formatting for mathematical content, and structured table extraction.

### 1.3. Definitions, Acronyms, and Abbreviations

*   **SRS:** System Requirements Specification
*   **UI:** User Interface
*   **UX:** User Experience
*   **API:** Application Programming Interface
*   **OCR:** Optical Character Recognition
*   **AI:** Artificial Intelligence
*   **PDF:** Portable Document Format
*   **DOCX:** Microsoft Word Document (XML-based)
*   **XLSX:** Microsoft Excel Spreadsheet (XML-based)
*   **PPT:** Microsoft PowerPoint Presentation
*   **TXT:** Plain Text File
*   **PNG:** Portable Network Graphics
*   **JPG:** Joint Photographic Experts Group
*   **Markdown:** A lightweight markup language for creating formatted text using a plain-text editor.
*   **JSON:** JavaScript Object Notation
*   **Next.js:** A React framework for building web applications.
*   **Node.js:** A JavaScript runtime environment.
*   **Flask:** A Python web framework.
*   **LaTeX:** A document preparation system for high-quality typesetting, especially for mathematical content.

### 1.4. References

*   User Requirements Document (Implicit in the initial prompt)
*   Technical Architecture and Tech Stack Document (technical_architecture.md)

## 2. Overall Description

### 2.1. Product Perspective

The document parsing web application is a standalone system designed to provide a comprehensive solution for converting various document types into Markdown format. It will interact with user browsers for input and output, and leverage a backend service for processing, which in turn communicates with a specialized document processing microservice.

### 2.2. Product Functions

The primary functions of the system include:

*   File Upload and Management
*   Document to Markdown Conversion
*   Dual-Panel Viewing and Synchronization
*   Content Extraction (Text, Images, Diagrams, Tables, Math)
*   AI-Powered Image/Diagram Description
*   Export Functionality (Markdown, JSON)
*   Persistent Document History
*   Real-time Markdown Preview
*   Search Functionality
*   File Metadata Display
*   Error Handling
*   Auto-save
*   Keyboard Shortcuts

### 2.3. User Characteristics

The target users for this application include:

*   **Researchers:** Who need to extract structured information from various academic papers and reports.
*   **Content Creators:** Who want to convert existing documents into Markdown for publishing on blogs or websites.
*   **Developers:** Who require structured data from documents for further processing or integration.
*   **Students:** Who need to organize notes and study materials in a standardized format.

Users are expected to have basic computer literacy and familiarity with web applications. No prior knowledge of Markdown or programming is required.

### 2.4. General Constraints

*   **Supported File Formats:** PDF, DOCX, XLSX, PPT, TXT, PNG, JPG.
*   **Output Formats:** Markdown, JSON.
*   **Performance:** The system must provide a responsive user experience, with reasonable processing times for typical document sizes.
*   **Security:** User data and uploaded files must be handled securely.
*   **Scalability:** The architecture should allow for future scaling to accommodate increased user load and document processing volume.
*   **OpenAI API Usage:** Reliance on OpenAI Vision API for specific AI functionalities.

## 3. Functional Requirements

### 3.1. File Upload Functionality

**FR-1.1:** The system SHALL allow users to upload files via a clear file upload area with drag-and-drop support.
**FR-1.2:** The system SHALL support the upload of PDF, DOCX, XLSX, PPT, TXT, PNG, and JPG file formats.
**FR-1.3:** The system SHALL display loading states and progress indicators during file processing.
**FR-1.4:** The system SHALL provide error handling for unsupported file formats, notifying the user appropriately.

### 3.2. Document Conversion to Markdown

**FR-2.1:** The system SHALL accurately convert uploaded documents (PDF, DOCX, XLSX, PPT, TXT) to Markdown format.
**FR-2.2:** The system SHALL identify and process images and diagrams within documents.
**FR-2.3:** The system SHALL use the OpenAI Vision model to generate descriptive results for images and diagrams, explaining their content and context in Markdown format.
**FR-2.4:** The system SHALL identify and convert mathematical content into LaTeX format within the Markdown output.
**FR-2.5:** The system SHALL extract tables from documents and format them as Markdown tables.

### 3.3. User Interface and Interaction

**FR-3.1:** The system SHALL present a dual-panel interface with the original document viewer on the left and a real-time Markdown preview on the right.
**FR-3.2:** The system SHALL enable bi-directional synchronization between the original document view and the Markdown preview, meaning scrolling or navigating in one panel updates the other.
**FR-3.3:** The system SHALL implement click-to-highlight functionality, allowing users to click on a section in the Markdown preview to highlight the corresponding section in the original document, and vice-versa.
**FR-3.4:** The system SHALL include a toggle switch for switching between Markdown editing mode and Markdown preview mode.
**FR-3.5:** The system SHALL display file metadata (size, type, upload date) for the currently processed document.

### 3.4. Export Functionality

**FR-4.1:** The system SHALL allow users to export the converted Markdown content.
**FR-4.2:** The system SHALL allow users to export the processed document data in JSON format.

### 3.5. Persistent History System

**FR-5.1:** The system SHALL maintain a persistent history of previously processed documents.
**FR-5.2:** The system SHALL display an organized history sidebar with recent documents.
**FR-5.3:** The system SHALL allow users to re-open and view previously processed documents from the history.

### 3.6. Additional Features

**FR-6.1:** The system SHALL provide real-time Markdown preview as the user edits the Markdown content.
**FR-6.2:** The system SHALL implement search functionality within the displayed documents (both original and Markdown preview).
**FR-6.3:** The system SHALL implement auto-save functionality for the Markdown content.
**FR-6.4:** The system SHALL provide keyboard shortcuts for common actions (e.g., save, export, switch view).

## 4. Non-Functional Requirements

### 4.1. Performance Requirements

**NFR-1.1:** The application SHALL load within 3 seconds on a standard broadband connection.
**NFR-1.2:** Document conversion for typical documents (e.g., 10-page PDF, 5-page DOCX) SHALL complete within 15 seconds.
**NFR-1.3:** Real-time Markdown preview SHALL update with less than 100ms latency.
**NFR-1.4:** The system SHALL efficiently handle concurrent processing of multiple documents without significant performance degradation.

### 4.2. Security Requirements

**NFR-2.1:** The system SHALL ensure secure file uploads and storage, protecting against unauthorized access.
**NFR-2.2:** All communication between the frontend, backend, and document processing service SHALL be encrypted (HTTPS/SSL).
**NFR-2.3:** The system SHALL implement appropriate measures to prevent cross-site scripting (XSS) and cross-site request forgery (CSRF) attacks.

### 4.3. Usability Requirements

**NFR-3.1:** The user interface SHALL be intuitive and easy to navigate for users with basic computer literacy.
**NFR-3.2:** The application SHALL provide clear and concise feedback to the user for all actions, including success messages, error messages, and progress updates.
**NFR-3.3:** The application SHALL adhere to the specified color palette (Primary: Dark Blue #1a237e, Secondary: White #ffffff, Accent: Black #000000) for a clean and modern interface.
**NFR-3.4:** The application SHALL implement responsive design, ensuring optimal viewing and interaction across various screen sizes (desktop, tablet, mobile).

### 4.4. Reliability Requirements

**NFR-4.1:** The system SHALL handle unexpected errors gracefully, providing informative messages to the user without crashing.
**NFR-4.2:** The persistent history system SHALL reliably store and retrieve processed document information.

### 4.5. Maintainability Requirements

**NFR-5.1:** The codebase SHALL be well-documented and follow established coding standards.
**NFR-5.2:** The system architecture SHALL be modular, allowing for independent updates and maintenance of components.

### 4.6. Portability Requirements

**NFR-6.1:** The web application SHALL be accessible via modern web browsers (Chrome, Firefox, Safari, Edge) on various operating systems (Windows, macOS, Linux).

## 5. Data Model (Conceptual)

### 5.1. Document History Entry

| Field Name    | Data Type | Description                                  |
| :------------ | :-------- | :------------------------------------------- |
| `id`          | String    | Unique identifier for the document entry     |
| `fileName`    | String    | Original name of the uploaded file           |
| `fileType`    | String    | Type of the uploaded file (e.g., 


PDF, DOCX)          |
| `uploadDate`  | Date      | Timestamp of when the document was uploaded  |
| `markdownContent` | String    | The converted Markdown content               |
| `jsonContent` | JSON      | The extracted JSON data                      |
| `originalFileUrl` | String    | URL to the original uploaded file (temporary) |

## 6. System Design (High-Level)

### 6.1. Component Diagram

(Refer to `system_architecture.png` in the `technical_architecture.md` document for a visual representation of the system components and their interactions.)

### 6.2. Data Flow Diagram

1.  **User Uploads File:** The user interacts with the Next.js frontend to upload a document. The frontend uses `React Dropzone` for drag-and-drop functionality.
2.  **Frontend to Backend:** The uploaded file is sent to the Next.js API route (backend) via an HTTP POST request.
3.  **Backend to Document Processing Service:** The Next.js API route receives the file and forwards it to the Python Flask Document Processing Service. For large files, chunking or streaming might be implemented.
4.  **Document Processing:** The Python service identifies the file type and uses the appropriate parsing library (PyMuPDF, python-docx, openpyxl, python-pptx, Pillow). It extracts text, images, tables, and mathematical content.
    *   **Image/Diagram Processing:** Images and diagrams are sent to the OpenAI Vision API for description generation. The descriptions are then integrated into the Markdown output.
    *   **Math Processing:** Mathematical expressions are identified and converted to LaTeX format.
    *   **Table Processing:** Tables are extracted and formatted into Markdown table syntax.
5.  **Markdown Generation:** The processed content is assembled into a comprehensive Markdown string.
6.  **JSON Generation:** A JSON representation of the extracted data (e.g., text, image descriptions, table data, math expressions) is also generated.
7.  **Document Processing Service to Backend:** The Markdown content and JSON data are sent back to the Next.js API route.
8.  **Backend to Frontend (Real-time):** The Next.js API route sends the Markdown content and JSON data to the frontend. Real-time updates (e.g., processing progress, completion) are pushed to the frontend using Socket.IO.
9.  **Frontend Display:** The frontend displays the original document (using a viewer library) on the left panel and the Markdown preview on the right panel. Bi-directional synchronization is maintained.
10. **History Storage:** The Markdown content, JSON data, and file metadata are stored locally using `localForage` for persistent history.
11. **Export:** Users can trigger export of Markdown or JSON content from the frontend.

## 7. User Interface (UI) Requirements

### 7.1. General Layout

*   **Header:** Application title, potentially a logo, and navigation elements.
*   **Sidebar (Left):** Organized history of recent documents.
*   **Main Content Area:** Divided into two panels for document viewing and Markdown preview.
*   **Footer:** Copyright information, version number.

### 7.2. Color Palette

*   **Primary:** Dark Blue (#1a237e)
*   **Secondary:** White (#ffffff)
*   **Accent:** Black (#000000)

### 7.3. File Upload Area

*   A prominent, clear area for file uploads.
*   Support for drag-and-drop functionality.
*   Visual cues for file upload status (e.g., dashed border, changing background color on drag-over).

### 7.4. Dual-Panel Interface

*   **Left Panel:** Original document viewer. Should accurately render PDF, DOCX, XLSX, PPT, and image files. For TXT, it will display raw text.
*   **Right Panel:** Markdown editor with real-time preview. A toggle switch will allow switching between editing and preview modes.

### 7.5. History Sidebar

*   Displays a list of recently processed documents.
*   Each item should show the file name, type, and upload date.
*   Clicking an item should load the corresponding document and its Markdown/JSON content.

### 7.6. Loading States and Progress Indicators

*   Visual indicators (spinners, progress bars) for file uploads and document processing.
*   Clear messages indicating the current status (e.g., 


'Uploading file...', 'Processing document...', 'Conversion complete!').

### 7.7. Responsive Design

*   The UI SHALL adapt gracefully to various screen sizes, from mobile devices to large desktop monitors.
*   Layouts, font sizes, and interactive elements SHALL adjust to provide an optimal user experience on all devices.

## 8. Detailed System Design and Flow (End-to-End Flow of Different Document Processing)

This section details the end-to-end flow for processing different document types, highlighting how each feature works.

### 8.1. General Document Processing Flow

1.  **File Selection/Upload:**
    *   User navigates to the application homepage.
    *   User can either click on a designated upload area to open a file dialog or drag-and-drop a file into the area.
    *   **UI/UX:** The upload area will visually indicate drag-and-drop readiness (e.g., changing border color).
2.  **File Validation & Initial Processing (Frontend):**
    *   Upon file selection, the frontend immediately performs client-side validation for file type and size.
    *   If the file type is unsupported, an error message is displayed to the user (FR-1.4).
    *   **UI/UX:** A loading spinner and 


progress bar appear (FR-1.3).
3.  **Upload to Backend (Frontend to Next.js API Route):**
    *   The validated file is sent to the Next.js API route (e.g., `/api/upload`) using a `multipart/form-data` request.
    *   **Technical:** For large files, the frontend will implement chunking and resumable uploads to ensure robustness and prevent timeouts.
4.  **Backend Processing (Next.js API Route):**
    *   The Next.js API route receives the file. It temporarily stores the file and initiates a request to the Python Document Processing Service.
    *   **Technical:** The API route will use a unique identifier for each processing job and maintain its state.
    *   **Real-time Communication:** The backend establishes a WebSocket connection (Socket.IO) with the frontend to send real-time updates on the processing status (e.g., 



'File received', 'Processing started', 'Extracting images', 'Converting to Markdown').
5.  **Dispatch to Document Processing Service (Next.js API Route to Flask/Python):**
    *   The Next.js API route sends the file (or a reference to its temporary storage) and relevant metadata to the Flask Document Processing Service.
    *   **Technical:** This communication will be via an internal HTTP POST request, potentially using a message queue for asynchronous processing of large files to prevent blocking the API route.
6.  **Document Processing (Flask/Python Service):**
    *   The Flask service receives the file and determines its type.
    *   It then dispatches the file to the appropriate parser/library:
        *   **PDF:** PyMuPDF
        *   **DOCX:** python-docx
        *   **XLSX:** openpyxl
        *   **PPTX:** python-pptx
        *   **TXT:** Standard Python I/O
        *   **PNG/JPG:** Pillow (for basic image handling before OCR)
    *   **Content Extraction:**
        *   **Text:** All parsers will extract textual content.
        *   **Images/Diagrams:** Images are extracted. For each image, the service will:
            *   Send the image to the OpenAI Vision API (FR-2.3).
            *   Receive a descriptive text from the Vision API.
            *   Integrate this description into the Markdown output (e.g., `![Description of image](image_url)`).
        *   **Tables:** The service will identify tables within the document. Custom logic will be developed to parse table structures and content, then format them into Markdown tables (FR-2.5).
        *   **Mathematical Content:** The service will identify mathematical expressions. For each expression, it will attempt to convert it into LaTeX format using `latexify-py` or similar logic (FR-2.4). The LaTeX will be embedded in the Markdown output (e.g., `$$ \sum_{i=1}^n i = \frac{n(n+1)}{2} $$`).
    *   **Markdown Generation:** As content is extracted and processed, it is assembled into a single Markdown string.
    *   **JSON Generation:** Concurrently, a structured JSON object containing all extracted data (text, image descriptions, table data, math expressions, metadata) is generated (FR-4.2).
7.  **Results Back to Backend (Flask/Python Service to Next.js API Route):**
    *   Once processing is complete, the Flask service sends the generated Markdown and JSON content back to the Next.js API route.
8.  **Results to Frontend (Next.js API Route to Frontend):**
    *   The Next.js API route receives the processed data.
    *   It then pushes the Markdown and JSON content to the frontend via the established Socket.IO connection (FR-3.1, FR-6.1).
    *   **UI/UX:** The loading indicators disappear, and the dual-panel interface populates with the original document (if viewable) and the Markdown preview.
9.  **Frontend Display and Interaction:**
    *   **Dual-Panel Display:** The left panel displays the original document (using a suitable viewer, e.g., `react-pdf` for PDFs, or rendering images for image files). The right panel displays the generated Markdown in a real-time editor/preview component (FR-3.1, FR-6.1).
    *   **Bi-directional Synchronization:** As the user scrolls or navigates in one panel, the other panel automatically scrolls to the corresponding section (FR-3.2). This will require mapping sections of the original document to sections of the Markdown output.
    *   **Click-to-Highlight:** Clicking on a section in either panel will highlight the corresponding content in the other panel (FR-3.3). This will involve precise mapping and DOM manipulation.
    *   **Toggle Switch:** A toggle switch allows the user to switch the right panel between Markdown editing mode and a pure Markdown preview mode (FR-3.4).
    *   **File Metadata Display:** The frontend displays the file name, type, and upload date (FR-3.5).
10. **Persistent History:**
    *   After successful processing, the file metadata, Markdown content, and JSON content are stored locally using `localForage` (FR-5.1).
    *   **UI/UX:** The history sidebar is updated with the new entry (FR-5.2).
11. **Export Functionality:**
    *   Users can click 


on buttons to export the Markdown content (FR-4.1) or the JSON data (FR-4.2). The frontend will trigger a download of the respective file.

### 8.2. Specific Document Type Processing Considerations

#### 8.2.1. PDF Processing

*   **Challenges:** PDFs can contain a mix of text, images, and vector graphics. Scanned PDFs require robust OCR.
*   **Flow:**
    1.  PyMuPDF extracts text, images, and metadata. It can handle both native and scanned PDFs (with OCR via OpenAI Vision API).
    2.  Images are sent to OpenAI Vision for description.
    3.  Layout analysis is performed to identify paragraphs, headings, tables, and mathematical equations.
    4.  Tables are extracted and converted to Markdown tables.
    5.  Mathematical equations are converted to LaTeX.
    6.  The extracted content is assembled into Markdown.

#### 8.2.2. DOCX Processing

*   **Challenges:** DOCX files are XML-based and contain rich formatting, embedded objects, and complex structures.
*   **Flow:**
    1.  `python-docx` parses the DOCX file, extracting paragraphs, runs, tables, and embedded images.
    2.  Styles (headings, bold, italics) are mapped to Markdown equivalents.
    3.  Images are extracted and sent to OpenAI Vision for description.
    4.  Tables are extracted and converted to Markdown tables.
    5.  Mathematical equations (if present as MathML or embedded objects) are identified and converted to LaTeX.
    6.  The content is assembled into Markdown.

#### 8.2.3. XLSX Processing

*   **Challenges:** XLSX files are primarily tabular data, but can also contain charts and images.
*   **Flow:**
    1.  `openpyxl` reads the spreadsheet data, iterating through sheets, rows, and cells.
    2.  Each sheet is converted into a separate Markdown table.
    3.  Charts and embedded images (if any) are extracted and sent to OpenAI Vision for description.
    4.  The content is assembled into Markdown, with clear separation between sheets.

#### 8.2.4. PPTX Processing

*   **Challenges:** PPTX files are slide-based, containing text boxes, shapes, images, and charts.
*   **Flow:**
    1.  `python-pptx` extracts content slide by slide.
    2.  Text from text boxes is extracted and formatted.
    3.  Images and charts are extracted and sent to OpenAI Vision for description.
    4.  Tables (if present) are extracted and converted to Markdown tables.
    5.  The content is assembled into Markdown, with each slide potentially represented as a new section.

#### 8.2.5. TXT Processing

*   **Challenges:** Simple text files, but may require basic formatting or smart paragraph detection.
*   **Flow:**
    1.  Standard Python I/O reads the file content.
    2.  Basic line breaks and paragraph structures are preserved.
    3.  The content is directly output as Markdown.

#### 8.2.6. PNG/JPG Processing

*   **Challenges:** Pure image files require robust OCR and AI description.
*   **Flow:**
    1.  Pillow loads the image.
    2.  The image is sent to OpenAI Vision API for both OCR (to extract any text) and description generation.
    3.  The extracted text and the AI-generated description are combined into Markdown.

### 8.3. Search Functionality

*   **FR-6.2:** The system SHALL implement search functionality within the displayed documents (both original and Markdown preview).
*   **Flow:**
    1.  **Indexing:** When a document is processed, its text content (from both original and Markdown) is indexed locally (e.g., using a client-side search library like `lunr.js` or simply by storing the text in `localForage` and performing string matching).
    2.  **User Input:** User types a search query into a search bar.
    3.  **Real-time Search:** As the user types, the system performs a real-time search against the indexed content.
    4.  **Highlighting Results:** Matching terms are highlighted in both the original document viewer (if supported by the viewer) and the Markdown preview.
    5.  **Navigation:** Users can navigate between search results (e.g., using 

