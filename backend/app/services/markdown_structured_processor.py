"""
Markdown structured data processor for images, diagrams, and tables.
Generates standardized markdown format for visual elements.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class MarkdownStructuredProcessor:
    """Processes visual elements into structured markdown format."""
    
    @staticmethod
    def generate_image_markdown(metadata: Dict[str, Any]) -> str:
        """
        Generate structured markdown for an image/diagram.
        
        Args:
            metadata: Dictionary containing image metadata
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        # Header
        figure_id = metadata.get('id', 'fig-unknown')
        lines.append(f"### 📌 Figure ID: {figure_id}")
        
        # Basic info
        lines.append(f"**Type:** {metadata.get('type', 'Image').title()}")
        lines.append(f"**Title:** {metadata.get('title', 'Untitled')}")
        lines.append(f"**Caption:** {metadata.get('caption', '')}")
        
        # Source info
        source = metadata.get('source', {})
        lines.append(f"**File:** {source.get('filename', 'unknown')}")
        lines.append(f"**Page:** {source.get('page', 'N/A')}")
        lines.append(f"**Document Section:** {source.get('documentSection', 'N/A')}")
        lines.append("")
        
        # Location (if available)
        location = metadata.get('location', {})
        if any(location.values()):
            lines.append("#### 📍 Location")
            lines.append(f"- X: {location.get('x', 0)}")
            lines.append(f"- Y: {location.get('y', 0)}")
            lines.append(f"- Width: {location.get('width', 0)}")
            lines.append(f"- Height: {location.get('height', 0)}")
            lines.append("")
        
        # Description
        lines.append("#### 🧾 Description")
        lines.append(metadata.get('description', 'No description available.'))
        lines.append("")
        
        # Contextual Summary
        lines.append("#### 🧠 Contextual Summary")
        lines.append(metadata.get('contextualSummary', 'No contextual summary available.'))
        lines.append("")
        
        # Linked Entities
        entities = metadata.get('linkedEntities', [])
        if entities:
            lines.append("#### 🔗 Linked Entities")
            for entity in entities:
                lines.append(f"- {entity.get('type', 'Unknown').title()}: {entity.get('value', '')}")
            lines.append("")
        
        # Text References
        references = metadata.get('textReferences', [])
        if references:
            lines.append("#### 🔍 Text References")
            for ref in references:
                lines.append(f'- "{ref.get("text", "")}"')
            lines.append("")
        
        # Semantic Tags
        tags = metadata.get('semanticTags', [])
        if tags:
            lines.append("#### 🏷️ Semantic Tags")
            lines.append(' '.join(f'`{tag}`' for tag in tags))
            lines.append("")
        
        # AI Annotations
        ai_annotations = metadata.get('aiAnnotations', {})
        if ai_annotations:
            lines.append("#### 🤖 AI Annotations")
            
            objects = ai_annotations.get('objectsDetected', [])
            if objects:
                lines.append(f"- Objects Detected: {', '.join(objects)}")
            
            ocr_text = ai_annotations.get('ocrText', '')
            if ocr_text:
                lines.append(f'- OCR Text: "{ocr_text}"')
            
            language = ai_annotations.get('language', 'en')
            if language:
                lines.append(f"- Language: {language}")
            
            explanation = ai_annotations.get('explanationGenerated', '')
            if explanation:
                lines.append(f"- Explanation: {explanation}")
            
            lines.append("")
        
        # Relations
        relations = metadata.get('relations', {})
        if relations:
            lines.append("#### 🔗 Relations")
            
            explains = relations.get('explains', [])
            if explains:
                lines.append(f"- Explains: {', '.join(explains)}")
            
            referenced_by = relations.get('referencedBy', [])
            if referenced_by:
                lines.append(f"- Referenced By: {', '.join(referenced_by)}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_table_markdown(metadata: Dict[str, Any]) -> str:
        """
        Generate structured markdown for a table.
        
        Args:
            metadata: Dictionary containing table metadata
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        # Header
        table_id = metadata.get('id', 'tbl-unknown')
        lines.append(f"### 📌 Figure ID: {table_id}")
        
        # Basic info
        lines.append("**Type:** Table")
        lines.append(f"**Title:** {metadata.get('title', 'Untitled Table')}")
        lines.append(f"**Caption:** {metadata.get('caption', '')}")
        
        # Source info
        source = metadata.get('source', {})
        lines.append(f"**File:** {source.get('filename', 'unknown')}")
        lines.append(f"**Page:** {source.get('page', 'N/A')}")
        lines.append(f"**Document Section:** {source.get('documentSection', 'N/A')}")
        lines.append("")
        
        # Description
        lines.append("#### 🧾 Description")
        lines.append(metadata.get('description', 'No description available.'))
        lines.append("")
        
        # Contextual Summary
        lines.append("#### 🧠 Contextual Summary")
        lines.append(metadata.get('contextualSummary', 'No contextual summary available.'))
        lines.append("")
        
        # Linked Entities
        entities = metadata.get('linkedEntities', [])
        if entities:
            lines.append("#### 🔗 Linked Entities")
            for entity in entities:
                lines.append(f"- {entity.get('type', 'Unknown').title()}: {entity.get('value', '')}")
            lines.append("")
        
        # Semantic Tags
        tags = metadata.get('semanticTags', [])
        if tags:
            lines.append("#### 🏷️ Semantic Tags")
            lines.append(' '.join(f'`{tag}`' for tag in tags))
            lines.append("")
        
        # AI Annotations for tables
        ai_annotations = metadata.get('aiAnnotations', {})
        if ai_annotations:
            lines.append("#### 🤖 AI Annotations")
            
            if ai_annotations.get('dataValidated'):
                lines.append(f"- Data Validated: {ai_annotations.get('dataValidated')}")
            
            if ai_annotations.get('summary'):
                lines.append(f"- Summary: {ai_annotations.get('summary')}")
            
            if ai_annotations.get('highlightedTrend'):
                lines.append(f"- Highlighted Trend: {ai_annotations.get('highlightedTrend')}")
            
            lines.append("")
        
        # Relations
        relations = metadata.get('relations', {})
        if relations:
            lines.append("#### 🔗 Relations")
            
            explains = relations.get('explains', [])
            if explains:
                lines.append(f"- Explains: {', '.join(explains)}")
            
            referenced_by = relations.get('referencedBy', [])
            if referenced_by:
                lines.append(f"- Referenced By: {', '.join(referenced_by)}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    @staticmethod
    def parse_markdown_to_metadata(markdown_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse structured markdown back into metadata dictionary.
        
        Args:
            markdown_text: Structured markdown text
            
        Returns:
            Dictionary containing parsed metadata or None if parsing fails
        """
        try:
            metadata = {
                'source': {},
                'location': {},
                'linkedEntities': [],
                'textReferences': [],
                'semanticTags': [],
                'aiAnnotations': {},
                'relations': {}
            }
            
            lines = markdown_text.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Parse figure ID
                if line.startswith('### 📌 Figure ID:'):
                    metadata['id'] = line.split(':', 1)[1].strip()
                
                # Parse basic fields
                elif line.startswith('**Type:**'):
                    metadata['type'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('**Title:**'):
                    metadata['title'] = line.split(':', 1)[1].strip()
                elif line.startswith('**Caption:**'):
                    metadata['caption'] = line.split(':', 1)[1].strip()
                elif line.startswith('**File:**'):
                    metadata['source']['filename'] = line.split(':', 1)[1].strip()
                elif line.startswith('**Page:**'):
                    try:
                        metadata['source']['page'] = int(line.split(':', 1)[1].strip())
                    except:
                        metadata['source']['page'] = 0
                elif line.startswith('**Document Section:**'):
                    metadata['source']['documentSection'] = line.split(':', 1)[1].strip()
                
                # Track current section
                elif line.startswith('####'):
                    if '📍 Location' in line:
                        current_section = 'location'
                    elif '🧾 Description' in line:
                        current_section = 'description'
                    elif '🧠 Contextual Summary' in line:
                        current_section = 'contextualSummary'
                    elif '🔗 Linked Entities' in line:
                        current_section = 'linkedEntities'
                    elif '🔍 Text References' in line:
                        current_section = 'textReferences'
                    elif '🏷️ Semantic Tags' in line:
                        current_section = 'semanticTags'
                    elif '🤖 AI Annotations' in line:
                        current_section = 'aiAnnotations'
                    elif '🔗 Relations' in line:
                        current_section = 'relations'
                
                # Parse section content
                elif current_section and line:
                    if current_section == 'location' and line.startswith('- '):
                        key_val = line[2:].split(':', 1)
                        if len(key_val) == 2:
                            key = key_val[0].strip().lower()
                            try:
                                metadata['location'][key] = float(key_val[1].strip())
                            except:
                                metadata['location'][key] = 0
                    
                    elif current_section == 'description':
                        metadata['description'] = line
                        current_section = None
                    
                    elif current_section == 'contextualSummary':
                        metadata['contextualSummary'] = line
                        current_section = None
                    
                    elif current_section == 'linkedEntities' and line.startswith('- '):
                        entity_parts = line[2:].split(':', 1)
                        if len(entity_parts) == 2:
                            metadata['linkedEntities'].append({
                                'type': entity_parts[0].strip().lower(),
                                'value': entity_parts[1].strip()
                            })
                    
                    elif current_section == 'textReferences' and line.startswith('- '):
                        text = line[2:].strip('"')
                        metadata['textReferences'].append({'text': text})
                    
                    elif current_section == 'semanticTags':
                        # Extract tags from backticks
                        tags = re.findall(r'`([^`]+)`', line)
                        metadata['semanticTags'].extend(tags)
                        current_section = None
            
            return metadata
            
        except Exception as e:
            print(f"Error parsing markdown to metadata: {e}")
            return None
