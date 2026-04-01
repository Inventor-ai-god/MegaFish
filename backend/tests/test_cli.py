"""
Tests for CLI command registration and client helper functions.
Does NOT invoke the backend server or any external service.
Uses Typer's CliRunner to exercise command registration and help output.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock


runner = CliRunner()


def _get_app():
    """Import the CLI Typer app with filesystem-touching installer mocked out."""
    with patch("cli.installer.is_installed", return_value=True):
        from cli.main import app
    return app


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------

def test_help_command_exits_zero():
    app = _get_app()
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0


def test_help_output_mentions_commands():
    app = _get_app()
    result = runner.invoke(app, ["help"])
    # Should list at least some known subcommands
    assert "update" in result.output or "status" in result.output


def test_status_command_is_registered():
    app = _get_app()
    with (
        patch("cli.launcher.check_neo4j", return_value=False),
        patch("cli.launcher.check_ollama", return_value=False),
        patch("cli.launcher.check_backend", return_value=False),
        patch("cli.launcher.check_frontend", return_value=False),
    ):
        result = runner.invoke(app, ["status"])
    assert "No such command" not in result.output
    assert result.exit_code == 0


def test_stop_command_is_registered():
    app = _get_app()
    with patch("cli.launcher.stop_all", return_value=None):
        result = runner.invoke(app, ["stop"])
    assert "No such command" not in result.output
    assert result.exit_code == 0


def test_install_command_is_registered():
    app = _get_app()
    with patch("cli.installer.run_install", return_value=None):
        result = runner.invoke(app, ["install"])
    assert "No such command" not in result.output


def test_update_command_is_registered():
    app = _get_app()
    with patch("cli.installer.run_update", return_value=None):
        result = runner.invoke(app, ["update"])
    assert "No such command" not in result.output


def test_uninstall_command_is_registered():
    app = _get_app()
    with patch("cli.installer.run_uninstall", return_value=None):
        result = runner.invoke(app, ["uninstall"])
    assert "No such command" not in result.output


# ---------------------------------------------------------------------------
# client.py — pure function tests (no network)
# ---------------------------------------------------------------------------

def test_get_result_url_contains_sim_id():
    from cli.client import get_result_url
    url = get_result_url("sim_abc123", 3000)
    assert "sim_abc123" in url


def test_get_result_url_contains_port():
    from cli.client import get_result_url
    url = get_result_url("sim_xyz", 4321)
    assert "4321" in url


def test_get_result_url_default_port():
    from cli.client import get_result_url
    url = get_result_url("sim_test")
    assert "3000" in url


def test_poll_task_returns_on_completed(monkeypatch):
    """poll_task must return immediately when task status is 'completed'."""
    import cli.client as _client

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"status": "completed", "message": "done", "progress": 100},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_response):
        result = _client.poll_task("task_abc", interval=0)

    assert result["status"] == "completed"


def test_poll_task_returns_on_failed(monkeypatch):
    """poll_task must return when task status is 'failed'."""
    import cli.client as _client

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": False,
        "data": {"status": "failed", "message": "LLM timeout", "progress": 0},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_response):
        result = _client.poll_task("task_fail", interval=0)

    assert result["status"] == "failed"


def test_poll_task_calls_on_progress_callback():
    """poll_task must invoke the on_progress callback with the task message."""
    import cli.client as _client

    messages_received = []

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"status": "completed", "message": "Graph complete", "progress": 100},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_response):
        _client.poll_task("task_progress", on_progress=messages_received.append, interval=0)

    assert len(messages_received) >= 1
    assert "Graph complete" in messages_received[0]
