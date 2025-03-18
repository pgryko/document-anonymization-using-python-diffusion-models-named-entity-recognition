"""
Command-line interface for the PII Anonymizer.
"""
import click
import os
import sys
from typing import Set, List

from .anonymizer import Anonymizer


@click.group()
def cli():
    """Tool for anonymizing PII data in PDF documents."""
    pass


@cli.command()
@click.option(
    "--input", "-i", 
    required=True, 
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to the input PDF file"
)
@click.option(
    "--output", "-o", 
    required=True, 
    type=click.Path(file_okay=True, dir_okay=False),
    help="Path to save the anonymized PDF file"
)
@click.option(
    "--ner-model", 
    default="en_core_web_lg",
    help="SpaCy model to use for NER (default: en_core_web_lg)"
)
@click.option(
    "--text-model", 
    default="gpt2",
    help="Text generation model to use (default: gpt2)"
)
@click.option(
    "--diffusion-model", 
    default="runwayml/stable-diffusion-v1-5",
    help="Diffusion model to use (default: runwayml/stable-diffusion-v1-5)"
)
@click.option(
    "--entity-types", 
    default=None,
    help="Comma-separated list of entity types to anonymize (default: all PII types)"
)
def anonymize(
    input: str, 
    output: str, 
    ner_model: str, 
    text_model: str, 
    diffusion_model: str,
    entity_types: str
):
    """Anonymize PII data in a PDF file."""
    # Parse entity types if provided
    entity_types_set = None
    if entity_types:
        entity_types_set = set(entity_types.split(","))
    
    # Create the anonymizer
    anonymizer = Anonymizer(
        ner_model_name=ner_model,
        text_model_name=text_model,
        diffusion_model_name=diffusion_model,
        entity_types_to_anonymize=entity_types_set
    )
    
    # Anonymize the PDF
    click.echo(f"Anonymizing {input}...")
    stats = anonymizer.anonymize_pdf(input, output)
    
    # Display statistics
    click.echo(f"Done! Anonymized {stats['total_entities_anonymized']} entities")
    click.echo("Entities by type:")
    for entity_type, count in stats["entities_by_type"].items():
        click.echo(f"  {entity_type}: {count}")


@cli.command()
@click.option(
    "--input-dir", "-i", 
    required=True, 
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing PDF files to anonymize"
)
@click.option(
    "--output-dir", "-o", 
    required=True, 
    type=click.Path(file_okay=False, dir_okay=True),
    help="Directory to save anonymized PDF files"
)
@click.option(
    "--ner-model", 
    default="en_core_web_lg",
    help="SpaCy model to use for NER (default: en_core_web_lg)"
)
@click.option(
    "--text-model", 
    default="gpt2",
    help="Text generation model to use (default: gpt2)"
)
@click.option(
    "--diffusion-model", 
    default="runwayml/stable-diffusion-v1-5",
    help="Diffusion model to use (default: runwayml/stable-diffusion-v1-5)"
)
@click.option(
    "--entity-types", 
    default=None,
    help="Comma-separated list of entity types to anonymize (default: all PII types)"
)
def batch_anonymize(
    input_dir: str, 
    output_dir: str, 
    ner_model: str, 
    text_model: str, 
    diffusion_model: str,
    entity_types: str
):
    """Anonymize PII data in all PDF files in a directory."""
    # Parse entity types if provided
    entity_types_set = None
    if entity_types:
        entity_types_set = set(entity_types.split(","))
    
    # Create the anonymizer
    anonymizer = Anonymizer(
        ner_model_name=ner_model,
        text_model_name=text_model,
        diffusion_model_name=diffusion_model,
        entity_types_to_anonymize=entity_types_set
    )
    
    # Anonymize all PDFs in the directory
    click.echo(f"Anonymizing PDFs in {input_dir}...")
    stats = anonymizer.batch_anonymize_pdfs(input_dir, output_dir)
    
    # Display statistics
    click.echo(f"Done! Processed {stats['processed_files']} files")
    click.echo(f"Anonymized {stats['total_entities_anonymized']} entities in total")
    click.echo("Entities by type:")
    for entity_type, count in stats["entities_by_type"].items():
        click.echo(f"  {entity_type}: {count}")


if __name__ == "__main__":
    cli()