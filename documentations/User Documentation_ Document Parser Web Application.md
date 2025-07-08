# User Documentation: Document Parser Web Application

Welcome to the Document Parser Web Application! This guide will help you understand how to use the application to convert various document formats into Markdown, view them, and utilize advanced features like AI-powered content descriptions and persistent history.

## 1. Getting Started

### 1.1. What is this Application?

This application is a powerful tool designed to help you convert your documents (PDFs, Word files, Excel sheets, PowerPoint presentations, text files, and images) into Markdown format. It provides a clean interface where you can see your original document alongside its Markdown conversion in real-time. You can then export the Markdown or even a structured JSON version of your document.

### 1.2. Supported File Formats

You can upload and convert the following file types:

*   **Documents:** PDF, DOCX (Microsoft Word), XLSX (Microsoft Excel), PPTX (Microsoft PowerPoint), TXT (Plain Text)
*   **Images:** PNG, JPG

## 2. User Interface Overview

The application features a clean and intuitive interface with a dark blue, white, and black color palette. Here's a quick tour:

*   **Header:** At the top, you'll find the application title and potentially navigation options.
*   **History Sidebar (Left):** This panel on the left side of the screen displays a list of all the documents you've processed previously. You can click on any entry to quickly reload and view its content.
*   **Main Content Area:** This is the central part of the application, divided into two main panels:
    *   **Original Document Viewer (Left Panel):** This panel shows your uploaded document in its original format. You can scroll through it and interact with it as you would with a standard document viewer.
    *   **Markdown Editor/Preview (Right Panel):** This panel displays the converted Markdown content of your document. You can edit the Markdown directly, and any changes will be reflected in real-time in the preview. A toggle switch allows you to switch between editing and a pure preview mode.
*   **File Upload Area:** A prominent area, usually in the center or top, where you can drag and drop your files or click to select them from your computer.

![UI Overview](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866641691_na1fn_L2hvbWUvdWJ1bnR1L3VpX292ZXJ2aWV3.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDE2OTFfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzVnBYMjkyWlhKMmFXVjMucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzk4NzYxNjAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=KOFrvpMuV3de1YBD9204lnBCji8ASDWVQZRpvbkZ0g8GkQ5KvSRaKqejvCjWokI0hPKyRwJ9QpPsrzv4J1779nu4N6PYnadZr1sdONk2ZweGn36htaldqAeG-3gGdsbKKDSxVGLAwReXGy25paFfI3JnKeGwGr5OjGTaVPcmYxX3W5x1Q1So6qON8cneenSrv~FHcv1ByIHk5d35DwzrPXHatPxPrKolslHgVJCflIdpoiDQ6BiuOjjOWQiSFKnAtMpswNAZRD5YXVrxDB39YWYd7Y~Rwtf0RP5oaDsJbRmDpH6UoKGY1h8vg6qYKH0k~ea8~gRYutgULZQQDD4KAw__)

## 3. How to Use the Application

### 3.1. Uploading a Document

1.  **Drag and Drop:** Simply drag your desired file from your computer and drop it onto the designated 


file upload area.
2.  **Click to Upload:** Alternatively, click anywhere within the file upload area. This will open your computer's file explorer, allowing you to browse and select the document you wish to upload.

*   **Progress Indicators:** Once you upload a file, you will see loading states and progress indicators, showing you that your document is being processed. Please wait until the conversion is complete.
*   **Unsupported Files:** If you try to upload an unsupported file type, the application will notify you with an error message.

### 3.2. Viewing and Interacting with Documents

After a successful upload and conversion, your screen will display the dual-panel interface:

*   **Original Document Viewer (Left):** Your original document will be displayed here. You can scroll through it to review its content.
*   **Markdown Editor/Preview (Right):** The converted Markdown version of your document will appear here. You can:
    *   **Edit Markdown:** Directly type and modify the Markdown content. The preview will update in real-time.
    *   **Toggle Preview Mode:** Use the toggle switch above the Markdown panel to switch between the editable Markdown view and a clean preview mode. This is useful for reviewing the final rendered output.

### 3.3. Bi-directional Synchronization and Click-to-Highlight

One of the key features of this application is the seamless connection between the original document and its Markdown conversion:

*   **Scrolling Synchronization:** As you scroll through the original document on the left, the Markdown content on the right will automatically scroll to the corresponding section, and vice-versa. This helps you easily compare the two versions.
*   **Click-to-Highlight:** You can click on a specific section in the Markdown preview, and the application will highlight the corresponding content in the original document. This works in reverse as well: clicking on content in the original document will highlight its Markdown equivalent.

### 3.4. AI-Powered Content Descriptions

For documents containing images or diagrams, the application uses advanced Artificial Intelligence (AI) to understand and describe them. Instead of just seeing an image, the Markdown output will include a detailed textual description of what the image or diagram represents, along with its context. This means you can understand the visual content without even looking at the image itself.

### 3.5. Mathematical Content and Tables

*   **Mathematical Content:** Any mathematical equations or formulas identified in your document will be converted and presented in standard LaTeX format within the Markdown output. This ensures accurate and high-quality rendering of complex equations.
*   **Tables:** Tables from your documents will be intelligently extracted and formatted into clean, readable Markdown tables, preserving their structure and data.

### 3.6. Exporting Your Content

Once you are satisfied with the conversion, you can export your processed document in two formats:

*   **Export Markdown:** Click the 


Export Markdown button to download the converted Markdown file to your computer.
*   **Export JSON:** Click the Export JSON button to download a structured JSON file containing all the extracted data from your document, including text, image descriptions, and table data.

### 3.7. Persistent History

The application automatically saves a history of all the documents you process. This means you can close your browser and come back later, and your previously processed documents will still be available in the History sidebar.

*   **Accessing History:** Click on any document listed in the History sidebar to instantly reload its original content and Markdown conversion.
*   **Clearing History:** There will be an option to clear your entire document history if you wish.

### 3.8. Search Functionality

Easily find specific content within your documents:

*   **Search Bar:** A search bar will be available, allowing you to type in keywords or phrases.
*   **Real-time Results:** As you type, the application will highlight matching terms in both the original document and the Markdown preview.
*   **Navigation:** You can navigate between search results to quickly jump to relevant sections.

### 3.9. File Metadata Display

For each processed document, the application will display useful metadata, such as:

*   **File Name:** The original name of your uploaded file.
*   **File Type:** The format of the uploaded file (e.g., PDF, DOCX, PNG).
*   **Upload Date:** The date and time when the document was processed.

### 3.10. Auto-save Functionality

Any changes you make to the Markdown content in the editor will be automatically saved locally in your browser. This ensures that your work is not lost, even if you accidentally close the tab or your computer shuts down.

### 3.11. Keyboard Shortcuts

For power users, the application will support various keyboard shortcuts to speed up common actions. These will be listed within the application or in a dedicated help section.

## 4. Troubleshooting

*   **File Upload Errors:** If your file fails to upload, ensure it is one of the supported formats and within a reasonable size limit. Check your internet connection.
*   **Processing Delays:** Large documents or complex files may take longer to process. Please be patient and observe the progress indicators.
*   **Inaccurate Conversion:** While the application strives for accuracy, complex layouts or highly stylized documents might result in minor conversion discrepancies. You can always edit the Markdown manually.

If you encounter any persistent issues, please refer to the technical documentation or contact support.

Thank you for using the Document Parser Web Application!



## 5. Document Processing Flow Diagrams

This section provides visual representations of the end-to-end document processing workflows.

### 5.1. General Document Processing Flow

![General Document Processing Flow](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866641692_na1fn_L2hvbWUvdWJ1bnR1L2dlbmVyYWxfZmxvdw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDE2OTJfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyZGxibVZ5WVd4ZlpteHZkdy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=EAwvHBNXH9rU798lpU-CucYQ2HXA-vWMXyousJEWMyrEyiKd2s4zg3W5~bJew0Zyrts26dpUFq~njzWUe-QxK4Q7sZ1syi6nrlCXETkylA4NzzRH-7U3LpIoB3Gxw6xcHzwaaA63N7Z8w3wVER1k3Z9AQG30O4uHgrIZItEe9PKlpyJox0tPUtHzPnLjmORPY3rF0Hd07wAEbt~c-2IOuV7wb~yFps2kw58GCR2skzqVE5Q9rv8rDyNnIT7wqM9IIZfpT2Uu5gpbbHyQ-SI5M6au5urPv3QgeBAcXQXwR7JsYJYx1hNa8XPM~1fnD~-RTaAgYK8V-ts7aZ~Gr0s6hA__)

### 5.2. PDF Document Processing Flow

![PDF Document Processing Flow](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866641693_na1fn_L2hvbWUvdWJ1bnR1L3BkZl9mbG93.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDE2OTNfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzQmtabDltYkc5My5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=VI~yIFamuBIE~6iZ103mDFAgEUrZZwo8CTBT9YqexwIV~AKhOucQoVeS-3Cp3md8bRPuvLTbrFsD3CqHmgNVz01BFUD3Bp4Z1q36r3cFRQB~F86HnCjY5dqCs3HvBgnUs2mJK2cL3OWkj4pRGoZOGWiuP1VQdCsduvj3nqd0AEcpd2x3JHStccV5xDZv1NoI2dsxZlU22tpCLbQAHAm-czkdJbJ2SHeM46gvqdEKrSvne0xgJLHbhfz0fbBRiXplo-7cug7kPNlaxGUpM5DuAgfzJ-YVmblCRakopduZJ6BDaS8mFG4uoKl7N1AlYZHAnXvmqTuhL4~TdFG18Xl07Q__)

### 5.3. DOCX Document Processing Flow

![DOCX Document Processing Flow](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866641693_na1fn_L2hvbWUvdWJ1bnR1L2RvY3hfZmxvdw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDE2OTNfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyUnZZM2hmWm14dmR3LnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=Bi5-pd19hAh2SDdMu904i5oKj7QliZJyPSsDdc5HEmVkRmq404fGsPRGQrqAdBPUa9b4pCkOXMR-duLI0wSOYyAltEpNP2428FOgGMvpTBvVCdTqlo06UBb8r-ZJQPC1t0~~67QAJU-Ywb2~8IT2m7Kx6Ih9kNAe0yeVsrc2nMG3PflWvnoPp2Hed0berLc8VSINgwJB-2LY3VHnedftch5UcbHbpelbmhcBYBc9vQ7sXRBPBU8I-o4aGfBeKqwjxZPZ8-a3nuZ-~eBynSiWH7HQmad25~c4n4vtJkMdmLwA4J3YQfUQHMw~1JN5-RU7oHWns0WQhyIeYY~eDTthvQ__)

### 5.4. Image (PNG/JPG) Document Processing Flow

![Image (PNG/JPG) Document Processing Flow](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866641694_na1fn_L2hvbWUvdWJ1bnR1L2ltYWdlX2Zsb3c.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDE2OTRfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwybHRZV2RsWDJac2IzYy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=td~qLZm-Su~SE7eN3e84VhnVn7dALcrQna0aRZEjXlTq507CXIGy3IA6R803dn2VbPT5S1EWD2Vxf5uQhhtQnCG7KbolhrOuA9R5lp9I2ZT5XKqhBXfmtcktUjelRBb0rSyIr38w~NPjZbuWmvJdK1ZpUYNae1lPBlJgq12YhEhRsZow6Lv3QW7p6gDc9KCOke4JKGbrCdQa5zsSWcNrfRgf57Z9h285-gfDPpvLG4z4vcCWxUZgCyCZKR2WiNgJg~hb4tTalLDlt~k1YZcsLUbnDVJAxAwVweaFsfaDwGFrvSdrp71uPNn3jxOXC68ZCx~kP58IdQBIfxa59xI6eg__)


