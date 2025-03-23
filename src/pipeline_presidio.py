import fitz  # PyMuPDF
import io

from src.anonymize import anonymize_text
from src.detect_presidio import detect_pii_in_text
from src.extract import extract_text_from_pdf, extract_images_from_pdf
from src.redact_presidio import redact_pii_in_image


def anonymize_pdf(
    input_pdf_path: str, output_pdf_path: str, operators: dict = None
) -> None:
    """Process a PDF to anonymize PII in both text and images.

    Args:
        input_pdf_path: Path to the input PDF
        output_pdf_path: Path to save the anonymized PDF
        operators: Optional dictionary mapping entity types to anonymization methods
    """
    # Step 1: Extract text
    text = extract_text_from_pdf(input_pdf_path)

    # Step 2: Detect PII in text
    entities = detect_pii_in_text(text)

    # Step 3: Anonymize text
    anonymized_text = anonymize_text(text, entities, operators)

    # Step 4: Extract images from PDF
    images = extract_images_from_pdf(input_pdf_path)

    # Step 5: Redact PII in images
    redacted_images = []
    for img_data in images:
        redacted_img = redact_pii_in_image(img_data["image"])
        redacted_images.append(
            {"page_num": img_data["page_num"], "image": redacted_img}
        )

    # Step 6: Create a new PDF with anonymized content
    # This is a simplified approach - in practice, recreating the exact
    # PDF layout is complex and might require more sophisticated methods
    doc = fitz.open(input_pdf_path)
    new_doc = fitz.open()

    for page_num in range(len(doc)):
        # Add a new page
        page = new_doc.new_page(
            width=doc[page_num].rect.width, height=doc[page_num].rect.height
        )

        # Add the redacted image as background
        img_data = redacted_images[page_num]["image"]
        img_bytes = io.BytesIO()
        img_data.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Insert image
        page.insert_image(page.rect, stream=img_bytes)

    # Save the new document
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()
