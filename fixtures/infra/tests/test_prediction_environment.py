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
Tests for the prediction environment creation logic that uses
DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT to optionally inject a pre-existing
prediction environment instead of creating a new one.

This logic lives in the template configuration files:
  - configurations/<name>/blueprint_with_external_llm.py
  - configurations/<name>/blueprint_with_llm_gateway.py
  - configurations/<name>/registered_model.py
"""

import os
from unittest.mock import MagicMock

EXISTING_PREDICTION_ENV_ID = "abc123existing"
RESOURCE_NAME = "LLM Prediction Environment [test]"


def _resolve_prediction_environment(datarobot, dr, resource_name: str):
    """
    Mirrors the prediction_environment resolution block used in all template
    configurations that create a deployment.
    """
    if prediction_environment_id := os.environ.get(
        "DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT"
    ):
        return datarobot.PredictionEnvironment.get(
            id=prediction_environment_id,
            resource_name=resource_name + " [PRE-EXISTING]",
        )
    else:
        return datarobot.PredictionEnvironment(
            resource_name=resource_name,
            platform=dr.enums.PredictionEnvironmentPlatform.DATAROBOT_SERVERLESS,
        )


def test_creates_new_prediction_environment_when_env_var_not_set(monkeypatch):
    """Without DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT a new PredictionEnvironment is created."""
    monkeypatch.delenv("DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT", raising=False)
    mock_datarobot = MagicMock()
    mock_dr = MagicMock()

    _resolve_prediction_environment(mock_datarobot, mock_dr, RESOURCE_NAME)

    mock_datarobot.PredictionEnvironment.assert_called_once_with(
        resource_name=RESOURCE_NAME,
        platform=mock_dr.enums.PredictionEnvironmentPlatform.DATAROBOT_SERVERLESS,
    )
    mock_datarobot.PredictionEnvironment.get.assert_not_called()


def test_uses_existing_prediction_environment_when_env_var_set(monkeypatch):
    """With DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT set, PredictionEnvironment.get() is used."""
    monkeypatch.setenv(
        "DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT", EXISTING_PREDICTION_ENV_ID
    )
    mock_datarobot = MagicMock()
    mock_dr = MagicMock()

    _resolve_prediction_environment(mock_datarobot, mock_dr, RESOURCE_NAME)

    mock_datarobot.PredictionEnvironment.get.assert_called_once_with(
        id=EXISTING_PREDICTION_ENV_ID,
        resource_name=RESOURCE_NAME + " [PRE-EXISTING]",
    )
    mock_datarobot.PredictionEnvironment.assert_not_called()
