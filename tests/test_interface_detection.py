"""Tests for interface-aware bridge initialization (bridge_init.py).

Covers:
  - detect_caller_interface() across all six caller types
  - get_initialization_for_interface() tailoring + unknown fallback
  - mark_interface_initialized() marker creation, layout, idempotency
  - serve_init_response() format selection + auto-detection + optional marking
"""
import json

import pytest

from cowork_to_code_bridge.bridge_init import (
    INITIALIZED_DIR,
    INTERFACES,
    detect_caller_interface,
    get_initialization_for_interface,
    is_interface_initialized,
    mark_interface_initialized,
    serve_init_response,
)


# --------------------------------------------------------------------------- #
# detect_caller_interface
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "env, expected",
    [
        # CI/CD wins even when BRIDGE_ROOT + a sandbox marker are also present.
        ({"GITHUB_ACTIONS": "true", "BRIDGE_ROOT": "/b", "COWORK": "1"}, "ci-cd"),
        ({"CI": "true"}, "ci-cd"),
        ({"GITLAB_CI": "true"}, "ci-cd"),
        # Explicit self-identification.
        ({"BRIDGE_CALLER": "hermes-agent-7"}, "hermes"),
        ({"BRIDGE_USER_AGENT": "Cowork/1.0"}, "cowork"),
        ({"BRIDGE_CALLER": "claude-code"}, "claude-code"),
        # Explicit caller that exactly names a known interface.
        ({"BRIDGE_CALLER": "ci-cd"}, "ci-cd"),
        ({"BRIDGE_CALLER": "script"}, "script"),
        # Cowork sandbox: BRIDGE_ROOT + sandbox fingerprint.
        ({"BRIDGE_ROOT": "/b", "COWORK_SESSION_ID": "abc"}, "cowork"),
        ({"BRIDGE_ROOT": "/b", "SANDBOX": "1"}, "cowork"),
        # Claude Code: local execution context.
        ({"BRIDGE_ROOT": "/b", "CLAUDECODE": "1"}, "claude-code"),
        # Script: bridge reachable, no rich identity.
        ({"BRIDGE_ROOT": "/b"}, "script"),
        # Unknown: nothing recognizable.
        ({}, "unknown"),
        # Falsey CI marker must NOT trigger ci-cd.
        ({"CI": "false", "BRIDGE_ROOT": "/b"}, "script"),
    ],
)
def test_detect_caller_interface(env, expected):
    assert detect_caller_interface(env=env) == expected


def test_detect_defaults_to_os_environ(monkeypatch):
    for k in ("CI", "GITHUB_ACTIONS", "BRIDGE_ROOT", "BRIDGE_CALLER",
              "COWORK", "SANDBOX", "CLAUDECODE", "CLAUDE_CODE"):
        monkeypatch.delenv(k, raising=False)
    assert detect_caller_interface() == "unknown"
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    assert detect_caller_interface() == "ci-cd"


# --------------------------------------------------------------------------- #
# get_initialization_for_interface
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("iface", [i for i in INTERFACES])
def test_init_knowledge_present_for_every_interface(iface):
    kb = get_initialization_for_interface(iface)
    assert kb["interface"] == iface
    assert kb["title"]
    assert kb["summary"]
    assert kb["capabilities"] and isinstance(kb["capabilities"], list)
    assert kb["examples"]
    assert kb["format"] in ("markdown", "cli", "structured")


def test_init_knowledge_is_tailored_per_interface():
    cowork = get_initialization_for_interface("cowork")
    ci = get_initialization_for_interface("ci-cd")
    script = get_initialization_for_interface("script")
    # Cowork emphasizes async queue/poll.
    assert any("queue_task" in c for c in cowork["capabilities"])
    # CI emphasizes idempotency.
    assert any("idempotency" in c.lower() for c in ci["capabilities"])
    # Scripts get raw folder format.
    assert any("queue/" in c for c in script["capabilities"])


def test_unknown_interface_falls_back():
    kb = get_initialization_for_interface("totally-made-up")
    assert kb["interface"] == "unknown"
    assert kb["title"]


def test_returned_capabilities_are_a_copy():
    kb = get_initialization_for_interface("cowork")
    kb["capabilities"].append("MUTATED")
    fresh = get_initialization_for_interface("cowork")
    assert "MUTATED" not in fresh["capabilities"]


# --------------------------------------------------------------------------- #
# mark_interface_initialized / is_interface_initialized
# --------------------------------------------------------------------------- #

def test_mark_creates_per_interface_marker(tmp_path):
    res = mark_interface_initialized("cowork", bridge_root=tmp_path)
    marker = tmp_path / INITIALIZED_DIR / "cowork"
    assert marker.exists()
    assert res["already_initialized"] is False
    assert res["initialized"] is True
    assert res["marker_path"] == str(marker)
    payload = json.loads(marker.read_text())
    assert payload["interface"] == "cowork"
    assert payload["ts"] == res["ts"]


def test_mark_is_idempotent_and_preserves_timestamp(tmp_path):
    first = mark_interface_initialized("ci-cd", bridge_root=tmp_path)
    second = mark_interface_initialized("ci-cd", bridge_root=tmp_path)
    assert second["already_initialized"] is True
    assert second["ts"] == first["ts"]


def test_mark_tolerates_corrupt_interface_marker(tmp_path):
    """A pre-existing but unparseable interface marker reports already-initialized."""
    init_dir = tmp_path / INITIALIZED_DIR
    init_dir.mkdir(parents=True)
    (init_dir / "cowork").write_text("garbage{{{")
    res = mark_interface_initialized("cowork", bridge_root=tmp_path)
    assert res["already_initialized"] is True
    assert res["ts"] == 0.0


def test_is_interface_initialized(tmp_path):
    assert is_interface_initialized("hermes", bridge_root=tmp_path) is False
    mark_interface_initialized("hermes", bridge_root=tmp_path)
    assert is_interface_initialized("hermes", bridge_root=tmp_path) is True


def test_interfaces_are_independent(tmp_path):
    mark_interface_initialized("cowork", bridge_root=tmp_path)
    assert is_interface_initialized("cowork", bridge_root=tmp_path) is True
    assert is_interface_initialized("claude-code", bridge_root=tmp_path) is False


def test_unknown_interface_name_normalized_on_mark(tmp_path):
    res = mark_interface_initialized("bogus", bridge_root=tmp_path)
    assert res["interface"] == "unknown"
    assert (tmp_path / INITIALIZED_DIR / "unknown").exists()
    assert not (tmp_path / INITIALIZED_DIR / "bogus").exists()


def test_marker_layout_matches_spec(tmp_path):
    for iface in ("cowork", "claude-code", "ci-cd", "hermes"):
        mark_interface_initialized(iface, bridge_root=tmp_path)
    init_dir = tmp_path / INITIALIZED_DIR
    names = {p.name for p in init_dir.iterdir()}
    assert {"cowork", "claude-code", "ci-cd", "hermes"} <= names


# --------------------------------------------------------------------------- #
# serve_init_response
# --------------------------------------------------------------------------- #

def test_serve_markdown_for_llm_callers():
    out = serve_init_response("cowork")
    assert out.startswith("# ")
    assert "```python" in out
    assert "queue_task" in out


def test_serve_cli_for_scripts():
    out = serve_init_response("script")
    assert not out.startswith("# ")
    assert "Capabilities:" in out
    assert "queue/" in out


def test_serve_structured_for_ci_and_unknown():
    for iface in ("ci-cd", "made-up"):
        out = serve_init_response(iface)
        parsed = json.loads(out)
        assert "capabilities" in parsed and "interface" in parsed


def test_serve_auto_detects(monkeypatch):
    env = {"GITHUB_ACTIONS": "true"}
    out = serve_init_response(env=env)
    parsed = json.loads(out)  # ci-cd → structured
    assert parsed["interface"] == "ci-cd"


def test_serve_does_not_mark_by_default(tmp_path):
    serve_init_response("cowork", bridge_root=tmp_path)
    assert is_interface_initialized("cowork", bridge_root=tmp_path) is False


def test_serve_marks_when_requested(tmp_path):
    serve_init_response("cowork", bridge_root=tmp_path, mark=True)
    assert is_interface_initialized("cowork", bridge_root=tmp_path) is True


def test_serve_marking_is_idempotent(tmp_path):
    serve_init_response("cowork", bridge_root=tmp_path, mark=True)
    serve_init_response("cowork", bridge_root=tmp_path, mark=True)
    # Single marker, no error.
    assert is_interface_initialized("cowork", bridge_root=tmp_path) is True
