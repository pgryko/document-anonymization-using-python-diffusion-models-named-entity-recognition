import pdf2image
from typing import List
import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text as a string
    """
    text = ""

    try:
        doc = pymupdf.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {e}")

    return text


def extract_images_from_pdf(pdf_path: str, dpi: int = 300) -> List[dict]:
    """Extract images from PDF pages for image-based redaction.

    Args:
        pdf_path: Path to the PDF file
        dpi: DPI for extracted images

    Returns:
        List of dictionaries with page number and image data
    """
    images = []

    try:
        # Convert PDF pages to images
        pages = pdf2image.convert_from_path(pdf_path, dpi=dpi)

        for i, page in enumerate(pages):
            images.append({"page_num": i + 1, "image": page})
    except Exception as e:
        raise Exception(f"Error extracting images from PDF: {e}")

    return images
