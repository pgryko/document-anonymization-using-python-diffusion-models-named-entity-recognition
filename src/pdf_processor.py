"""
PDF processor for extracting text and images from PDF files.
"""
import pymupdf  # PyMuPDF
from typing import List, Dict, Tuple, Optional
import os
import re

class PDFProcessor:
    """Class for processing PDF files to extract text and other content."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF processor with a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
        self.pdf_path = pdf_path
        self.document = pymupdf.open(pdf_path)
    
    def extract_text(self) -> str:
        """
        Extract all text from the PDF.
        
        Returns:
            A string containing all text from the PDF
        """
        text = ""
        for page in self.document:
            text += page.get_text()
        return text
    
    def extract_text_by_page(self) -> List[str]:
        """
        Extract text from each page of the PDF.
        
        Returns:
            A list of strings where each string contains text from one page
        """
        pages_text = []
        for page in self.document:
            pages_text.append(page.get_text())
        return pages_text
    
    def extract_text_blocks(self) -> List[Dict]:
        """
        Extract text blocks with their position information.
        
        Returns:
            A list of dictionaries containing text block information
            Each dictionary has: text, page_num, x0, y0, x1, y1
        """
        blocks = []
        for page_num, page in enumerate(self.document):
            for block in page.get_text("blocks"):
                # Each block is (x0, y0, x1, y1, text, block_type, block_no)
                blocks.append({
                    "text": block[4],
                    "page_num": page_num,
                    "x0": block[0],
                    "y0": block[1],
                    "x1": block[2],
                    "y1": block[3]
                })
        return blocks
    
    def extract_images(self, output_dir: str) -> List[str]:
        """
        Extract images from the PDF and save them to the output directory.
        
        Args:
            output_dir: Directory to save extracted images
            
        Returns:
            A list of paths to the extracted images
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        image_paths = []
        for page_num, page in enumerate(self.document):
            image_list = page.get_images(full=True)
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = self.document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = os.path.join(output_dir, f"page{page_num + 1}_img{img_index + 1}.{image_ext}")
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                image_paths.append(image_path)
                
        return image_paths
    
    def get_document_metadata(self) -> Dict:
        """
        Get the metadata of the PDF document.
        
        Returns:
            A dictionary containing metadata like title, author, etc.
        """
        return self.document.metadata
    
    def close(self):
        """Close the PDF document."""
        self.document.close()
        
    def __enter__(self):
        """Enter context manager."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close the document."""
        self.close()