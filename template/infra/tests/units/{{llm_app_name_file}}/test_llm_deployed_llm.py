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
Unit tests for configurations/<app>/deployed_llm.py.

Mocking strategy
----------------
deployed_llm.py runs side-effectful calls at module level and imports
`use_case` from its parent package, which doesn't exist in the test
context.  We:
  - register a MagicMock for configurations.llm.use_case in sys.modules
  - mock Pulumi resource classes so no engine is needed
  - mock validate_feature_flags / verify_llm in the lib module
  - set the required LLM_DEPLOYMENT_ID env var

pulumi_datarobot Arg classes are replaced with a plain namedtuple so
the resulting parameter lists can be inspected without a running engine.
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

    monkeypatch.setenv("LLM_DEPLOYMENT_ID", "fake-deployment-id")
    monkeypatch.delenv("LLM_DEFAULT_MODEL", raising=False)

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


def _reload_dl():
    import configurations.llm.deployed_llm as dl

    importlib.reload(dl)
    return dl


# ---------------------------------------------------------------------------
# app_runtime_parameters
# ---------------------------------------------------------------------------


def test_app_runtime_parameters_contains_deployment_id_key():
    dl = _reload_dl()
    keys = [p.key for p in dl.app_runtime_parameters]
    assert "LLM_DEPLOYMENT_ID" in keys


def test_app_runtime_parameters_contains_default_model_key():
    dl = _reload_dl()
    keys = [p.key for p in dl.app_runtime_parameters]
    assert "LLM_DEFAULT_MODEL" in keys


def test_app_runtime_parameters_contains_friendly_name_key():
    dl = _reload_dl()
    keys = [p.key for p in dl.app_runtime_parameters]
    assert "LLM_DEFAULT_MODEL_FRIENDLY_NAME" in keys


def test_app_runtime_parameters_gateway_flag_is_disabled():
    dl = _reload_dl()
    param = next(p for p in dl.app_runtime_parameters if p.key == "USE_DATAROBOT_LLM_GATEWAY")
    assert param.value == "0"


# ---------------------------------------------------------------------------
# custom_model_runtime_parameters
# ---------------------------------------------------------------------------


def test_custom_model_runtime_parameters_contains_deployment_id_key():
    dl = _reload_dl()
    keys = [p.key for p in dl.custom_model_runtime_parameters]
    assert "LLM_DEPLOYMENT_ID" in keys


def test_custom_model_runtime_parameters_contains_default_model_key():
    dl = _reload_dl()
    keys = [p.key for p in dl.custom_model_runtime_parameters]
    assert "LLM_DEFAULT_MODEL" in keys


def test_custom_model_runtime_parameters_gateway_flag_is_disabled():
    dl = _reload_dl()
    param = next(
        p for p in dl.custom_model_runtime_parameters if p.key == "USE_DATAROBOT_LLM_GATEWAY"
    )
    assert param.value == "0"


# ---------------------------------------------------------------------------
# default_model
# ---------------------------------------------------------------------------


def test_default_model_fallback_when_env_var_not_set():
    dl = _reload_dl()
    assert dl.default_model == "datarobot/datarobot-deployed-llm"


def test_default_model_reads_from_env_var(monkeypatch):
    monkeypatch.setenv("LLM_DEFAULT_MODEL", "datarobot/datarobot-deployed-llm")
    dl = _reload_dl()
    assert dl.default_model == "datarobot/datarobot-deployed-llm"


# ---------------------------------------------------------------------------
# Validation calls at module load time
# ---------------------------------------------------------------------------


def test_validate_feature_flags_is_called():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.deployed_llm as dl

    lib_mod.validate_feature_flags.reset_mock()
    importlib.reload(dl)
    assert lib_mod.validate_feature_flags.called


def test_verify_llm_is_called_with_deployment_id():
    lib_mod = next(
        mod
        for name, mod in sys.modules.items()
        if name.startswith("configurations.") and name.endswith("libllm")
    )
    import configurations.llm.deployed_llm as dl

    lib_mod.verify_llm.reset_mock()
    importlib.reload(dl)
    assert lib_mod.verify_llm.called
    _, kwargs = lib_mod.verify_llm.call_args
    assert "deployment_id" in kwargs
