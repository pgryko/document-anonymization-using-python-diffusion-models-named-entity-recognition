from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from typing import List


def setup_presidio_analyzer():
    """Set up and return a Presidio analyzer engine."""
    # Create NLP engine based on spaCy
    provider = NlpEngineProvider(nlp_configuration={"lang_code": "en"})
    nlp_engine = provider.create_engine()

    # Set up the analyzer with the NLP engine
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    return analyzer


def detect_pii_in_text(text: str, analyzer=None) -> List[dict]:
    """Detect PII entities in text using Presidio Analyzer.

    Args:
        text: Text to analyze
        analyzer: Optional pre-configured analyzer

    Returns:
        List of detected PII entities
    """
    if analyzer is None:
        analyzer = setup_presidio_analyzer()

    # Analyze text
    results = analyzer.analyze(text=text, language="en")

    # Convert to a more usable format
    entities = []
    for result in results:
        entities.append(
            {
                "text": text[result.start : result.end],
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
            }
        )

    return entities
