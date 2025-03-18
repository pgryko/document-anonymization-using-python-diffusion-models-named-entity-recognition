"""
Main anonymizer class that integrates NER detection, diffusion replacement, and PDF processing.
"""
from typing import Dict, List, Union, Optional, Set
import os
import pymupdf
from tqdm import tqdm
import tempfile
import shutil

from .ner_detector import NERDetector
from .diffusion_replacer import DiffusionReplacer
from .pdf_processor import PDFProcessor


class Anonymizer:
    """
    Class for anonymizing PII data in PDF documents using NER and diffusion models.
    """
    
    def __init__(
        self,
        ner_model_name: str = "en_core_web_lg",
        text_model_name: str = "gpt2",
        diffusion_model_name: str = "runwayml/stable-diffusion-v1-5",
        entity_types_to_anonymize: Optional[Set[str]] = None
    ):
        """
        Initialize the anonymizer with NER and diffusion models.
        
        Args:
            ner_model_name: The spaCy model to use for NER
            text_model_name: The transformer model to use for text generation
            diffusion_model_name: The diffusion model to use for image generation
            entity_types_to_anonymize: Set of entity types to anonymize (if None, use all PII types)
        """
        self.ner_detector = NERDetector(model_name=ner_model_name)
        self.diffusion_replacer = DiffusionReplacer(
            text_model_name=text_model_name,
            diffusion_model_name=diffusion_model_name
        )
        
        # If no entity types specified, use all PII types defined in NERDetector
        self.entity_types_to_anonymize = entity_types_to_anonymize or self.ner_detector.PII_ENTITY_TYPES
    
    def anonymize_text(self, text: str) -> str:
        """
        Anonymize PII data in a text string.
        
        Args:
            text: The text containing sensitive information
            
        Returns:
            The anonymized text with sensitive information replaced
        """
        # Detect PII entities in the text
        entities = self.ner_detector.get_entities_by_type(text, self.entity_types_to_anonymize)
        
        # Replace all detected entities
        anonymized_text = self.diffusion_replacer.replace_entities_in_text(text, entities)
        
        return anonymized_text
    
    def anonymize_pdf(self, input_pdf_path: str, output_pdf_path: str) -> Dict:
        """
        Anonymize PII data in a PDF document.
        
        Args:
            input_pdf_path: Path to the input PDF file
            output_pdf_path: Path to save the anonymized PDF
            
        Returns:
            Dictionary with statistics about the anonymization process
        """
        # Process the PDF
        pdf_processor = PDFProcessor(input_pdf_path)
        
        # Create a new PDF for the output
        anonymized_pdf = fitz.open()
        
        # Statistics to return
        stats = {
            "total_pages": len(pdf_processor.document),
            "total_entities_anonymized": 0,
            "entities_by_type": {}
        }
        
        # Process each page
        for page_num, page in enumerate(tqdm(pdf_processor.document, desc="Anonymizing pages")):
            # Extract text blocks from the page
            page_dict = page.get_text("dict")
            blocks = page_dict["blocks"]
            
            # Create a new page in the output PDF
            new_page = anonymized_pdf.new_page(width=page.rect.width, height=page.rect.height)
            
            # Copy the images from the original page
            for img in page.get_images(full=True):
                xref = img[0]
                new_page.insert_image(page.rect, xref=xref)
            
            # Process each block of text
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            font = span["font"]
                            font_size = span["size"]
                            
                            # Skip if empty text
                            if not text.strip():
                                continue
                            
                            # Detect and anonymize entities in this text span
                            entities = self.ner_detector.get_entities_by_type(
                                text, self.entity_types_to_anonymize
                            )
                            
                            # Update statistics
                            stats["total_entities_anonymized"] += len(entities)
                            for entity in entities:
                                entity_type = entity["label"]
                                if entity_type in stats["entities_by_type"]:
                                    stats["entities_by_type"][entity_type] += 1
                                else:
                                    stats["entities_by_type"][entity_type] = 1
                            
                            # Replace entities if any were found
                            if entities:
                                anonymized_text = self.diffusion_replacer.replace_entities_in_text(text, entities)
                            else:
                                anonymized_text = text
                            
                            # Add the anonymized text to the new page
                            new_page.insert_text(
                                fitz.Point(span["origin"][0], span["origin"][1]),
                                anonymized_text,
                                fontname=font,
                                fontsize=font_size
                            )
        
        # Save the anonymized PDF
        anonymized_pdf.save(output_pdf_path)
        anonymized_pdf.close()
        pdf_processor.close()
        
        return stats
    
    def batch_anonymize_pdfs(self, input_dir: str, output_dir: str) -> Dict:
        """
        Anonymize all PDF files in a directory.
        
        Args:
            input_dir: Directory containing PDF files to anonymize
            output_dir: Directory to save anonymized PDF files
            
        Returns:
            Dictionary with statistics about the anonymization process
        """
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Find all PDF files in the input directory
        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        
        # Statistics to return
        stats = {
            "total_files": len(pdf_files),
            "processed_files": 0,
            "total_entities_anonymized": 0,
            "entities_by_type": {}
        }
        
        # Process each PDF file
        for pdf_file in tqdm(pdf_files, desc="Anonymizing PDF files"):
            input_path = os.path.join(input_dir, pdf_file)
            output_path = os.path.join(output_dir, pdf_file)
            
            try:
                # Anonymize the PDF
                file_stats = self.anonymize_pdf(input_path, output_path)
                
                # Update statistics
                stats["processed_files"] += 1
                stats["total_entities_anonymized"] += file_stats["total_entities_anonymized"]
                
                # Update entity type statistics
                for entity_type, count in file_stats["entities_by_type"].items():
                    if entity_type in stats["entities_by_type"]:
                        stats["entities_by_type"][entity_type] += count
                    else:
                        stats["entities_by_type"][entity_type] = count
                        
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
        
        return stats