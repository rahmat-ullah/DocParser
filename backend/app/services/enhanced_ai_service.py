"""
Enhanced AI service with document type detection and specialized model selection.
Provides intelligent document analysis with context-aware processing.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import os

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_openai_config
from app.services.ai_service import AIService, AIServiceError


logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Document type classification."""
    SCIENTIFIC_PAPER = "scientific_paper"
    FINANCIAL_REPORT = "financial_report"
    TECHNICAL_MANUAL = "technical_manual"
    LEGAL_DOCUMENT = "legal_document"
    GENERAL = "general"


class AnalysisComplexity(Enum):
    """Analysis complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class DocumentContext:
    """Context information for document analysis."""
    document_type: DocumentType
    complexity: AnalysisComplexity
    subject_matter: str
    key_elements: List[str]
    total_pages: int
    language: str = "en"
    
    
class StructuredImageAnalysis(BaseModel):
    """Structured output for image analysis."""
    id: str
    type: str
    title: str
    caption: str
    description: str
    contextual_summary: str
    linked_entities: List[Dict[str, str]]
    semantic_tags: List[str]
    technical_details: Dict[str, Any]
    confidence_score: float
    

class EnhancedAIService(AIService):
    """Enhanced AI service with document type detection and specialized processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.document_context: Optional[DocumentContext] = None
        
    async def analyze_document_type(self, text_sample: str, metadata: Dict[str, Any]) -> DocumentType:
        """
        Analyze document type from text sample and metadata.
        
        Args:
            text_sample: Sample text from the document
            metadata: Document metadata
            
        Returns:
            Detected document type
        """
        try:
            prompt = f"""
            Analyze the following document sample and metadata to determine the document type.
            
            Document metadata: {json.dumps(metadata, indent=2)}
            
            Text sample:
            ---
            {text_sample[:2000]}
            ---
            
            Classify this document as one of:
            - scientific_paper: Academic papers, research articles, journals
            - financial_report: Financial statements, annual reports, SEC filings
            - technical_manual: User manuals, technical documentation, specifications
            - legal_document: Contracts, legal briefs, regulations, policies
            - general: General business documents, presentations, reports
            
            Respond with only the classification (e.g., "scientific_paper").
            """
            
            response = await self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a document classification expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            classification = response.choices[0].message.content.strip().lower()
            
            # Map response to enum
            type_mapping = {
                "scientific_paper": DocumentType.SCIENTIFIC_PAPER,
                "financial_report": DocumentType.FINANCIAL_REPORT,
                "technical_manual": DocumentType.TECHNICAL_MANUAL,
                "legal_document": DocumentType.LEGAL_DOCUMENT,
                "general": DocumentType.GENERAL
            }
            
            return type_mapping.get(classification, DocumentType.GENERAL)
            
        except Exception as e:
            logger.warning(f"Document type detection failed: {e}")
            return DocumentType.GENERAL
    
    async def determine_analysis_complexity(self, text_sample: str, image_count: int) -> AnalysisComplexity:
        """
        Determine the complexity level of analysis required.
        
        Args:
            text_sample: Sample text from the document
            image_count: Number of images in the document
            
        Returns:
            Analysis complexity level
        """
        # Simple heuristics for complexity
        if image_count > 10:
            return AnalysisComplexity.COMPLEX
        
        # Check for complex content indicators
        complex_indicators = [
            r'\b(algorithm|methodology|statistical|analysis|regression|correlation)\b',
            r'\b(financial|revenue|EBITDA|balance sheet|cash flow)\b',
            r'\b(specification|protocol|API|interface|architecture)\b',
            r'\b(regulation|compliance|liability|jurisdiction|statute)\b'
        ]
        
        complexity_score = 0
        for pattern in complex_indicators:
            if re.search(pattern, text_sample, re.IGNORECASE):
                complexity_score += 1
        
        if complexity_score >= 3:
            return AnalysisComplexity.COMPLEX
        elif complexity_score >= 1:
            return AnalysisComplexity.MODERATE
        else:
            return AnalysisComplexity.SIMPLE
    
    def get_model_for_document_type(self, doc_type: DocumentType) -> str:
        """Get the appropriate model for the document type."""
        model_mapping = self.config.get("document_type_models", {})
        return model_mapping.get(doc_type.value, self.config["vision_model"])
    
    async def analyze_image_with_context(
        self, 
        base64_img: str, 
        context: Dict[str, Any],
        document_context: Optional[DocumentContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze image with enhanced context awareness.
        
        Args:
            base64_img: Base64-encoded image
            context: Image context information
            document_context: Document-level context
            
        Returns:
            Enhanced structured metadata
        """
        # Use document context if available
        if document_context:
            model = self.get_model_for_document_type(document_context.document_type)
        else:
            model = self.config["vision_model"]
        
        # Build enhanced system prompt based on document type
        system_prompt = self._build_context_aware_prompt(document_context)
        
        # Prepare context message
        context_msg = self._build_context_message(context, document_context)
        
        try:
            if self.config.get("use_structured_outputs", False):
                return await self._analyze_with_structured_output(
                    base64_img, system_prompt, context_msg, model, context
                )
            else:
                return await self._analyze_with_json_mode(
                    base64_img, system_prompt, context_msg, model, context
                )
                
        except Exception as e:
            logger.error(f"Enhanced image analysis failed: {e}")
            # Fallback to basic analysis
            return await super().analyze_image_structured(base64_img, context)
    
    def _build_context_aware_prompt(self, document_context: Optional[DocumentContext]) -> str:
        """Build context-aware system prompt."""
        base_prompt = """You are an expert document analysis assistant specializing in extracting detailed, accurate metadata from visual elements."""
        
        if not document_context:
            return base_prompt
        
        type_specific_instructions = {
            DocumentType.SCIENTIFIC_PAPER: """
            Focus on:
            - Experimental data, graphs, and statistical visualizations
            - Methodology diagrams and process flows
            - Research findings and data interpretations
            - Mathematical equations and formulas
            - Figure citations and academic references
            """,
            DocumentType.FINANCIAL_REPORT: """
            Focus on:
            - Financial charts, graphs, and performance metrics
            - Balance sheets, income statements, and cash flow diagrams
            - Market analysis and trend visualizations
            - Financial ratios and key performance indicators
            - Regulatory compliance information
            """,
            DocumentType.TECHNICAL_MANUAL: """
            Focus on:
            - System architecture and component diagrams
            - Process workflows and procedural steps
            - Technical specifications and parameters
            - User interface screenshots and navigation
            - Safety warnings and operational guidelines
            """,
            DocumentType.LEGAL_DOCUMENT: """
            Focus on:
            - Legal frameworks and process diagrams
            - Compliance flowcharts and decision trees
            - Organizational charts and responsibility matrices
            - Timeline diagrams and case progressions
            - Regulatory requirements and legal citations
            """,
            DocumentType.GENERAL: """
            Focus on:
            - General business processes and workflows
            - Organizational information and structures
            - Data presentations and summaries
            - Communication and presentation materials
            """
        }
        
        specific_instructions = type_specific_instructions.get(
            document_context.document_type, 
            type_specific_instructions[DocumentType.GENERAL]
        )
        
        return f"{base_prompt}\n\nDocument Type: {document_context.document_type.value}\n{specific_instructions}"
    
    def _build_context_message(
        self, 
        context: Dict[str, Any], 
        document_context: Optional[DocumentContext]
    ) -> str:
        """Build enhanced context message."""
        base_context = f"""
        Image Context:
        - File: {context.get('filename', 'Unknown')}
        - Page: {context.get('page', 'Unknown')}
        - Section: {context.get('section', 'Unknown')}
        """
        
        if document_context:
            doc_context = f"""
            Document Context:
            - Type: {document_context.document_type.value}
            - Complexity: {document_context.complexity.value}
            - Subject: {document_context.subject_matter}
            - Total Pages: {document_context.total_pages}
            - Key Elements: {', '.join(document_context.key_elements)}
            """
            return base_context + doc_context
        
        return base_context
    
    def _log_llm_response(self, content: str, model: str, mode: str, context_msg: str) -> None:
        """Log the LLM raw response to a file with additional metadata and context."""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"llm_response_{timestamp}_{mode}.log"
        filepath = os.path.join(log_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as log_file:
            log_file.write(f"Model: {model}\n")
            log_file.write(f"Mode: {mode}\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(f"Context: {context_msg}\n")
            log_file.write("="*50 + "\n")
            log_file.write("Response:\n")
            log_file.write(content)
    
    async def _analyze_with_structured_output(
        self, 
        base64_img: str, 
        system_prompt: str, 
        context_msg: str, 
        model: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze image using structured outputs (if supported)."""
        # Generate context-aware ID
        filename = context.get('filename', 'unknown')
        page = context.get('page', 1)
        section = context.get('section', '')
        figure_id = f"fig_{page}_{abs(hash(filename))}"
        
        enhanced_prompt = f"""
        {system_prompt}

        Analyze this image and provide structured metadata optimized for canonical markdown conversion.
        
        CRITICAL: Classify the image type accurately:
        - "diagram" for: flowcharts, process diagrams, system architecture, UML diagrams, decision trees
        - "chart" for: bar charts, pie charts, line graphs, scatter plots, histograms
        - "table" for: data tables, spreadsheet-like content, structured data grids
        - "image" for: photographs, illustrations, screenshots, general images
        - "formula" for: mathematical equations, formulas, scientific notation
        
        DETAILED ANALYSIS REQUIREMENTS:
        
        1. CONTEXTUAL SUMMARY: Write 2-4 sentences explaining:
           - How this visual relates to the broader document context
           - Why it's significant or important to include
           - What specific purpose it serves in the document
           - What key message or insight it conveys
        
        2. KEY FINDINGS (for technical_details):
           - Extract 5-15 specific, concrete observations
           - Focus on measurable facts, not generic descriptions
           - Examples: "Shows 25% increase in revenue", "Contains 4 decision points", "Displays temperature range 0-100°C"
           - Avoid vague statements like "shows information" or "contains data"
        
        3. FLOW STEPS (for diagrams only):
           - Provide 3-10 numbered steps describing the process flow
           - Be specific about what happens at each step
           - Include decision points, inputs, outputs, and transformations
           - Example: "Input data is validated for format compliance", "System checks user authentication credentials"
        
        4. DATA POINTS (for charts/tables):
           - Extract 5-20 specific numerical values, percentages, or measurements
           - Include units and context where visible
           - Examples: "Revenue: $2.5M", "Growth rate: 15%", "Temperature: 68°F"
           - Identify trends, peaks, minimums, maximums
        
        5. DIAGRAM COMPONENTS (for diagrams):
           - List 3-10 specific components, modules, or elements visible
           - Use actual names/labels from the diagram
           - Examples: "User Authentication Module", "Database Connection Pool", "Payment Gateway"
        
        6. DESCRIPTION: Write 2-5 sentences with:
           - Clear, specific details about what is shown
           - Actual content rather than generic statements
           - Technical accuracy where applicable
           - Present tense, active voice
        
        Provide response in JSON format with the following structure:
        {{
            "id": "{figure_id}",
            "type": "diagram|chart|table|image|formula",
            "title": "Specific descriptive title (not generic)",
            "caption": "Detailed caption explaining the visual content",
            "description": "Comprehensive 2-5 sentence description with specific details",
            "contextual_summary": "2-4 sentences explaining relevance and significance in document context",
            "linked_entities": [
                {{"type": "concept|person|organization|metric", "value": "specific_entity_name", "confidence": 0.8}}
            ],
            "semantic_tags": ["specific_domain_tags", "content_type", "topic_areas"],
            "technical_details": {{
                "data_points": ["Specific measurements with units", "Percentage: 25%", "Value: $1.2M"],
                "measurements": {{"width": "value", "height": "value", "scale": "value"}},
                "key_findings": ["Specific concrete observations", "Measurable facts", "Notable patterns"],
                "flow_steps": ["Step 1: Specific action", "Step 2: Decision point", "Step 3: Output generated"],
                "diagram_components": ["Component A", "Module B", "System C"]
            }},
            "confidence_score": 0.85,
            "source": {{
                "filename": "{filename}",
                "page": {page},
                "documentSection": "{section}"
            }},
            "location": {{"x": 0, "y": 0, "width": 0, "height": 0}},
            "textReferences": [],
            "aiAnnotations": {{
                "objectsDetected": ["specific_objects_detected"],
                "ocrText": "Any text visible in the image",
                "language": "en",
                "explanationGenerated": "Detailed explanation with specific steps for diagrams or insights for charts"
            }},
            "relations": {{"explains": [], "referencedBy": []}}
        }}
        
        REMEMBER: Be specific, not generic. Extract actual content, not placeholder descriptions.
        """
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enhanced_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this image and provide structured metadata.{context_msg}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                        }
                    ]
                }
            ],
            max_tokens=self.config.get("max_tokens", 4000),
            temperature=self.config.get("temperature", 0.1),
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Log LLM raw response with metadata
        self._log_llm_response(content, model, "structured_output", context_msg)

        return json.loads(content)
    
    async def _analyze_with_json_mode(
        self, 
        base64_img: str, 
        system_prompt: str, 
        context_msg: str, 
        model: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze image using JSON mode with canonical markdown format support."""
        # Generate context-aware ID
        filename = context.get('filename', 'unknown')
        page = context.get('page', 1)
        section = context.get('section', '')
        figure_id = f"fig_{page}_{abs(hash(filename))}"
        
        enhanced_prompt = f"""
        {system_prompt}

        Analyze this image and provide structured metadata optimized for canonical markdown conversion.
        
        CRITICAL: Classify the image type accurately:
        - "diagram" for: flowcharts, process diagrams, system architecture, UML diagrams, decision trees
        - "chart" for: bar charts, pie charts, line graphs, scatter plots, histograms
        - "table" for: data tables, spreadsheet-like content, structured data grids
        - "image" for: photographs, illustrations, screenshots, general images
        - "formula" for: mathematical equations, formulas, scientific notation
        
        DETAILED ANALYSIS REQUIREMENTS:
        
        1. CONTEXTUAL SUMMARY: Write 2-20 sentences explaining:
           - How this visual relates to the broader document context
           - Why it's significant or important to include
           - What specific purpose it serves in the document
           - What key message or insight it conveys
        
        2. KEY FINDINGS (for technical_details):
           - Extract 5-25 specific, concrete observations
           - Focus on measurable facts, not generic descriptions
           - Examples: "Shows 25% increase in revenue", "Contains 4 decision points", "Displays temperature range 0-100°C"
           - Avoid vague statements like "shows information" or "contains data"
        
        3. FLOW STEPS (for diagrams only):
           - Provide 3-20 numbered steps describing the process flow
           - Be specific about what happens at each step
           - Include decision points, inputs, outputs, and transformations
           - Example: "Input data is validated for format compliance", "System checks user authentication credentials"
        
        4. DATA POINTS (for charts/tables):
           - Extract 5-30 specific numerical values, percentages, or measurements
           - Include units and context where visible
           - Examples: "Revenue: $2.5M", "Growth rate: 15%", "Temperature: 68°F"
           - Identify trends, peaks, minimums, maximums
        
        5. DIAGRAM COMPONENTS (for diagrams):
           - List 3-50 specific components, modules, or elements visible
           - Use actual names/labels from the diagram
           - Examples: "User Authentication Module", "Database Connection Pool", "Payment Gateway"
        
        6. DESCRIPTION: Write 2-15 sentences with:
           - Clear, specific details about what is shown
           - Actual content rather than generic statements
           - Technical accuracy where applicable
           - Present tense, active voice
        
        Provide response in JSON format with the following structure:
        {{
            "id": "{figure_id}",
            "type": "diagram|chart|table|image|formula",
            "title": "Specific descriptive title (not generic)",
            "caption": "Detailed caption explaining the visual content",
            "description": "Comprehensive 2-5 sentence description with specific details",
            "contextual_summary": "2-30 sentences explaining relevance and significance in document context",
            "linked_entities": [
                {{"type": "concept|person|organization|metric", "value": "specific_entity_name", "confidence": 0.8}}
            ],
            "semantic_tags": ["specific_domain_tags", "content_type", "topic_areas"],
            "technical_details": {{
                "data_points": ["Specific measurements with units", "Percentage: 25%", "Value: $1.2M"],
                "measurements": {{"width": "value", "height": "value", "scale": "value"}},
                "key_findings": ["Specific concrete observations", "Measurable facts", "Notable patterns"],
                "flow_steps": ["Step 1: Specific action", "Step 2: Decision point", "Step 3: Output generated"],
                "diagram_components": ["Component A", "Module B", "System C"]
            }},
            "confidence_score": 0.85,
            "source": {{
                "filename": "{filename}",
                "page": {page},
                "documentSection": "{section}"
            }},
            "location": {{"x": 0, "y": 0, "width": 0, "height": 0}},
            "textReferences": [],
            "aiAnnotations": {{
                "objectsDetected": ["specific_objects_detected"],
                "ocrText": "Any text visible in the image",
                "language": "en",
                "explanationGenerated": "Detailed explanation with specific steps for diagrams or insights for charts"
            }},
            "relations": {{"explains": [], "referencedBy": []}}
        }}
        
        REMEMBER: Be specific, not generic. Extract actual content, not placeholder descriptions.
        """
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enhanced_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this image and provide structured metadata.{context_msg}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                        }
                    ]
                }
            ],
            max_tokens=self.config.get("max_tokens", 4000),
            temperature=self.config.get("temperature", 0.1)
        )
        
        content = response.choices[0].message.content
        
        # Log LLM raw response with metadata
        self._log_llm_response(content, model, "json_mode", context_msg)
        
        # Extract JSON from response
        try:
            # Try to parse as JSON directly
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                raise AIServiceError("Failed to parse JSON response")
    
    async def generate_contextual_summary(
        self, 
        document_elements: List[Dict[str, Any]], 
        document_context: DocumentContext
    ) -> str:
        """
        Generate a contextual summary of the entire document.
        
        Args:
            document_elements: List of all document elements (text, images, tables)
            document_context: Document context information
            
        Returns:
            Contextual summary of the document
        """
        if not document_elements:
            return ""
        
        # Use reasoning model for complex documents
        model = self.config["reasoning_model"] if (
            self.config.get("use_reasoning_model_for_complex_docs", False) and 
            document_context.complexity == AnalysisComplexity.COMPLEX
        ) else self.config["model"]
        
        # Prepare document overview
        overview = {
            "type": document_context.document_type.value,
            "complexity": document_context.complexity.value,
            "subject_matter": document_context.subject_matter,
            "total_pages": document_context.total_pages,
            "element_count": len(document_elements)
        }
        
        prompt = f"""
        Generate a comprehensive contextual summary of this document based on its elements and metadata.
        
        Document Overview:
        {json.dumps(overview, indent=2)}
        
        Document Elements Summary:
        {json.dumps(document_elements[:50], indent=2)}  # Limit to first 50 elements
        
        Provide a detailed summary that includes:
        1. Main purpose and objectives
        2. Key findings or conclusions
        3. Important visual elements and their significance
        4. Overall structure and organization
        5. Target audience and use cases
        
        Make the summary comprehensive yet concise, suitable for executive review.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are an expert document analyst specializing in {document_context.document_type.value} documents."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=self.config.get("temperature", 0.1)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Contextual summary generation failed: {e}")
            return "Summary generation failed due to an error."
    
    async def set_document_context(
        self, 
        text_sample: str, 
        metadata: Dict[str, Any], 
        image_count: int
    ) -> DocumentContext:
        """
        Set the document context for enhanced analysis.
        
        Args:
            text_sample: Sample text from the document
            metadata: Document metadata
            image_count: Number of images in the document
            
        Returns:
            Document context object
        """
        # Detect document type
        doc_type = await self.analyze_document_type(text_sample, metadata)
        
        # Determine complexity
        complexity = await self.determine_analysis_complexity(text_sample, image_count)
        
        # Extract subject matter (simplified)
        subject_matter = metadata.get("subject", "General document")
        
        # Extract key elements (simplified)
        key_elements = ["text", "images", "tables"] if image_count > 0 else ["text"]
        
        # Create document context
        self.document_context = DocumentContext(
            document_type=doc_type,
            complexity=complexity,
            subject_matter=subject_matter,
            key_elements=key_elements,
            total_pages=metadata.get("pages", 1),
            language=metadata.get("language", "en")
        )
        
        logger.info(f"Document context set: {doc_type.value}, complexity: {complexity.value}")
        return self.document_context


# Global enhanced service instance
_enhanced_ai_service: Optional[EnhancedAIService] = None


async def get_enhanced_ai_service() -> EnhancedAIService:
    """Get or create the global enhanced AI service instance."""
    global _enhanced_ai_service
    if _enhanced_ai_service is None:
        _enhanced_ai_service = EnhancedAIService()
    return _enhanced_ai_service


async def shutdown_enhanced_ai_service() -> None:
    """Shutdown the global enhanced AI service instance."""
    global _enhanced_ai_service
    if _enhanced_ai_service is not None:
        await _enhanced_ai_service.close()
        _enhanced_ai_service = None
