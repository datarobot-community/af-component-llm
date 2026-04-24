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
Unit tests for configurations/<app>/nim_deployed_llm.py.

Mocking strategy
----------------
nim_deployed_llm.py is structurally identical to deployed_llm.py but
uses NIM-specific env var names (LLM_NIM_DEPLOYMENT_ID,
LLM_NIM_DEFAULT_MODEL, LLM_NIM_DEFAULT_MODEL_FRIENDLY_NAME).  The same
mocking strategy applies: register a use_case mock, stub Pulumi resource
classes, and patch lib functions to prevent real API calls.
"""

import importlib
import sys
from collections import namedtuple
from unittest.mock import MagicMock

import pytest

Param = namedtuple("Param", ["key", "type", "value"], defaults=[None, None, None])


@pytest.fixture(autouse=True)
def _mocks(monkeypatch):
    import pulumi
    import pulumi_datarobot
    import datarobot_pulumi_utils.pulumi as dpu_pulumi

    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )

    # `from . import use_case` needs configurations.llm.use_case to resolve
    use_case_mock = MagicMock()
    app_pkg = sys.modules["configurations.llm"]
    monkeypatch.setattr(app_pkg, "use_case", use_case_mock, raising=False)
    monkeypatch.setitem(sys.modules, "configurations.llm.use_case", use_case_mock)

    monkeypatch.setenv("LLM_NIM_DEPLOYMENT_ID", "fake-nim-deployment-id")
    monkeypatch.delenv("LLM_NIM_DEFAULT_MODEL", raising=False)

    monkeypatch.setattr(pulumi, "get_project", MagicMock(return_value="unittest"))
    monkeypatch.setattr(pulumi, "export", MagicMock())
    monkeypatch.setattr(pulumi_datarobot, "ApplicationSourceRuntimeParameterValueArgs", Param)
    monkeypatch.setattr(pulumi_datarobot, "CustomModelRuntimeParameterValueArgs", Param)
    monkeypatch.setattr(pulumi_datarobot, "Playground", MagicMock())
    monkeypatch.setattr(pulumi_datarobot, "Deployment", MagicMock())
    monkeypatch.setattr(pulumi_datarobot, "PredictionEnvironment", MagicMock())
    monkeypatch.setattr(dpu_pulumi, "export", MagicMock())
    monkeypatch.setattr(lib_mod, "validate_feature_flags", MagicMock())
    monkeypatch.setattr(lib_mod, "verify_llm", MagicMock())


def _reload_nim():
    import configurations.llm.nim_deployed_llm as nim

    importlib.reload(nim)
    return nim


# ---------------------------------------------------------------------------
# app_runtime_parameters
# ---------------------------------------------------------------------------


def test_app_runtime_parameters_contains_nim_deployment_id_key():
    nim = _reload_nim()
    keys = [p.key for p in nim.app_runtime_parameters]
    assert "LLM_NIM_DEPLOYMENT_ID" in keys


def test_app_runtime_parameters_contains_nim_default_model_key():
    nim = _reload_nim()
    keys = [p.key for p in nim.app_runtime_parameters]
    assert "LLM_NIM_DEFAULT_MODEL" in keys


def test_app_runtime_parameters_contains_nim_friendly_name_key():
    nim = _reload_nim()
    keys = [p.key for p in nim.app_runtime_parameters]
    assert "LLM_NIM_DEFAULT_MODEL_FRIENDLY_NAME" in keys


def test_app_runtime_parameters_gateway_flag_is_disabled():
    nim = _reload_nim()
    param = next(p for p in nim.app_runtime_parameters if p.key == "USE_DATAROBOT_LLM_GATEWAY")
    assert param.value == "0"


# ---------------------------------------------------------------------------
# custom_model_runtime_parameters
# ---------------------------------------------------------------------------


def test_custom_model_runtime_parameters_contains_nim_deployment_id_key():
    nim = _reload_nim()
    keys = [p.key for p in nim.custom_model_runtime_parameters]
    assert "LLM_NIM_DEPLOYMENT_ID" in keys


def test_custom_model_runtime_parameters_contains_nim_default_model_key():
    nim = _reload_nim()
    keys = [p.key for p in nim.custom_model_runtime_parameters]
    assert "LLM_NIM_DEFAULT_MODEL" in keys


def test_custom_model_runtime_parameters_gateway_flag_is_disabled():
    nim = _reload_nim()
    param = next(
        p for p in nim.custom_model_runtime_parameters if p.key == "USE_DATAROBOT_LLM_GATEWAY"
    )
    assert param.value == "0"


# ---------------------------------------------------------------------------
# default_model
# ---------------------------------------------------------------------------


def test_default_model_fallback_when_env_var_not_set():
    nim = _reload_nim()
    assert nim.default_model == "datarobot/datarobot-deployed-llm"


def test_default_model_reads_from_env_var(monkeypatch):
    monkeypatch.setenv("LLM_NIM_DEFAULT_MODEL", "datarobot/datarobot-deployed-llm")
    nim = _reload_nim()
    assert nim.default_model == "datarobot/datarobot-deployed-llm"


# ---------------------------------------------------------------------------
# Validation calls at module load time
# ---------------------------------------------------------------------------


def test_validate_feature_flags_is_called():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.nim_deployed_llm as nim

    lib_mod.validate_feature_flags.reset_mock()
    importlib.reload(nim)
    assert lib_mod.validate_feature_flags.called


def test_verify_llm_is_called_with_nim_deployment_id():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.nim_deployed_llm as nim

    lib_mod.verify_llm.reset_mock()
    importlib.reload(nim)
    assert lib_mod.verify_llm.called
    _, kwargs = lib_mod.verify_llm.call_args
    assert "deployment_id" in kwargs
