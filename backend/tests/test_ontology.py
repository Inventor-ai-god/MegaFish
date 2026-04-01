"""
Unit tests for pure / mockable functions in OntologyGenerator.

All tests mock the LLMClient so no Ollama instance is needed.
"""

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def generator():
    """Return an OntologyGenerator with a mocked LLMClient."""
    with patch("app.utils.llm_client.LLMClient") as MockLLM:
        from app.services.ontology_generator import OntologyGenerator
        mock_llm = MagicMock()
        gen = OntologyGenerator(llm_client=mock_llm)
        gen.llm_client = mock_llm
        return gen


# ---------------------------------------------------------------------------
# _build_user_message
# ---------------------------------------------------------------------------

def test_build_user_message_contains_simulation_requirement(generator):
    msg = generator._build_user_message(
        document_texts=["Some document content"],
        simulation_requirement="Simulate public reaction to a product launch",
        additional_context=None,
    )
    assert "Simulate public reaction to a product launch" in msg


def test_build_user_message_contains_document_text(generator):
    msg = generator._build_user_message(
        document_texts=["Document about climate policy"],
        simulation_requirement="Climate simulation",
        additional_context=None,
    )
    assert "Document about climate policy" in msg


def test_build_user_message_includes_additional_context(generator):
    msg = generator._build_user_message(
        document_texts=["Doc"],
        simulation_requirement="req",
        additional_context="Focus on tech companies",
    )
    assert "Focus on tech companies" in msg


def test_build_user_message_truncates_long_document(generator):
    """Documents longer than MAX_TEXT_LENGTH_FOR_LLM chars must be truncated."""
    long_doc = "A" * (generator.MAX_TEXT_LENGTH_FOR_LLM + 1000)
    msg = generator._build_user_message(
        document_texts=[long_doc],
        simulation_requirement="req",
        additional_context=None,
    )
    assert "[truncated:" in msg


def test_build_user_message_truncates_long_simulation_requirement(generator):
    """Long simulation_requirement must be truncated at MAX_SIM_REQ_LENGTH."""
    long_req = "B" * (generator.MAX_SIM_REQ_LENGTH + 500)
    msg = generator._build_user_message(
        document_texts=["Doc"],
        simulation_requirement=long_req,
        additional_context=None,
    )
    # The full long_req should not appear verbatim — it was cut
    assert long_req not in msg
    assert "..." in msg


def test_build_user_message_multiple_docs_joined(generator):
    msg = generator._build_user_message(
        document_texts=["First doc", "Second doc"],
        simulation_requirement="req",
        additional_context=None,
    )
    assert "First doc" in msg
    assert "Second doc" in msg


# ---------------------------------------------------------------------------
# _validate_and_process
# ---------------------------------------------------------------------------

def test_validate_ensures_entity_types_key(generator):
    result = generator._validate_and_process({})
    assert "entity_types" in result


def test_validate_ensures_edge_types_key(generator):
    result = generator._validate_and_process({})
    assert "edge_types" in result


def test_validate_ensures_analysis_summary_key(generator):
    result = generator._validate_and_process({})
    assert "analysis_summary" in result


def test_validate_adds_person_fallback_if_missing(generator):
    """If 'Person' entity type is absent, _validate_and_process must inject it."""
    result = generator._validate_and_process({
        "entity_types": [{"name": "Company", "description": "A company"}],
        "edge_types": [],
    })
    names = [e["name"] for e in result["entity_types"]]
    assert "Person" in names


def test_validate_adds_organization_fallback_if_missing(generator):
    result = generator._validate_and_process({
        "entity_types": [{"name": "Person", "description": "A person"}],
        "edge_types": [],
    })
    names = [e["name"] for e in result["entity_types"]]
    assert "Organization" in names


def test_validate_does_not_duplicate_person(generator):
    result = generator._validate_and_process({
        "entity_types": [
            {"name": "Person", "description": "A person"},
            {"name": "Organization", "description": "An org"},
        ],
        "edge_types": [],
    })
    person_count = sum(1 for e in result["entity_types"] if e["name"] == "Person")
    assert person_count == 1


def test_validate_caps_entity_types_at_10(generator):
    many_entities = [{"name": f"Type{i}", "description": "desc"} for i in range(15)]
    result = generator._validate_and_process({
        "entity_types": many_entities,
        "edge_types": [],
    })
    assert len(result["entity_types"]) <= 10


def test_validate_caps_edge_types_at_10(generator):
    many_edges = [{"name": f"EDGE_{i}", "description": "desc"} for i in range(15)]
    result = generator._validate_and_process({
        "entity_types": [],
        "edge_types": many_edges,
    })
    assert len(result["edge_types"]) <= 10


def test_validate_truncates_long_entity_description(generator):
    long_desc = "X" * 200
    result = generator._validate_and_process({
        "entity_types": [{"name": "Thing", "description": long_desc}],
        "edge_types": [],
    })
    entity = next(e for e in result["entity_types"] if e["name"] == "Thing")
    assert len(entity["description"]) <= 100


def test_validate_truncates_long_edge_description(generator):
    long_desc = "Y" * 200
    result = generator._validate_and_process({
        "entity_types": [],
        "edge_types": [{"name": "LONG_EDGE", "description": long_desc}],
    })
    edge = next(e for e in result["edge_types"] if e["name"] == "LONG_EDGE")
    assert len(edge["description"]) <= 100


def test_validate_adds_missing_attributes_key_to_entity(generator):
    result = generator._validate_and_process({
        "entity_types": [{"name": "Company", "description": "A company"}],
        "edge_types": [],
    })
    company = next((e for e in result["entity_types"] if e["name"] == "Company"), None)
    assert company is not None
    assert "attributes" in company


def test_validate_adds_missing_examples_key_to_entity(generator):
    result = generator._validate_and_process({
        "entity_types": [{"name": "Company", "description": "A company"}],
        "edge_types": [],
    })
    company = next((e for e in result["entity_types"] if e["name"] == "Company"), None)
    assert "examples" in company


# ---------------------------------------------------------------------------
# generate() — end-to-end with mocked LLM
# ---------------------------------------------------------------------------

def test_generate_calls_llm_client(generator):
    generator.llm_client.chat_json.return_value = {
        "entity_types": [
            {"name": "Person", "description": "A person"},
            {"name": "Organization", "description": "An org"},
        ],
        "edge_types": [],
        "analysis_summary": "Test summary",
    }
    result = generator.generate(
        document_texts=["A news article about a product launch"],
        simulation_requirement="Simulate public reaction",
    )
    generator.llm_client.chat_json.assert_called_once()
    assert "entity_types" in result
    assert "edge_types" in result


def test_generate_returns_analysis_summary(generator):
    generator.llm_client.chat_json.return_value = {
        "entity_types": [],
        "edge_types": [],
        "analysis_summary": "This text is about a corporate scandal",
    }
    result = generator.generate(
        document_texts=["Doc"],
        simulation_requirement="req",
    )
    assert result["analysis_summary"] == "This text is about a corporate scandal"
