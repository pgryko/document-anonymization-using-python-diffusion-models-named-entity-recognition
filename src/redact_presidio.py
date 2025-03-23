from presidio_image_redactor import ImageRedactorEngine
from PIL import Image


def redact_pii_in_image(image: Image.Image) -> Image.Image:
    """Redact PII in an image using Presidio Image Redactor.

    Args:
        image: PIL Image object

    Returns:
        Redacted image
    """
    # Initialize the engine
    engine = ImageRedactorEngine()

    # Redact the image
    redacted_image = engine.redact(image)

    return redacted_image
