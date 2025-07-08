# Technical Architecture and Tech Stack

This document outlines the technical architecture and the selected technology stack for the document parsing web application. The choices have been made to ensure performance, scalability, and a high-quality user experience, while also considering the specific requirements of the project.

## 1. System Architecture

The application will follow a microservices-oriented architecture, separating the frontend, backend, and document processing functionalities. This approach provides several advantages, including:

*   **Scalability:** Each service can be scaled independently based on its specific load.
*   **Flexibility:** Different technologies can be used for each service, allowing for the best tool to be chosen for each job.
*   **Maintainability:** Services are smaller and more focused, making them easier to develop, test, and maintain.

The architecture consists of three main components:

1.  **Frontend Application:** A Next.js application responsible for the user interface and user experience.
2.  **Backend Service:** A Node.js service built with Next.js API routes that handles user authentication, file uploads, and communication with the document processing service.
3.  **Document Processing Service:** A Python-based service that performs the core document parsing, conversion, and AI-powered analysis.

![System Architecture Diagram](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866642200_na1fn_L2hvbWUvdWJ1bnR1L3N5c3RlbV9hcmNoaXRlY3R1cmU.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDIyMDBfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzTjVjM1JsYlY5aGNtTm9hWFJsWTNSMWNtVS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=hq2q58mYwYfyBdCxf~UYf8wLaTE7JJJGrFVu~nsce4dySUGDjndkgbGyV2c2zFDg-8q8h8-qW5-4NRTLzmLnpsbIS5EjJqNy43k-vO38DT2E4OBgPLTb7iJZhhFrUijnF7S6iP67Cne6LZG6zbK42JnzGPL8PAqA8ChAJFVBdRe6lcuzi3ZohZ-5TVmzlAozbp3CZaS8IQpdE6rR3iekb8wIDTvaUz2wbPvuNW4DSIFOPkFCnY2hAfQsjnqbx1NeKfx0mMIrvxV3N7gkONIUG~FGhTYwmjbhwkVJJFklzf83E7kz~taukI8eL99V6-8PNV1guSxPluzAqCAjGtcnpg__)

*(A diagram will be generated and inserted here in a later step)*

## 2. Technology Stack

### 2.1. Frontend

*   **Framework:** [Next.js](https://nextjs.org/) (with TypeScript) - A React framework that provides a robust set of features for building modern web applications, including server-side rendering (SSR) and static site generation (SSG) for optimal performance and SEO.
*   **UI Library:** [Tailwind CSS](https://tailwindcss.com/) - A utility-first CSS framework for rapidly building custom user interfaces. It will be used in conjunction with a component library to ensure a clean and modern design.
*   **Component Library:** [shadcn/ui](https://ui.shadcn.com/) - A collection of re-usable components built with Radix UI and Tailwind CSS, which will accelerate UI development and ensure consistency.
*   **State Management:** [Zustand](https://github.com/pmndrs/zustand) - A small, fast, and scalable state-management solution for React.
*   **File Uploads:** [React Dropzone](https://react-dropzone.js.org/) - A library to create a drag-and-drop zone for file uploads.

### 2.2. Backend

*   **Framework:** [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction) - For handling API requests from the frontend, managing user sessions, and orchestrating the document processing workflow.
*   **Real-time Communication:** [Socket.IO](https://socket.io/) - For providing real-time updates to the frontend on the status of document processing.

### 2.3. Document Processing Service

*   **Language:** [Python](https://www.python.org/) - The ideal language for this service due to its extensive ecosystem of libraries for data processing, machine learning, and AI.
*   **Framework:** [Flask](https://flask.palletsprojects.com/) - A lightweight and flexible web framework for Python, perfect for creating a dedicated microservice for document processing.
*   **Document Parsing Libraries:**
    *   **PDF:** [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) - A high-performance Python library for data extraction and manipulation of PDF documents.
    *   **DOCX:** [python-docx](https://python-docx.readthedocs.io/en/latest/) - For parsing and converting Microsoft Word documents.
    *   **XLSX:** [openpyxl](https://openpyxl.readthedocs.io/en/latest/) - For reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files.
    *   **PPTX:** [python-pptx](https://python-pptx.readthedocs.io/en/latest/) - For creating and updating PowerPoint presentations.
    *   **TXT:** Standard Python file I/O.
    *   **Images (PNG, JPG):** [Pillow](https://pillow.readthedocs.io/en/stable/) - The Python Imaging Library, for opening, manipulating, and saving many different image file formats.
*   **AI and OCR:**
    *   [OpenAI Vision API](https://platform.openai.com/docs/guides/vision) - For performing Optical Character Recognition (OCR) on images and scanned documents, as well as for generating descriptive text for images and diagrams.
*   **Math Content:**
    *   [latexify-py](https://github.com/google/latexify_py) - To convert Python functions to LaTeX.
*   **Table Extraction:** Custom logic will be implemented to extract tables from various document formats and convert them into Markdown tables.

### 2.4. Database

*   **History System:** [localForage](https://localforage.github.io/localForage/) - A fast and simple storage library that improves the offline experience of your web app by using asynchronous storage (IndexedDB or WebSQL) with a simple, `localStorage`-like API. This will be used for the persistent history of processed documents on the client-side.

## 3. Rationale for Technology Choices

*   **Next.js** was chosen as the primary frontend framework because it was explicitly requested by the user and is an excellent choice for building modern, performant, and SEO-friendly web applications.
*   A **separate Python service for document processing** is crucial for performance and to leverage the best-in-class libraries available in the Python ecosystem for this task. This also allows for independent scaling of the processing service.
*   The **OpenAI Vision API** is a powerful tool that directly addresses the user's requirement for AI-powered image and diagram analysis.
*   The use of **Tailwind CSS and shadcn/ui** will enable the rapid development of a clean, modern, and responsive user interface that meets the specified UI/UX requirements.
*   **localForage** provides a simple and effective way to implement the persistent history feature without the need for a complex server-side database, which is suitable for the initial phase of the project.




![System Architecture Diagram](https://private-us-east-1.manuscdn.com/sessionFile/2ToCxeW8a0uvYxrpPnJu4V/sandbox/tCqJpsSQkvuVYGOOPsupJH-images_1751866642199_na1fn_L2hvbWUvdWJ1bnR1L3N5c3RlbV9hcmNoaXRlY3R1cmU.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMlRvQ3hlVzhhMHV2WXhycFBuSnU0Vi9zYW5kYm94L3RDcUpwc1NRa3Z1VllHT09Qc3VwSkgtaW1hZ2VzXzE3NTE4NjY2NDIxOTlfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzTjVjM1JsYlY5aGNtTm9hWFJsWTNSMWNtVS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=MdKRybvGtV8FPS0kN7W4A-Z7qCnf3LjK4zBGa-wdrBiFAdyqdbH1V7YcfM4vYwOYInvd1loeiojW3l~FCt8vRPzpYIDsvNnCW49Vp5oAtNY3ff~aQka1zVD2ZpVqEyi8bnru2G3VHhVj7SNJ5u2WNwHpanaA23hckTA6BdgGFP19Kw5L3lZ~3H807YXic4ONNf3gTDeH50wP5oeXTuYNZNnY3tu4yFamDp5MNrazB0F1qudIfx~6inHaDJkWcvAmbSV~RM-yjwstk11l0yfIjrIYTBqZyLX9ot-DRpOBNe-SQI~Z64zPqL2oLY8uBzOlBeTeOC3LMvTMyqPXMCQt-g__)


