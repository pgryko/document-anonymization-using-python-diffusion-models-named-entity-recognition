"""
Tests for the NERDetector class.
"""

import pytest
from src.ner_detector import NERDetector


@pytest.fixture
def ner_detector():
    return NERDetector(model_name="en_core_web_sm")


def test_detect_entities(ner_detector):
    """Test that entities are correctly detected in text."""
    text = "John Smith works at Apple Inc. in New York City and earns $5000 per month."
    entities = ner_detector.detect_entities(text)

    # Check that we found at least some entities
    assert len(entities) >= 4

    # Check entity types and texts
    entity_texts = [entity["text"] for entity in entities]
    entity_labels = [entity["label"] for entity in entities]

    assert "John Smith" in entity_texts
    assert "Apple Inc." in entity_texts
    assert "New York City" in entity_texts
    assert "$5000" in entity_texts

    assert "PERSON" in entity_labels
    assert "ORG" in entity_labels
    assert "GPE" in entity_labels
    assert "MONEY" in entity_labels


def test_get_pii_entities(ner_detector):
    """Test filtering to only PII entities."""
    text = "John Smith visited Paris on Tuesday with his colleague Sarah."
    pii_entities = ner_detector.get_pii_entities(text)

    # Check that we found PII entities
    assert len(pii_entities) >= 3

    # Check that all returned entities are in the PII_ENTITY_TYPES set
    for entity in pii_entities:
        assert entity["label"] in NERDetector.PII_ENTITY_TYPES

    # Check for specific entities
    entity_texts = [entity["text"] for entity in pii_entities]
    assert "John Smith" in entity_texts
    assert "Paris" in entity_texts
    assert "Tuesday" in entity_texts


def test_get_entities_by_type(ner_detector):
    """Test filtering entities by specific types."""
    text = "Amazon reported $5 billion in revenue last quarter, according to CEO Jeff Bezos."

    # Get only person entities
    person_entities = ner_detector.get_entities_by_type(text, {"PERSON"})
    assert len(person_entities) >= 1
    assert all(entity["label"] == "PERSON" for entity in person_entities)
    assert "Jeff Bezos" in [entity["text"] for entity in person_entities]

    # Get only organization and money entities
    org_money_entities = ner_detector.get_entities_by_type(text, {"ORG", "MONEY"})
    assert len(org_money_entities) >= 2
    assert all(entity["label"] in {"ORG", "MONEY"} for entity in org_money_entities)
    assert "Amazon" in [entity["text"] for entity in org_money_entities]
    assert "$5 billion" in [entity["text"] for entity in org_money_entities]
