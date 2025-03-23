from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
from typing import List, Dict


def anonymize_text(
    text: str, entities: List[Dict], operators: Dict[str, str] = None
) -> str:
    """Anonymize text based on detected entities.

    Args:
        text: Original text
        entities: List of detected entities (from detect_pii_in_text)
        operators: Dictionary mapping entity types to anonymization methods
                  (e.g., {"PERSON": "replace", "EMAIL_ADDRESS": "mask"})

    Returns:
        Anonymized text
    """
    # Default to replacing all entities with their type
    if operators is None:
        operators = {}

    # Convert our entities back to Presidio format
    analyzer_results = []
    for entity in entities:
        analyzer_results.append(
            RecognizerResult(
                entity_type=entity["entity_type"],
                start=entity["start"],
                end=entity["end"],
                score=entity["score"],
            )
        )

    # Create operator configuration
    operator_configs = {}
    for entity_type, operator in operators.items():
        operator_configs[entity_type] = OperatorConfig(operator)

    # Anonymize
    anonymizer = AnonymizerEngine()
    anonymized_text = anonymizer.anonymize(
        text=text, analyzer_results=analyzer_results, operators=operator_configs
    ).text

    return anonymized_text
