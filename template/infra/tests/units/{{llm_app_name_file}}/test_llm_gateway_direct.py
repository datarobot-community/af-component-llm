# Copyright 2025 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Unit tests for configurations/<app>/gateway_direct.py.

Mocking strategy
----------------
gateway_direct.py runs several side-effectful calls at module level
(validate_feature_flags, verify_llm_gateway_model_availability, verify_llm,
export).  We patch those in the lib module before every reload so the module
executes cleanly and we can inspect the resulting module-level attributes.

pulumi_datarobot's Arg classes are replaced with a plain namedtuple so the
resulting parameter lists can be inspected without a running Pulumi engine.
"""

import importlib
import sys
from collections import namedtuple
from unittest.mock import MagicMock

import pytest

# Namedtuple mirrors the .key/.type/.value interface of the real Arg classes.
Param = namedtuple("Param", ["key", "type", "value"], defaults=[None, None, None])


@pytest.fixture(autouse=True)
def _mocks(monkeypatch):
    import pulumi
    import pulumi_datarobot
    import datarobot_pulumi_utils.pulumi as dpu_pulumi

    # lib module was loaded by conftest as configurations.<app>.lib<app>
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )

    monkeypatch.setattr(pulumi, "get_project", MagicMock(return_value="unittest"))
    monkeypatch.setattr(pulumi_datarobot, "ApplicationSourceRuntimeParameterValueArgs", Param)
    monkeypatch.setattr(pulumi_datarobot, "CustomModelRuntimeParameterValueArgs", Param)
    monkeypatch.setattr(dpu_pulumi, "export", MagicMock())
    monkeypatch.setattr(lib_mod, "validate_feature_flags", MagicMock())
    monkeypatch.setattr(lib_mod, "verify_llm_gateway_model_availability", MagicMock())
    monkeypatch.setattr(lib_mod, "verify_llm", MagicMock())
    monkeypatch.delenv("LLM_DEFAULT_MODEL", raising=False)


def _reload_gd():
    """Return a freshly-reloaded gateway_direct module."""
    import configurations.llm.gateway_direct as gd

    importlib.reload(gd)
    return gd


# ---------------------------------------------------------------------------
# app_runtime_parameters
# ---------------------------------------------------------------------------


def test_app_runtime_parameters_contains_gateway_flag():
    gd = _reload_gd()
    keys = [p.key for p in gd.app_runtime_parameters]
    assert "USE_DATAROBOT_LLM_GATEWAY" in keys


def test_app_runtime_parameters_contains_default_model_key():
    gd = _reload_gd()
    keys = [p.key for p in gd.app_runtime_parameters]
    assert "LLM_DEFAULT_MODEL" in keys


def test_app_runtime_parameters_gateway_flag_value_is_one():
    gd = _reload_gd()
    param = next(p for p in gd.app_runtime_parameters if p.key == "USE_DATAROBOT_LLM_GATEWAY")
    assert param.value == "1"


# ---------------------------------------------------------------------------
# custom_model_runtime_parameters
# ---------------------------------------------------------------------------


def test_custom_model_runtime_parameters_contains_gateway_flag():
    gd = _reload_gd()
    keys = [p.key for p in gd.custom_model_runtime_parameters]
    assert "USE_DATAROBOT_LLM_GATEWAY" in keys


def test_custom_model_runtime_parameters_contains_default_model_key():
    gd = _reload_gd()
    keys = [p.key for p in gd.custom_model_runtime_parameters]
    assert "LLM_DEFAULT_MODEL" in keys


def test_custom_model_runtime_parameters_gateway_flag_value_is_one():
    gd = _reload_gd()
    param = next(p for p in gd.custom_model_runtime_parameters if p.key == "USE_DATAROBOT_LLM_GATEWAY")
    assert param.value == "1"


# ---------------------------------------------------------------------------
# default_model selection and prefix normalisation
# ---------------------------------------------------------------------------


def test_default_model_fallback_when_env_var_not_set():
    gd = _reload_gd()
    assert gd.default_model == "datarobot/azure/gpt-5-mini-2025-08-07"


def test_default_model_reads_from_env_var(monkeypatch):
    monkeypatch.setenv("LLM_DEFAULT_MODEL", "datarobot/azure/my-model")
    gd = _reload_gd()
    assert gd.default_model == "datarobot/azure/my-model"


def test_default_model_adds_datarobot_prefix_when_missing(monkeypatch):
    monkeypatch.setenv("LLM_DEFAULT_MODEL", "azure/my-model")
    gd = _reload_gd()
    assert gd.default_model == "datarobot/azure/my-model"


def test_default_model_does_not_double_prefix(monkeypatch):
    monkeypatch.setenv("LLM_DEFAULT_MODEL", "datarobot/azure/my-model")
    gd = _reload_gd()
    assert not gd.default_model.startswith("datarobot/datarobot/")


# ---------------------------------------------------------------------------
# Validation calls at module load time
# ---------------------------------------------------------------------------


def test_validate_feature_flags_is_called():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.gateway_direct as gd

    lib_mod.validate_feature_flags.reset_mock()
    importlib.reload(gd)
    assert lib_mod.validate_feature_flags.called


def test_verify_llm_gateway_model_availability_is_called():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.gateway_direct as gd

    lib_mod.verify_llm_gateway_model_availability.reset_mock()
    importlib.reload(gd)
    assert lib_mod.verify_llm_gateway_model_availability.called


def test_verify_llm_is_called_with_use_llm_gateway_true():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.gateway_direct as gd

    lib_mod.verify_llm.reset_mock()
    importlib.reload(gd)
    assert lib_mod.verify_llm.called
    _, kwargs = lib_mod.verify_llm.call_args
    assert kwargs.get("use_llm_gateway") is True
