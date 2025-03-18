"""
NER Detector for identifying PII data in text.
"""
import spacy
from typing import List, Dict, Tuple, Set

class NERDetector:
    """Class for detecting named entities in text using spaCy."""
    
    PII_ENTITY_TYPES = {
        "PERSON", "ORG", "GPE", "LOC", "MONEY", "CARDINAL", 
        "DATE", "TIME"
    }
    
    def __init__(self, model_name: str = "en_core_web_lg"):
        """
        Initialize the NER detector with a spaCy model.
        
        Args:
            model_name: The spaCy model to use for NER. Default is 'en_core_web_lg'.
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise ValueError(f"Spacy model '{model_name}' not found. Install it with: python -m spacy download {model_name}")
    
    def detect_entities(self, text: str) -> List[Dict]:
        """
        Detect named entities in the provided text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A list of dictionaries containing entity information
            Each dictionary has: text, label, start_char, end_char
        """
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char
            })
        
        return entities
    
    def get_pii_entities(self, text: str) -> List[Dict]:
        """
        Extract only PII entities from the provided text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A list of dictionaries containing PII entity information
        """
        entities = self.detect_entities(text)
        return [entity for entity in entities if entity["label"] in self.PII_ENTITY_TYPES]
    
    def get_entities_by_type(self, text: str, entity_types: Set[str]) -> List[Dict]:
        """
        Extract entities of specific types from the provided text.
        
        Args:
            text: The text to analyze
            entity_types: A set of entity types to extract
            
        Returns:
            A list of dictionaries containing entity information
        """
        entities = self.detect_entities(text)
        return [entity for entity in entities if entity["label"] in entity_types]