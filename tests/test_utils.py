"""Tests for IOIntelligenceUtils model-listing helpers."""

from unittest.mock import patch

import pytest

from langchain_iointelligence.exceptions import IOIntelligenceError
from langchain_iointelligence.utils import IOIntelligenceUtils


def _utils():
    return IOIntelligenceUtils(
        api_key="k", api_url="https://test.api.com/v1/chat/completions"
    )


def _catalog(ids):
    return [{"id": model_id} for model_id in ids]


class TestGetRecommendedModels:
    def test_failure_propagates(self):
        """API failures must propagate, not return a stale fallback list."""
        utils = _utils()
        with patch.object(
            IOIntelligenceUtils,
            "list_models",
            side_effect=IOIntelligenceError("boom"),
        ):
            with pytest.raises(IOIntelligenceError, match="boom"):
                utils.get_recommended_models()

    def test_pattern_matching_selects_flagships(self):
        utils = _utils()
        catalog = _catalog(
            [
                "zai-org/GLM-5",
                "zai-org/GLM-4.7-Flash",
                "deepseek-ai/DeepSeek-V4-Pro",
                "meta-llama/Llama-3.3-70B-Instruct",
                "openai/gpt-oss-20b",
            ]
        )
        with patch.object(IOIntelligenceUtils, "list_models", return_value=catalog):
            recommended = utils.get_recommended_models()
        assert recommended == [
            "zai-org/GLM-5",
            "deepseek-ai/DeepSeek-V4-Pro",
            "meta-llama/Llama-3.3-70B-Instruct",
        ]

    def test_first_three_fallback_when_no_pattern_matches(self):
        utils = _utils()
        catalog = _catalog(["a/model-1", "b/model-2", "c/model-3", "d/model-4"])
        with patch.object(IOIntelligenceUtils, "list_models", return_value=catalog):
            recommended = utils.get_recommended_models()
        assert recommended == ["a/model-1", "b/model-2", "c/model-3"]

    def test_empty_catalog_returns_empty(self):
        utils = _utils()
        with patch.object(IOIntelligenceUtils, "list_models", return_value=[]):
            assert utils.get_recommended_models() == []
