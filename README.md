# PII Anonymizer

A tool for anonymizing personally identifiable information (PII) in PDF documents using Named Entity Recognition (NER) and diffusion models.

## Features

- Extract text and structure from PDF documents
- Identify PII using Named Entity Recognition (NER)
- Replace sensitive information with plausible fake data using diffusion models
- Generate anonymized PDFs that maintain the original layout and design
- Batch process multiple PDFs
- Customizable entity types to anonymize

## Sample data sources

https://www.edisontd.nl/
https://www.nist.gov/srd/nist-special-database-2
[RVL-CDIP - Document image dataset](https://paperswithcode.com/dataset/rvl-cdip)

https://microsoft.github.io/presidio/samples/

## Installation

### Using Poetry (recommended)

1. Clone the repository:
```bash
git clone git@github.com:pgryko/document-anonymization-using-python-diffusion-models-named-entity-recognition.git
cd document-anonymization-using-python-diffusion-models-named-entity-recognition.git
```

2. Install dependencies using [uv](https://github.com/astral-sh/uv):
```bash
uv install
```

3. Download the spaCy model:
```bash
uv run python -m spacy download en_core_web_lg
```

## Usage

### Command Line Interface

```bash
# Anonymize a single PDF file
python -m pii_anonymizer.cli anonymize --input document.pdf --output anonymized.pdf

# Anonymize all PDFs in a directory
python -m pii_anonymizer.cli batch-anonymize --input-dir pdfs/ --output-dir anonymized/

# Specify entity types to anonymize
python -m pii_anonymizer.cli anonymize --input document.pdf --output anonymized.pdf --entity-types PERSON,ORG,GPE,MONEY
```

### Python API

```python
from src.anonymizer import Anonymizer

# Initialize the anonymizer with default settings
anonymizer = Anonymizer()

# Anonymize text
sensitive_text = "John Smith works at Apple Inc. in New York and earns $5000 per month."
anonymized_text = anonymizer.anonymize_text(sensitive_text)
print(anonymized_text)

# Anonymize a PDF file
stats = anonymizer.anonymize_pdf("document.pdf", "anonymized.pdf")
print(f"Anonymized {stats['total_entities_anonymized']} entities")

# Batch anonymize PDFs
stats = anonymizer.batch_anonymize_pdfs("pdfs/", "anonymized/")
print(f"Processed {stats['processed_files']} files")
```

## Customization

You can customize the anonymization process by specifying:

- NER model: Use different spaCy models for entity recognition
- Text generation model: Use different generative models for text replacement
- Diffusion model: Use different stable diffusion models for image generation
- Entity types: Specify which entity types to anonymize

```python
from src.anonymizer import Anonymizer

# Custom configuration
anonymizer = Anonymizer(
    ner_model_name="en_core_web_trf",  # More accurate spaCy model
    text_model_name="gpt2-medium",     # Larger text generation model
    diffusion_model_name="stabilityai/stable-diffusion-2-1",  # Different diffusion model
    entity_types_to_anonymize={"PERSON", "ORG", "MONEY"}  # Only anonymize these types
)
```

## Presentation

This repository also includes a presentation on anonymization of sensitive information:

1. Install Marp CLI:
```bash
npm install -g @marp-team/marp-cli
```

2. Convert to PDF/PPTX:
```bash
marp --pdf Anonymization-of-Sensitive-Information-in-Financial-Documents-Using-Python-Diffusion-Models-and-Named-Entity-Recognition.md --allow-local-files 
# or
marp --pptx Anonymization-of-Sensitive-Information-in-Financial-Documents-Using-Python-Diffusion-Models-and-Named-Entity-Recognition.md --allow-local-files 
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
