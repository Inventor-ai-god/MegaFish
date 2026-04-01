"""
Tests for Flask app creation and key route registration.
Does NOT require Neo4j, Ollama, or any external service.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def app():
    """Create the Flask app with Neo4j mocked out."""
    # Patch Neo4jStorage so __init__ doesn't attempt a real DB connection
    with patch("app.storage.Neo4jStorage") as MockStorage:
        MockStorage.return_value = MagicMock()
        from app import create_app
        flask_app = create_app()
        flask_app.config["TESTING"] = True
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_endpoint_returns_200(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_health_response_has_status_ok(client):
    res = client.get("/health")
    data = res.get_json()
    assert data["status"] == "ok"


def test_health_response_has_service_name(client):
    res = client.get("/health")
    data = res.get_json()
    assert "MegaFish" in data["service"]


# ---------------------------------------------------------------------------
# Route registration — graph blueprint
# ---------------------------------------------------------------------------

def test_graph_ontology_generate_route_registered(app):
    """POST /api/graph/ontology/generate must be registered."""
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/graph/ontology/generate" in rules


def test_graph_build_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/graph/build" in rules


def test_graph_task_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/graph/task/<task_id>" in rules


def test_graph_project_list_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/graph/project/list" in rules


# ---------------------------------------------------------------------------
# Route registration — simulation blueprint
# ---------------------------------------------------------------------------

def test_simulation_create_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/simulation/create" in rules


def test_simulation_world_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/simulation/world" in rules


# ---------------------------------------------------------------------------
# Route registration — report blueprint
# ---------------------------------------------------------------------------

def test_report_generate_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/report/generate" in rules


def test_report_chat_route_registered(app):
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/api/report/chat" in rules


# ---------------------------------------------------------------------------
# Basic 400 validation — no DB needed for input-validation paths
# ---------------------------------------------------------------------------

def test_graph_build_missing_project_id_returns_400(client):
    """POST /api/graph/build with empty body must return 400."""
    res = client.post("/api/graph/build", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False


def test_simulation_create_missing_project_id_returns_400(client):
    res = client.post("/api/simulation/create", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False


def test_report_generate_missing_simulation_id_returns_400(client):
    res = client.post("/api/report/generate", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False


def test_graph_task_not_found_returns_404(client):
    res = client.get("/api/graph/task/nonexistent-task-id")
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False


def test_graph_project_not_found_returns_404(client):
    res = client.get("/api/graph/project/proj_nonexistent")
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False
