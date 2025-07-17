"""
Entity Recognition and Linking Service

This service provides advanced entity recognition capabilities including:
- Named Entity Recognition (NER) using spaCy and custom models
- Entity linking to external knowledge bases (Wikipedia, Wikidata, etc.)
- Domain-specific entity extraction (scientific terms, legal concepts, etc.)
- Relationship extraction between entities
- Semantic search capabilities
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from urllib.parse import quote
import aiohttp
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span
import openai
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Types of entities that can be recognized"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    WORK_OF_ART = "WORK_OF_ART"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    
    # Domain-specific entities
    SCIENTIFIC_TERM = "SCIENTIFIC_TERM"
    CHEMICAL_COMPOUND = "CHEMICAL_COMPOUND"
    GENE = "GENE"
    PROTEIN = "PROTEIN"
    DISEASE = "DISEASE"
    MEDICATION = "MEDICATION"
    LEGAL_TERM = "LEGAL_TERM"
    FINANCIAL_INSTRUMENT = "FINANCIAL_INSTRUMENT"
    TECHNOLOGY = "TECHNOLOGY"
    METHODOLOGY = "METHODOLOGY"

class ConfidenceLevel(Enum):
    """Confidence levels for entity recognition"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class EntityMention:
    """Represents a mention of an entity in the text"""
    text: str
    start: int
    end: int
    entity_type: EntityType
    confidence: float
    context: str = ""
    
@dataclass
class LinkedEntity:
    """Represents an entity linked to external knowledge base"""
    mention: EntityMention
    wiki_id: Optional[str] = None
    wikidata_id: Optional[str] = None
    wikipedia_url: Optional[str] = None
    description: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    
@dataclass
class EntityRelationship:
    """Represents a relationship between two entities"""
    source_entity: LinkedEntity
    target_entity: LinkedEntity
    relationship_type: str
    confidence: float
    context: str = ""

@dataclass
class EntityExtractionResult:
    """Result of entity extraction process"""
    entities: List[LinkedEntity]
    relationships: List[EntityRelationship]
    semantic_embeddings: Dict[str, np.ndarray] = field(default_factory=dict)
    domain_context: Optional[str] = None
    processing_stats: Dict[str, Any] = field(default_factory=dict)

class EntityRecognitionService:
    """Service for recognizing and linking entities in documents"""
    
    def __init__(self, openai_client: openai.AsyncOpenAI):
        self.openai_client = openai_client
        self.nlp = None
        self.matcher = None
        self.sentence_transformer = None
        self.session = None
        
        # Domain-specific patterns
        self.domain_patterns = {
            EntityType.SCIENTIFIC_TERM: [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:effect|theorem|law|principle|method|algorithm)\b',
                r'\b(?:RNA|DNA|mRNA|tRNA|rRNA|siRNA|miRNA)\b',
                r'\b\d+(?:\.\d+)?\s*(?:nm|μm|mm|cm|m|km|ml|l|mg|g|kg|mol|M|mM|μM|nM|pM)\b'
            ],
            EntityType.CHEMICAL_COMPOUND: [
                r'\b[A-Z][a-z]*(?:\([IVX]+\))?\b',  # Chemical formulas
                r'\b(?:C\d+H\d+(?:O\d+)?(?:N\d+)?)\b',  # Molecular formulas
                r'\b\d+(?:\.\d+)?\s*(?:mol|M|mM|μM|nM|pM)\b'  # Concentrations
            ],
            EntityType.LEGAL_TERM: [
                r'\b(?:Section|Article|Chapter|Title|Paragraph|Subsection)\s+\d+(?:\.\d+)*\b',
                r'\b(?:USC|CFR|Fed\.?\s*R\.?\s*Civ\.?\s*P\.?|F\.?\s*Supp\.?)\b',
                r'\b(?:plaintiff|defendant|appellant|appellee|petitioner|respondent)\b'
            ],
            EntityType.FINANCIAL_INSTRUMENT: [
                r'\b(?:USD|EUR|GBP|JPY|CAD|AUD|CHF|CNY)\s*\d+(?:,\d{3})*(?:\.\d{2})?\b',
                r'\b(?:stock|bond|option|future|derivative|equity|debt|security)\b',
                r'\b(?:S&P|NYSE|NASDAQ|FTSE|DAX|Nikkei)\b'
            ]
        }
        
    async def initialize(self):
        """Initialize the service components"""
        try:
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Using basic tokenizer.")
                self.nlp = spacy.blank("en")
            
            # Initialize matcher for custom patterns
            self.matcher = Matcher(self.nlp.vocab)
            self._add_custom_patterns()
            
            # Initialize sentence transformer for embeddings
            try:
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            logger.info("Entity Recognition Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Entity Recognition Service: {e}")
            raise
    
    def _add_custom_patterns(self):
        """Add custom patterns to the matcher"""
        # Scientific terms pattern
        science_pattern = [
            {"TEXT": {"REGEX": r"[A-Z][a-z]+"}},
            {"TEXT": {"IN": ["effect", "theorem", "law", "principle", "method", "algorithm"]}}
        ]
        self.matcher.add("SCIENTIFIC_TERM", [science_pattern])
        
        # Chemical compound pattern
        chemical_pattern = [
            {"TEXT": {"REGEX": r"[A-Z][a-z]*\d*"}}
        ]
        self.matcher.add("CHEMICAL_COMPOUND", [chemical_pattern])
        
        # Legal citation pattern
        legal_pattern = [
            {"TEXT": {"IN": ["Section", "Article", "Chapter"]}},
            {"TEXT": {"REGEX": r"\d+"}}
        ]
        self.matcher.add("LEGAL_TERM", [legal_pattern])
    
    async def extract_entities(self, text: str, document_type: str = "general") -> EntityExtractionResult:
        """Extract and link entities from text"""
        try:
            # Step 1: Basic NER with spaCy
            doc = self.nlp(text)
            basic_entities = self._extract_basic_entities(doc)
            
            # Step 2: Domain-specific entity extraction
            domain_entities = self._extract_domain_entities(text, document_type)
            
            # Step 3: Custom pattern matching
            custom_entities = self._extract_custom_entities(doc)
            
            # Step 4: AI-enhanced entity extraction
            ai_entities = await self._extract_ai_entities(text, document_type)
            
            # Step 5: Combine and deduplicate entities
            all_mentions = basic_entities + domain_entities + custom_entities + ai_entities
            deduplicated_mentions = self._deduplicate_entities(all_mentions)
            
            # Step 6: Entity linking
            linked_entities = []
            for mention in deduplicated_mentions:
                linked_entity = await self._link_entity(mention)
                linked_entities.append(linked_entity)
            
            # Step 7: Relationship extraction
            relationships = await self._extract_relationships(linked_entities, text)
            
            # Step 8: Generate semantic embeddings
            embeddings = self._generate_embeddings(linked_entities)
            
            return EntityExtractionResult(
                entities=linked_entities,
                relationships=relationships,
                semantic_embeddings=embeddings,
                domain_context=document_type,
                processing_stats={
                    "total_entities": len(linked_entities),
                    "total_relationships": len(relationships),
                    "basic_entities": len(basic_entities),
                    "domain_entities": len(domain_entities),
                    "custom_entities": len(custom_entities),
                    "ai_entities": len(ai_entities)
                }
            )
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return EntityExtractionResult(entities=[], relationships=[])
    
    def _extract_basic_entities(self, doc: Doc) -> List[EntityMention]:
        """Extract basic named entities using spaCy"""
        entities = []
        
        for ent in doc.ents:
            try:
                entity_type = EntityType(ent.label_)
            except ValueError:
                # Map spaCy labels to our EntityType
                entity_type = self._map_spacy_label(ent.label_)
            
            entities.append(EntityMention(
                text=ent.text,
                start=ent.start_char,
                end=ent.end_char,
                entity_type=entity_type,
                confidence=0.8,  # Default confidence for spaCy entities
                context=str(ent.sent)
            ))
        
        return entities
    
    def _extract_domain_entities(self, text: str, document_type: str) -> List[EntityMention]:
        """Extract domain-specific entities using regex patterns"""
        entities = []
        
        # Select patterns based on document type
        relevant_patterns = {}
        if document_type.lower() in ['scientific', 'research', 'medical']:
            relevant_patterns.update({
                EntityType.SCIENTIFIC_TERM: self.domain_patterns[EntityType.SCIENTIFIC_TERM],
                EntityType.CHEMICAL_COMPOUND: self.domain_patterns[EntityType.CHEMICAL_COMPOUND]
            })
        elif document_type.lower() in ['legal', 'contract', 'regulatory']:
            relevant_patterns.update({
                EntityType.LEGAL_TERM: self.domain_patterns[EntityType.LEGAL_TERM]
            })
        elif document_type.lower() in ['financial', 'economic', 'business']:
            relevant_patterns.update({
                EntityType.FINANCIAL_INSTRUMENT: self.domain_patterns[EntityType.FINANCIAL_INSTRUMENT]
            })
        
        # Apply patterns
        for entity_type, patterns in relevant_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append(EntityMention(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        entity_type=entity_type,
                        confidence=0.6,  # Medium confidence for regex matches
                        context=self._get_context(text, match.start(), match.end())
                    ))
        
        return entities
    
    def _extract_custom_entities(self, doc: Doc) -> List[EntityMention]:
        """Extract entities using custom patterns"""
        entities = []
        matches = self.matcher(doc)
        
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            try:
                entity_type = EntityType(label)
            except ValueError:
                entity_type = EntityType.SCIENTIFIC_TERM  # Default fallback
            
            entities.append(EntityMention(
                text=span.text,
                start=span.start_char,
                end=span.end_char,
                entity_type=entity_type,
                confidence=0.7,
                context=str(span.sent)
            ))
        
        return entities
    
    async def _extract_ai_entities(self, text: str, document_type: str) -> List[EntityMention]:
        """Extract entities using AI/LLM"""
        try:
            prompt = f"""
            Extract named entities from the following {document_type} text. 
            Focus on entities that might be missed by standard NER tools.
            
            Text: {text[:2000]}  # Limit text length
            
            Return a JSON array of entities with the following structure:
            {{
                "text": "entity text",
                "type": "entity type",
                "start": start_position,
                "end": end_position,
                "confidence": 0.0-1.0
            }}
            
            Entity types to consider: {[t.value for t in EntityType]}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse AI response
            entities = []
            try:
                ai_entities = json.loads(response.choices[0].message.content)
                for entity_data in ai_entities:
                    try:
                        entity_type = EntityType(entity_data['type'])
                    except ValueError:
                        continue
                    
                    entities.append(EntityMention(
                        text=entity_data['text'],
                        start=entity_data.get('start', 0),
                        end=entity_data.get('end', 0),
                        entity_type=entity_type,
                        confidence=entity_data.get('confidence', 0.5),
                        context=self._get_context(text, entity_data.get('start', 0), entity_data.get('end', 0))
                    ))
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI entity extraction response")
            
            return entities
            
        except Exception as e:
            logger.error(f"AI entity extraction failed: {e}")
            return []
    
    def _deduplicate_entities(self, entities: List[EntityMention]) -> List[EntityMention]:
        """Remove duplicate entities based on text overlap"""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda x: x.start)
        
        deduplicated = []
        for entity in entities:
            # Check for overlap with existing entities
            is_duplicate = False
            for existing in deduplicated:
                if self._entities_overlap(entity, existing):
                    # Keep the one with higher confidence
                    if entity.confidence > existing.confidence:
                        deduplicated.remove(existing)
                        deduplicated.append(entity)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(entity)
        
        return deduplicated
    
    def _entities_overlap(self, entity1: EntityMention, entity2: EntityMention) -> bool:
        """Check if two entities overlap"""
        return not (entity1.end <= entity2.start or entity2.end <= entity1.start)
    
    async def _link_entity(self, mention: EntityMention) -> LinkedEntity:
        """Link entity to external knowledge base"""
        try:
            # First, try Wikipedia/Wikidata linking
            wiki_result = await self._link_to_wikipedia(mention.text)
            
            if wiki_result:
                return LinkedEntity(
                    mention=mention,
                    wiki_id=wiki_result.get('wiki_id'),
                    wikidata_id=wiki_result.get('wikidata_id'),
                    wikipedia_url=wiki_result.get('wikipedia_url'),
                    description=wiki_result.get('description'),
                    aliases=wiki_result.get('aliases', []),
                    properties=wiki_result.get('properties', {}),
                    confidence=wiki_result.get('confidence', 0.5)
                )
            else:
                # Fallback to basic entity without linking
                return LinkedEntity(
                    mention=mention,
                    confidence=mention.confidence * 0.5  # Reduce confidence for unlinked entities
                )
                
        except Exception as e:
            logger.error(f"Entity linking failed for '{mention.text}': {e}")
            return LinkedEntity(mention=mention, confidence=mention.confidence * 0.5)
    
    async def _link_to_wikipedia(self, entity_text: str) -> Optional[Dict[str, Any]]:
        """Link entity to Wikipedia/Wikidata"""
        try:
            # Search Wikipedia API
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(entity_text)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'wiki_id': data.get('pageid'),
                        'wikipedia_url': data.get('content_urls', {}).get('desktop', {}).get('page'),
                        'description': data.get('extract'),
                        'aliases': [data.get('title', entity_text)],
                        'properties': {
                            'type': data.get('type'),
                            'lang': data.get('lang'),
                            'thumbnail': data.get('thumbnail')
                        },
                        'confidence': 0.8
                    }
                    
        except Exception as e:
            logger.debug(f"Wikipedia linking failed for '{entity_text}': {e}")
        
        return None
    
    async def _extract_relationships(self, entities: List[LinkedEntity], text: str) -> List[EntityRelationship]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple co-occurrence based relationships
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if entities are mentioned close to each other
                distance = abs(entity1.mention.start - entity2.mention.start)
                if distance < 200:  # Within 200 characters
                    relationship = EntityRelationship(
                        source_entity=entity1,
                        target_entity=entity2,
                        relationship_type="co-occurs",
                        confidence=0.5,
                        context=self._get_context(text, 
                                                min(entity1.mention.start, entity2.mention.start),
                                                max(entity1.mention.end, entity2.mention.end))
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _generate_embeddings(self, entities: List[LinkedEntity]) -> Dict[str, np.ndarray]:
        """Generate semantic embeddings for entities"""
        embeddings = {}
        
        if not self.sentence_transformer:
            return embeddings
        
        try:
            for entity in entities:
                text_to_embed = entity.mention.text
                if entity.description:
                    text_to_embed += f" {entity.description}"
                
                embedding = self.sentence_transformer.encode(text_to_embed)
                embeddings[entity.mention.text] = embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
        
        return embeddings
    
    def _map_spacy_label(self, label: str) -> EntityType:
        """Map spaCy entity labels to our EntityType enum"""
        mapping = {
            'PERSON': EntityType.PERSON,
            'ORG': EntityType.ORGANIZATION,
            'GPE': EntityType.LOCATION,
            'LOC': EntityType.LOCATION,
            'DATE': EntityType.DATE,
            'TIME': EntityType.DATE,
            'MONEY': EntityType.MONEY,
            'PERCENT': EntityType.PERCENT,
            'PRODUCT': EntityType.PRODUCT,
            'EVENT': EntityType.EVENT,
            'WORK_OF_ART': EntityType.WORK_OF_ART,
            'LAW': EntityType.LAW,
            'LANGUAGE': EntityType.LANGUAGE,
        }
        
        return mapping.get(label, EntityType.SCIENTIFIC_TERM)
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around entity mention"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    async def close(self):
        """Close the service and clean up resources"""
        if self.session:
            await self.session.close()
        logger.info("Entity Recognition Service closed")

# Additional utility functions for semantic search
class SemanticSearchEngine:
    """Semantic search engine for entities"""
    
    def __init__(self, entities: List[LinkedEntity], embeddings: Dict[str, np.ndarray]):
        self.entities = entities
        self.embeddings = embeddings
        self.entity_index = {entity.mention.text: entity for entity in entities}
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[LinkedEntity, float]]:
        """Search for entities semantically similar to query"""
        if not self.embeddings:
            return []
        
        try:
            # Get query embedding
            query_embedding = SentenceTransformer('all-MiniLM-L6-v2').encode(query)
            
            # Calculate similarities
            similarities = []
            for entity_text, embedding in self.embeddings.items():
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1), 
                    embedding.reshape(1, -1)
                )[0][0]
                
                if entity_text in self.entity_index:
                    similarities.append((self.entity_index[entity_text], similarity))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
