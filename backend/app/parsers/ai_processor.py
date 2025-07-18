"""
AI Processor for enhancing parsed content with AI-generated descriptions.
Handles images (description and table extraction) and math blocks using AI services.
"""

import asyncio
import base64
from io import BytesIO
from PIL import Image
from typing import List, Optional, AsyncGenerator

from ..services.ai_service import get_ai_service
from ..services.enhanced_ai_service import get_enhanced_ai_service, DocumentContext
from ..services.spatial_context_analyzer import SpatialContextAnalyzer, DocumentLayout
from ..services.entity_recognition_service import EntityRecognitionService
from .ast_models import DocumentAST, ImageBlock, MathBlock, TableBlock, ParseProgress
from ..utils.image_analysis_utils import extract_table_from_pil_image
from ..core.config import settings


class AIProcessor:
    """Processor for enhancing document AST with AI-generated content."""
    
    def __init__(self):
        self.document_context: Optional[DocumentContext] = None
        self.enhanced_ai_service = None
        self.spatial_analyzer = SpatialContextAnalyzer()
        self.document_layout: Optional[DocumentLayout] = None
        self.entity_recognition_service = None  # Will be initialized later

    async def process_ast(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """
        Process document AST and enhance with AI-generated content.
        This includes document type detection, contextual analysis, and enhanced descriptions.
        """
        if progress_callback:
            await self._emit_progress(progress_callback, "ai_processing_start", 0.0, "Starting enhanced AI processing")

        # Initialize enhanced AI service
        self.enhanced_ai_service = await get_enhanced_ai_service()
        
        # Step 1: Analyze document context
        await self._analyze_document_context(ast, progress_callback)
        
        # Step 2: Analyze spatial layout and relationships
        await self._analyze_spatial_layout(ast, progress_callback)
        
        # Step 3: Process images with enhanced context
        await self._process_images_with_context(ast, progress_callback)
        
        # Step 3: Process math blocks
        await self._process_math(ast.math, progress_callback)
        
        # Step 4: Generate document summary if enabled
        if settings.enable_contextual_understanding:
            await self._generate_document_summary(ast, progress_callback)

        if progress_callback:
            await self._emit_progress(progress_callback, "ai_processing_complete", 1.0, "Enhanced AI processing completed")

        return ast
    
    async def _analyze_document_context(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Analyze document context for enhanced processing."""
        if progress_callback:
            await self._emit_progress(progress_callback, "document_analysis", 0.1, "Analyzing document context")
        
        try:
            # Extract text sample from document
            text_sample = ""
            for text_block in ast.textBlocks[:10]:  # Sample from first 10 text blocks
                text_sample += text_block.content + "\n"
            
            # Set document context with timeout
            self.document_context = await asyncio.wait_for(
                self.enhanced_ai_service.set_document_context(
                    text_sample=text_sample,
                    metadata=ast.metadata or {},
                    image_count=len(ast.images)
                ),
                timeout=30.0  # 30 second timeout
            )
            
            if progress_callback:
                await self._emit_progress(
                    progress_callback, 
                    "document_analysis_complete", 
                    0.15, 
                    f"Document type: {self.document_context.document_type.value}, complexity: {self.document_context.complexity.value}"
                )
            
            # Perform entity recognition and linking
            await self._perform_entity_recognition(ast, text_sample, progress_callback)
        except asyncio.TimeoutError:
            print("Warning: Document context analysis timed out, using fallback")
            # Create fallback context
            from ..services.enhanced_ai_service import DocumentContext, DocumentType, AnalysisComplexity
            self.document_context = DocumentContext(
                document_type=DocumentType.GENERAL,
                complexity=AnalysisComplexity.SIMPLE,
                subject_matter="General document",
                key_elements=["text"],
                total_pages=1
            )
            if progress_callback:
                await self._emit_progress(
                    progress_callback, 
                    "document_analysis_complete", 
                    0.2, 
                    "Document context analysis timed out, using fallback"
                )
        except Exception as e:
            print(f"Error in document context analysis: {e}")
            # Create fallback context
            from ..services.enhanced_ai_service import DocumentContext, DocumentType, AnalysisComplexity
            self.document_context = DocumentContext(
                document_type=DocumentType.GENERAL,
                complexity=AnalysisComplexity.SIMPLE,
                subject_matter="General document",
                key_elements=["text"],
                total_pages=1
            )
            if progress_callback:
                await self._emit_progress(
                    progress_callback, 
                    "document_analysis_complete", 
                    0.2, 
                    f"Document context analysis failed: {str(e)[:100]}"
                )
    
    async def _perform_entity_recognition(
        self,
        ast: DocumentAST,
        text_sample: str,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Perform entity recognition and linking on the document text."""
        if progress_callback:
            await self._emit_progress(
                progress_callback,
                "entity_recognition_start",
                0.16,
                "Starting entity recognition and linking"
            )
        
        try:
            # Initialize the entity recognition service with OpenAI client
            if self.entity_recognition_service is None:
                self.entity_recognition_service = EntityRecognitionService(self.enhanced_ai_service.client)
            await self.entity_recognition_service.initialize()
            
            # Determine document type for entity extraction
            document_type = (
                self.document_context.document_type.value.lower()
                if self.document_context and self.document_context.document_type
                else "general"
            )
            
            # Extract entities from the text sample
            entity_result = await self.entity_recognition_service.extract_entities(
                text=text_sample,
                document_type=document_type
            )
            
            # Store entity recognition results in AST metadata
            if not ast.metadata:
                ast.metadata = {}
            
            # Convert entity result to serializable format
            ast.metadata["entity_recognition"] = {
                "entities": [
                    {
                        "text": entity.text,
                        "label": entity.label,
                        "start_pos": entity.start_pos,
                        "end_pos": entity.end_pos,
                        "confidence": entity.confidence,
                        "source": entity.source,
                        "linked_entity": {
                            "wikipedia_id": entity.linked_entity.wikipedia_id,
                            "wikidata_id": entity.linked_entity.wikidata_id,
                            "title": entity.linked_entity.title,
                            "description": entity.linked_entity.description,
                            "url": entity.linked_entity.url,
                            "confidence": entity.linked_entity.confidence
                        } if entity.linked_entity else None,
                        "domain_specific_info": entity.domain_specific_info
                    }
                    for entity in entity_result.entities
                ],
                "relationships": [
                    {
                        "entity1_text": rel.entity1_text,
                        "entity2_text": rel.entity2_text,
                        "relationship_type": rel.relationship_type,
                        "confidence": rel.confidence,
                        "context": rel.context
                    }
                    for rel in entity_result.relationships
                ],
                "total_entities": entity_result.total_entities,
                "processing_time": entity_result.processing_time,
                "document_type": entity_result.document_type
            }
            
            if progress_callback:
                await self._emit_progress(
                    progress_callback,
                    "entity_recognition_complete",
                    0.2,
                    f"Entity recognition complete: {entity_result.total_entities} entities found"
                )
                
        except Exception as e:
            # Log the error but don't stop processing
            print(f"Warning: Entity recognition failed: {e}")
            
            if not ast.metadata:
                ast.metadata = {}
            
            ast.metadata["entity_recognition"] = {
                "error": str(e),
                "entities": [],
                "relationships": [],
                "total_entities": 0,
                "processing_time": 0.0,
                "document_type": "unknown"
            }
            
            if progress_callback:
                await self._emit_progress(
                    progress_callback,
                    "entity_recognition_error",
                    0.2,
                    f"Entity recognition failed: {str(e)[:100]}"
                )
    
    async def _analyze_spatial_layout(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Analyze spatial layout and relationships in the document."""
        if progress_callback:
            await self._emit_progress(progress_callback, "spatial_analysis", 0.25, "Analyzing spatial layout")
        
        try:
            # Analyze document layout
            self.document_layout = self.spatial_analyzer.analyze_document_layout(ast)
            
            # Add spatial context to AST metadata
            if not ast.metadata:
                ast.metadata = {}
            
            # Add spatial analysis results to metadata
            ast.metadata["spatial_analysis"] = {
                "total_elements": len(self.document_layout.elements),
                "total_relationships": len(self.document_layout.relationships),
                "pages": len(self.document_layout.page_dimensions),
                "regions": {region: len(elements) for region, elements in self.document_layout.regions.items()}
            }
            
            # Enhance text blocks with spatial context
            await self._enhance_elements_with_spatial_context(ast)
            
            if progress_callback:
                await self._emit_progress(
                    progress_callback, 
                    "spatial_analysis_complete", 
                    0.3, 
                    f"Spatial analysis complete: {len(self.document_layout.elements)} elements, {len(self.document_layout.relationships)} relationships"
                )
                
        except Exception as e:
            print(f"Error in spatial analysis: {e}")
            if progress_callback:
                await self._emit_progress(
                    progress_callback, 
                    "spatial_analysis_error", 
                    0.3, 
                    f"Spatial analysis failed: {str(e)[:100]}"
                )
    
    async def _enhance_elements_with_spatial_context(self, ast: DocumentAST) -> None:
        """Enhance AST elements with spatial context information."""
        if not self.document_layout:
            return
        
        # Enhance text blocks
        for i, text_block in enumerate(ast.textBlocks):
            element_id = f"text_{i}"
            if element_id in self.document_layout.elements:
                spatial_context = self.spatial_analyzer.get_element_context(
                    element_id, self.document_layout
                )
                
                # Add spatial context to text block
                if text_block.spatial_context is None:
                    text_block.spatial_context = {}
                
                text_block.spatial_context.update({
                    "nearby_elements": len(spatial_context.get('nearby_elements', [])),
                    "relationships": len(spatial_context.get('relationships', [])),
                    "semantic_role": spatial_context.get('semantic_context', {}).get('role', 'content'),
                    "section": spatial_context.get('semantic_context', {}).get('section'),
                    "region": self._get_element_region(element_id)
                })
        
        # Enhance images
        for i, image_block in enumerate(ast.images):
            element_id = f"image_{i}"
            if element_id in self.document_layout.elements:
                spatial_context = self.spatial_analyzer.get_element_context(
                    element_id, self.document_layout
                )
                
                # Add spatial context to image block
                if image_block.spatial_context is None:
                    image_block.spatial_context = {}
                
                image_block.spatial_context.update({
                    "nearby_elements": len(spatial_context.get('nearby_elements', [])),
                    "relationships": len(spatial_context.get('relationships', [])),
                    "semantic_role": spatial_context.get('semantic_context', {}).get('role', 'illustration'),
                    "section": spatial_context.get('semantic_context', {}).get('section'),
                    "region": self._get_element_region(element_id)
                })
        
        # Enhance tables
        for i, table_block in enumerate(ast.tables):
            element_id = f"table_{i}"
            if element_id in self.document_layout.elements:
                spatial_context = self.spatial_analyzer.get_element_context(
                    element_id, self.document_layout
                )
                
                # Add spatial context to table block
                if table_block.spatial_context is None:
                    table_block.spatial_context = {}
                
                table_block.spatial_context.update({
                    "nearby_elements": len(spatial_context.get('nearby_elements', [])),
                    "relationships": len(spatial_context.get('relationships', [])),
                    "semantic_role": spatial_context.get('semantic_context', {}).get('role', 'data_presentation'),
                    "section": spatial_context.get('semantic_context', {}).get('section'),
                    "region": self._get_element_region(element_id)
                })
    
    def _get_element_region(self, element_id: str) -> Optional[str]:
        """Get the region type for an element."""
        if not self.document_layout:
            return None
        
        for region_type, element_ids in self.document_layout.regions.items():
            if element_id in element_ids:
                return region_type
        return None
    
    async def _process_images_with_context(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process images with enhanced context awareness."""
        if not ast.images:
            return
        
        if progress_callback:
            await self._emit_progress(progress_callback, "enhanced_image_processing", 0.3, "Processing images with context")
        
        # Determine total steps
        total_steps = len(ast.images)
        if settings.extract_tables_from_images_enabled:
            total_steps *= 2
        
        current_step = 0
        all_new_tables: List[TableBlock] = []
        
        # Process in batches
        batch_size = settings.ai_processor_image_batch_size or 3
        
        for i in range(0, len(ast.images), batch_size):
            batch_images = ast.images[i:i + batch_size]
            
            tasks = []
            for idx_in_batch, image_block in enumerate(batch_images):
                original_idx = i + idx_in_batch
                image_name = f"image_{original_idx}_p{image_block.page if image_block.page is not None else 'unk'}"
                
                tasks.append(self._process_single_image_with_context(
                    image_block,
                    image_name,
                    progress_callback,
                    current_step + (idx_in_batch * (2 if settings.extract_tables_from_images_enabled else 1)),
                    total_steps
                ))
            
            # Run batch concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, TableBlock):
                    all_new_tables.append(result)
                elif isinstance(result, Exception):
                    print(f"Error during enhanced image processing: {result}")
            
            current_step += len(batch_images) * (2 if settings.extract_tables_from_images_enabled else 1)
            
            # Update progress
            if progress_callback:
                processed_count = min(i + batch_size, len(ast.images))
                await self._emit_progress(
                    progress_callback,
                    "enhanced_image_batch_processed",
                    0.3 + (current_step / total_steps) * 0.4,  # 30% to 70% of total progress
                    f"Processed {processed_count}/{len(ast.images)} images with enhanced context"
                )
        
        # Add extracted tables to AST
        if all_new_tables:
            ast.tables.extend(all_new_tables)
    
    async def _process_single_image_with_context(
        self,
        image_block: ImageBlock,
        image_name: str,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]],
        base_step: int,
        total_steps: int
    ) -> Optional[TableBlock]:
        """Process a single image with enhanced context."""
        current_step = base_step
        
        # 1. Enhanced image description
        if not image_block.alt_text or image_block.alt_text.startswith("Image from"):
            try:
                await self._describe_image_with_context(image_block)
            except Exception as e:
                print(f"Error describing {image_name} with context: {e}")
                if not image_block.alt_text:
                    image_block.alt_text = "Image (enhanced description failed)"
        
        current_step += 1
        if progress_callback:
            await self._emit_progress(
                progress_callback,
                "enhanced_image_description",
                current_step / total_steps if total_steps > 0 else 0,
                f"Enhanced description for {image_name}"
            )
        
        # 2. Table extraction with context
        extracted_table: Optional[TableBlock] = None
        if settings.extract_tables_from_images_enabled:
            try:
                image_bytes = base64.b64decode(image_block.data)
                pil_image = Image.open(BytesIO(image_bytes))
                
                extracted_table = await extract_table_from_pil_image(pil_image, image_name)
                pil_image.close()
                
                if extracted_table and image_block.bbox and "page" in image_block.bbox:
                    page_num = image_block.bbox["page"]
                    if extracted_table.bbox:
                        extracted_table.bbox["page"] = page_num
                    else:
                        extracted_table.bbox = {"page": page_num}
                        
            except Exception as e:
                print(f"Error extracting table from {image_name}: {e}")
            
            current_step += 1
            if progress_callback:
                await self._emit_progress(
                    progress_callback,
                    "enhanced_table_extraction",
                    current_step / total_steps if total_steps > 0 else 0,
                    f"Table extraction for {image_name}"
                )
        
        return extracted_table
    
    async def _describe_image_with_context(self, image: ImageBlock) -> None:
        """Generate enhanced AI description with document context."""
        context = {
            "filename": image.source if hasattr(image, 'source') and image.source else "embedded_image",
            "page": image.page if image.page is not None else 0,
            "section": image.section if hasattr(image, 'section') and image.section else "",
            "index": image.index if image.index is not None else 0
        }
        
        try:
            # Use enhanced AI service with document context and timeout
            metadata = await asyncio.wait_for(
                self.enhanced_ai_service.analyze_image_with_context(
                    image.data, 
                    context, 
                    self.document_context
                ),
                timeout=60.0  # 60 second timeout for image analysis
            )
            
            # Store enhanced metadata
            if hasattr(image, 'metadata'):
                image.metadata = metadata
            
            # Set enhanced alt text
            image.alt_text = metadata.get('description', '') or \
                             metadata.get('aiAnnotations', {}).get('explanationGenerated', '')
            
            if not image.alt_text:
                ocr_text = metadata.get('aiAnnotations', {}).get('ocrText', '')
                if ocr_text:
                    image.alt_text = f"Text in image: {ocr_text[:200]}{'...' if len(ocr_text) > 200 else ''}"
                else:
                    image.alt_text = "Image (no enhanced description available)"
                    
        except asyncio.TimeoutError:
            print(f"Warning: Image analysis timed out for image at page {image.page}")
            image.alt_text = "Image (analysis timed out)"
            if hasattr(image, 'metadata'):
                image.metadata = {"error": "Analysis timed out"}
        except Exception as e:
            print(f"Error analyzing image: {e}")
            image.alt_text = "Image (analysis failed)"
            if hasattr(image, 'metadata'):
                image.metadata = {"error": str(e)}
    
    async def _generate_document_summary(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Generate contextual document summary."""
        if not self.document_context:
            return
            
        if progress_callback:
            await self._emit_progress(progress_callback, "document_summary", 0.8, "Generating document summary")
        
        # Prepare document elements for summary
        document_elements = []
        
        # Add text blocks
        for text_block in ast.textBlocks[:20]:  # Limit for performance
            document_elements.append({
                "type": "text",
                "content": text_block.content[:500],  # Truncate for summary
                "block_type": text_block.type.value if hasattr(text_block.type, 'value') else str(text_block.type)
            })
        
        # Add image metadata
        for image in ast.images:
            if hasattr(image, 'metadata') and image.metadata:
                document_elements.append({
                    "type": "image",
                    "description": image.metadata.get('description', ''),
                    "semantic_tags": image.metadata.get('semantic_tags', [])
                })
        
        # Add table information
        for table in ast.tables:
            document_elements.append({
                "type": "table",
                "headers": table.headers,
                "row_count": len(table.rows)
            })
        
        try:
            # Generate summary
            summary = await self.enhanced_ai_service.generate_contextual_summary(
                document_elements, 
                self.document_context
            )
            
            # Add summary to AST metadata
            if not ast.metadata:
                ast.metadata = {}
            ast.metadata["contextual_summary"] = summary
            ast.metadata["document_type"] = self.document_context.document_type.value
            ast.metadata["complexity"] = self.document_context.complexity.value
            
        except Exception as e:
            print(f"Error generating document summary: {e}")
            if not ast.metadata:
                ast.metadata = {}
            ast.metadata["contextual_summary"] = "Summary generation failed"
        
        if progress_callback:
            await self._emit_progress(progress_callback, "document_summary_complete", 0.9, "Document summary generated")

    async def _process_images_and_extract_tables(
        self, 
        ast: DocumentAST, # Pass the full AST to append tables
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process image blocks: generate AI descriptions and extract tables."""
        if not ast.images:
            return

        ai_service = await get_enhanced_ai_service()
        
        # Determine total steps for progress: 1 for description, 1 for table extraction (if enabled) per image
        total_image_processing_steps = len(ast.images)
        if settings.extract_tables_from_images_enabled:
            total_image_processing_steps *= 2

        current_step = 0

        all_new_tables: List[TableBlock] = []

        # Define a batch size for concurrent processing
        batch_size = settings.AI_PROCESSOR_IMAGE_BATCH_SIZE or 3 # Default to 3 if not in settings

        for i in range(0, len(ast.images), batch_size):
            batch_image_blocks = ast.images[i:i + batch_size]
            
            tasks = []
            for idx_in_batch, image_block in enumerate(batch_image_blocks):
                original_idx = i + idx_in_batch
                image_name = f"image_{original_idx}_p{image_block.page if image_block.page is not None else 'unk'}"
                tasks.append(self._process_single_image_fully(
                    ai_service,
                    image_block,
                    image_name,
                    progress_callback,
                    current_step + (idx_in_batch * (2 if settings.extract_tables_from_images_enabled else 1)), # initial step for this image
                    total_image_processing_steps
                ))
            
            # Run tasks for the current batch concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results from the batch
            for result in results:
                if isinstance(result, TableBlock):
                    all_new_tables.append(result)
                elif isinstance(result, Exception):
                    # Log the exception or handle as needed
                    print(f"Error during concurrent image processing: {result}")
            
            current_step += len(batch_image_blocks) * (2 if settings.extract_tables_from_images_enabled else 1)
            
            # Overall batch progress (optional, could be too granular)
            if progress_callback:
                 processed_images_count = min(i + batch_size, len(ast.images))
                 await self._emit_progress(
                    progress_callback,
                    "ai_image_batch_processed",
                    current_step / total_image_processing_steps if total_image_processing_steps > 0 else 0,
                    f"Batch of {len(batch_image_blocks)} images processed ({processed_images_count}/{len(ast.images)} total images)"
                )

        if all_new_tables:
            ast.tables.extend(all_new_tables)


    async def _process_single_image_fully(
        self,
        ai_service,
        image_block: ImageBlock,
        image_name: str,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]], # For granular updates
        base_step: int, # The starting step count for this image in overall progress
        total_overall_steps: int # Total steps for all images
        ) -> Optional[TableBlock]:
        """Processes a single image for description and table extraction."""

        current_local_step = base_step

        # 1. Describe image content
        if not image_block.alt_text or image_block.alt_text.startswith("Image from"):
            try:
                await self._describe_image_content(ai_service, image_block)
            except Exception as e:
                print(f"Error describing {image_name}: {e}")
                if not image_block.alt_text:
                    image_block.alt_text = "Image (description failed)"

        current_local_step +=1
        if progress_callback:
            await self._emit_progress(
                progress_callback,
                "ai_image_description",
                current_local_step / total_overall_steps if total_overall_steps > 0 else 0,
                f"Processed description for {image_name}"
            )

        # 2. Extract table if enabled
        extracted_table: Optional[TableBlock] = None
        if settings.extract_tables_from_images_enabled:
            try:
                image_bytes = base64.b64decode(image_block.data)
                pil_image = Image.open(BytesIO(image_bytes))

                extracted_table = await extract_table_from_pil_image(pil_image, image_name)
                pil_image.close()

                if extracted_table:
                    if image_block.bbox and "page" in image_block.bbox:
                        page_num = image_block.bbox["page"]
                        if extracted_table.bbox: # Should exist if table has content
                            extracted_table.bbox["page"] = page_num
                        else: # Fallback, though parse_markdown_table should init bbox if headers/rows exist
                            extracted_table.bbox = {"page": page_num}
                        # Assign other context if needed, e.g. original image bbox
                        # extracted_table.metadata = {"source_image_bbox": image_block.bbox}

            except Exception as e:
                print(f"Error extracting table from {image_name}: {e}")
            
            current_local_step +=1
            if progress_callback:
                 await self._emit_progress(
                    progress_callback,
                    "ai_image_table_extraction",
                    current_local_step / total_overall_steps if total_overall_steps > 0 else 0,
                    f"Processed table extraction for {image_name}"
                )

        return extracted_table


    async def _describe_image_content(self, ai_service, image: ImageBlock) -> None:
        """Helper to generate AI description for a single image block."""
        # (This is essentially the old _describe_image method, slightly refactored)
        context = {
            "filename": image.source if hasattr(image, 'source') and image.source else "embedded_image",
            "page": image.page if image.page is not None else 0, # Ensure page is not None
            "section": image.section if hasattr(image, 'section') and image.section else "",
            "index": image.index if image.index is not None else 0 # Ensure index is not None
        }

        # Use enhanced AI service with context
        if hasattr(ai_service, 'analyze_image_with_context'):
            metadata = await ai_service.analyze_image_with_context(image.data, context)
        else:
            # Fallback to basic method if enhanced method not available
            metadata = await ai_service.analyze_image_structured(image.data, context)

        if hasattr(image, 'metadata'): # Should always be true for ImageBlock
            image.metadata = metadata

        image.alt_text = metadata.get('description', '') or \
                         metadata.get('aiAnnotations', {}).get('explanationGenerated', '')

        if not image.alt_text:
            ocr_text = metadata.get('aiAnnotations', {}).get('ocrText', '')
            if ocr_text:
                image.alt_text = f"Text in image: {ocr_text[:200]}{'...' if len(ocr_text) > 200 else ''}" # Limit length
            else:
                image.alt_text = "Image (no description available)"


    async def _process_math(
        self, 
        math_blocks: List[MathBlock], 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process math blocks (placeholder for future enhancements)."""
        if not math_blocks:
            return
        
        for i, math_block in enumerate(math_blocks):
            if math_block.format == "text":
                math_block.format = "latex" # Simple conversion attempt
            
            if progress_callback:
                progress = (i + 1) / len(math_blocks) if len(math_blocks) > 0 else 0
                await self._emit_progress(
                    progress_callback,
                    "ai_math_processing",
                    progress,
                    f"Processed math block {i + 1}/{len(math_blocks)}"
                )

    async def _emit_progress(
        self,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]],
        stage: str,
        progress_val: float,
        message: str,
        details: Optional[dict] = None
    ) -> None:
        """Helper to emit progress if callback is available."""
        if progress_callback:
            progress_update = ParseProgress(
                stage=stage,
                progress=progress_val,
                message=message,
                details=details
            )
            try:
                await progress_callback.asend(progress_update)
            except (StopAsyncIteration, GeneratorExit):
                pass # Callback closed
