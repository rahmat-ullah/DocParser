# Document parser for pdf, docx, excel, ppt, text, image (png, jpg)

Create a document parsing web application using Next.js that allows seamless conversion of multiple file formats to markdown with the following specifications:

Technical Requirements:
- Implement file upload functionality supporting PDF, DOCX, XLSX, PPT, TXT, PNG, and JPG formats
- Create a dual-panel interface with the original document viewer on the left and markdown preview on the right
- Develop a parser system that accurately converts uploaded documents to markdown format
- Enable bi-directional synchronization between document and markdown views
- Add click-to-highlight functionality for navigating between markdown sections and source document
- Implement export functionality for both markdown and JSON formats
- Create a persistent history system for previously processed documents

UI/UX Requirements:
- Design a clean, modern interface using the following color palette:
  - Primary: Dark Blue (#1a237e)
  - Secondary: White (#ffffff)
  - Accent: Black (#000000)
- Include a toggle switch for markdown/preview mode
- Add a clear file upload area with drag-and-drop support
- Create an organized history sidebar with recent documents
- Implement responsive design for various screen sizes
- Add loading states and progress indicators for file processing

Additional Features:
- Real-time markdown preview
- Search functionality within documents
- File metadata display (size, type, upload date)
- Error handling for unsupported files
- Auto-save functionality
- Keyboard shortcuts for common actions

For the data processing:
The platform should be able to identify, image, diagrams, table, math and other complex data. Then it should use openai vision model to get a descriptieve results for any image or diagram that describe the figure in a way so that anyone can understand what is the figure is about and what are the context without looking at the image or diagram. The math content should be provided in a latex format. Table should be extracted in a formated markdown table. You can use openai or anthropic models. I have the api keys. solution focusing on performance, accessibility, and user experience.