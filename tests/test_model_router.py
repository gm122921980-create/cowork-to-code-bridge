"""Tests for model router gateway system.

Tests the route_task() function that intelligently selects Claude model tiers
for token efficiency, with mandatory complexity declaration and fallback cascading.
"""
import json
import tempfile
from pathlib import Path

import pytest

from cowork_to_code_bridge.model_router import (
    FallbackStrategy,
    ModelTier,
    _get_cascade_order,
    _validate_model_preference,
    get_routing_metadata,
    get_routing_recommendations,
    route_task,
)


# ─────────────────────────────────────────────────────────────────────────── #
# Model Preference Validation
# ─────────────────────────────────────────────────────────────────────────── #


def test_validate_model_preference_required():
    """model_preference is MANDATORY — raises ValueError if None."""
    with pytest.raises(ValueError, match="MANDATORY"):
        _validate_model_preference(None)


def test_validate_model_preference_string():
    """Accepts string model names (case-insensitive)."""
    assert _validate_model_preference("haiku") == ModelTier.HAIKU
    assert _validate_model_preference("SONNET") == ModelTier.SONNET
    assert _validate_model_preference("OpUs") == ModelTier.OPUS
    assert _validate_model_preference("fabo") == ModelTier.FABO


def test_validate_model_preference_enum():
    """Accepts ModelTier enum directly."""
    assert _validate_model_preference(ModelTier.OPUS) == ModelTier.OPUS


def test_validate_model_preference_invalid():
    """Rejects invalid model names with clear error."""
    with pytest.raises(ValueError, match="Invalid model_preference"):
        _validate_model_preference("gpt-4")
    with pytest.raises(ValueError):
        _validate_model_preference("claude")


def test_validate_model_preference_type_error():
    """Rejects non-string, non-enum types."""
    with pytest.raises(TypeError):
        _validate_model_preference(123)
    with pytest.raises(TypeError):
        _validate_model_preference(["haiku"])


# ─────────────────────────────────────────────────────────────────────────── #
# Cascade Order Logic
# ─────────────────────────────────────────────────────────────────────────── #


def test_cascade_up_from_haiku():
    """CASCADE_UP from Haiku: Haiku → Sonnet → Opus → Fabo."""
    order = _get_cascade_order(ModelTier.HAIKU, FallbackStrategy.CASCADE_UP)
    assert order == [ModelTier.HAIKU, ModelTier.SONNET, ModelTier.OPUS, ModelTier.FABO]


def test_cascade_up_from_sonnet():
    """CASCADE_UP from Sonnet: Sonnet → Opus → Fabo."""
    order = _get_cascade_order(ModelTier.SONNET, FallbackStrategy.CASCADE_UP)
    assert order == [ModelTier.SONNET, ModelTier.OPUS, ModelTier.FABO]


def test_cascade_up_from_fabo():
    """CASCADE_UP from Fabo: just Fabo (already at top)."""
    order = _get_cascade_order(ModelTier.FABO, FallbackStrategy.CASCADE_UP)
    assert order == [ModelTier.FABO]


def test_cascade_down_from_fabo():
    """CASCADE_DOWN from Fabo: Fabo → Opus → Sonnet → Haiku."""
    order = _get_cascade_order(ModelTier.FABO, FallbackStrategy.CASCADE_DOWN)
    assert order == [ModelTier.FABO, ModelTier.OPUS, ModelTier.SONNET, ModelTier.HAIKU]


def test_cascade_down_from_sonnet():
    """CASCADE_DOWN from Sonnet: Sonnet → Haiku."""
    order = _get_cascade_order(ModelTier.SONNET, FallbackStrategy.CASCADE_DOWN)
    assert order == [ModelTier.SONNET, ModelTier.HAIKU]


def test_cascade_down_from_haiku():
    """CASCADE_DOWN from Haiku: just Haiku (already at bottom)."""
    order = _get_cascade_order(ModelTier.HAIKU, FallbackStrategy.CASCADE_DOWN)
    assert order == [ModelTier.HAIKU]


def test_fail_fast_strategy():
    """FAIL_FAST: only try the requested model, no fallback."""
    for tier in [ModelTier.HAIKU, ModelTier.SONNET, ModelTier.OPUS, ModelTier.FABO]:
        order = _get_cascade_order(tier, FallbackStrategy.FAIL_FAST)
        assert order == [tier], f"FAIL_FAST should only return {tier}"


def test_cascade_with_string_strategy():
    """Cascade order accepts string strategy names."""
    order = _get_cascade_order(ModelTier.HAIKU, "cascade_up")
    assert order == [ModelTier.HAIKU, ModelTier.SONNET, ModelTier.OPUS, ModelTier.FABO]


# ─────────────────────────────────────────────────────────────────────────── #
# route_task() Function
# ─────────────────────────────────────────────────────────────────────────── #


def test_route_task_requires_model_preference():
    """route_task() raises ValueError if model_preference is missing."""
    with pytest.raises(ValueError, match="MANDATORY"):
        route_task("scripts/test.sh", model_preference=None)


def test_route_task_accepts_valid_preference():
    """route_task() accepts valid model preferences and returns task_id."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            args=["arg1"],
            model_preference="opus",
            bridge_root=bridge_root,
        )

        assert "task_id" in result
        assert result["status"] == "queued"
        assert result["requested_model"] == "opus"
        assert result["selected_model"] == "opus"
        assert result["fallback_used"] is False


def test_route_task_returns_routing_metadata():
    """route_task() return includes full routing metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/analyze.sh",
            args=["data.csv"],
            model_preference="sonnet",
            fallback_strategy="cascade_up",
            bridge_root=bridge_root,
        )

        assert "routing_metadata" in result
        routing = result["routing_metadata"]
        assert routing["requested_model"] == "sonnet"
        assert routing["selected_model"] == "sonnet"
        assert routing["fallback_strategy"] == "cascade_up"
        assert routing["fallback_used"] is False
        assert "cascade_order" in routing
        assert "ts_routed" in routing


def test_route_task_persists_routing_file():
    """route_task() stores routing metadata in routing/ folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            model_preference="haiku",
            bridge_root=bridge_root,
        )

        task_id = result["task_id"]
        routing_file = bridge_root / "routing" / f"{task_id}.json"
        assert routing_file.exists(), "Routing metadata should be persisted"

        routing_data = json.loads(routing_file.read_text())
        assert routing_data["selected_model"] == "haiku"


def test_route_task_atomic_write():
    """Routing metadata is written atomically (.tmp → rename)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            model_preference="opus",
            bridge_root=bridge_root,
        )

        task_id = result["task_id"]
        routing_file = bridge_root / "routing" / f"{task_id}.json"
        tmp_file = routing_file.with_suffix(".json.tmp")

        # File should exist, temp file should not
        assert routing_file.exists()
        assert not tmp_file.exists()


def test_route_task_idempotency_key():
    """route_task() respects idempotency_key parameter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        key = "my-unique-key-123"
        result = route_task(
            "scripts/test.sh",
            model_preference="sonnet",
            idempotency_key=key,
            bridge_root=bridge_root,
        )

        # Task should be queued with the key
        assert result["status"] == "queued"


def test_route_task_cascade_up():
    """route_task() with CASCADE_UP includes full cascade in metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            model_preference="haiku",
            fallback_strategy="cascade_up",
            bridge_root=bridge_root,
        )

        cascade = result["routing_metadata"]["cascade_order"]
        assert cascade == ["haiku", "sonnet", "opus", "fabo"]


def test_route_task_cascade_down():
    """route_task() with CASCADE_DOWN includes full cascade in metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            model_preference="fabo",
            fallback_strategy="cascade_down",
            bridge_root=bridge_root,
        )

        cascade = result["routing_metadata"]["cascade_order"]
        assert cascade == ["fabo", "opus", "sonnet", "haiku"]


def test_route_task_fail_fast():
    """route_task() with FAIL_FAST has single model in cascade."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            model_preference="opus",
            fallback_strategy="fail_fast",
            bridge_root=bridge_root,
        )

        cascade = result["routing_metadata"]["cascade_order"]
        assert cascade == ["opus"]


# ─────────────────────────────────────────────────────────────────────────── #
# Routing Metadata Retrieval
# ─────────────────────────────────────────────────────────────────────────── #


def test_get_routing_metadata_exists():
    """get_routing_metadata() retrieves stored routing info."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        result = route_task(
            "scripts/test.sh",
            model_preference="sonnet",
            bridge_root=bridge_root,
        )

        task_id = result["task_id"]
        routing_data = get_routing_metadata(task_id, bridge_root=bridge_root)

        assert routing_data is not None
        assert routing_data["selected_model"] == "sonnet"


def test_get_routing_metadata_not_found():
    """get_routing_metadata() returns None for non-existent task."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        (bridge_root / "routing").mkdir(exist_ok=True)

        result = get_routing_metadata("nonexistent_task_xyz", bridge_root=bridge_root)
        assert result is None


# ─────────────────────────────────────────────────────────────────────────── #
# Routing Recommendations (Informational)
# ─────────────────────────────────────────────────────────────────────────── #


def test_get_routing_recommendations():
    """get_routing_recommendations() provides reference guidance."""
    recs = get_routing_recommendations("Analyze quarterly data")

    assert "recommended_tier" in recs
    assert "reasoning" in recs
    assert "can_use_cheaper" in recs
    assert "must_use_expensive" in recs
    # Default recommendation is Sonnet
    assert recs["recommended_tier"] == "sonnet"


def test_get_routing_recommendations_no_error():
    """get_routing_recommendations() doesn't fail on any input."""
    for task in [
        "",
        "x" * 1000,
        None,  # type check: our function accepts str but should handle gracefully
    ]:
        try:
            recs = get_routing_recommendations(task if task is not None else "")
            assert isinstance(recs, dict)
        except Exception as e:
            pytest.fail(f"get_routing_recommendations raised {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────────────────── #
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────── #


def test_route_task_full_workflow():
    """Full workflow: route task → retrieve metadata → verify consistency."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        # 1. Route a task
        route_result = route_task(
            "scripts/complex_analysis.sh",
            args=["large_dataset.csv"],
            model_preference="opus",
            fallback_strategy="cascade_up",
            bridge_root=bridge_root,
        )

        task_id = route_result["task_id"]

        # 2. Verify task was queued
        assert route_result["status"] == "queued"
        assert route_result["selected_model"] == "opus"

        # 3. Retrieve routing metadata
        routing_data = get_routing_metadata(task_id, bridge_root=bridge_root)
        assert routing_data is not None

        # 4. Verify consistency between route_result and stored metadata
        assert routing_data["selected_model"] == route_result["selected_model"]
        assert routing_data["requested_model"] == route_result["requested_model"]
        assert routing_data["fallback_strategy"] == "cascade_up"


def test_route_task_all_tiers():
    """route_task() works for all model tiers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bridge_root = Path(tmpdir)
        for sub in ("queue", "results", "routing"):
            (bridge_root / sub).mkdir(exist_ok=True)

        for tier in ["haiku", "sonnet", "opus", "fabo"]:
            result = route_task(
                "scripts/test.sh",
                model_preference=tier,
                bridge_root=bridge_root,
            )

            assert result["selected_model"] == tier
            assert result["status"] == "queued"
