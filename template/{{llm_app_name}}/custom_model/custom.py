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
import logging
from types import SimpleNamespace
from typing import Any

import pandas as pd

# DRUM should be present in the latest moderation environment
from datarobot_drum import RuntimeParameters
from litellm import completion
from openai.types.chat import CompletionCreateParams

logger = logging.getLogger(__name__)


def load_model(code_dir: str) -> SimpleNamespace:
    logger.info("Loading Runtime Parameters..")

    model = RuntimeParameters.get("model")
    client_id = RuntimeParameters.get("client_id")
    base_url = RuntimeParameters.get("base_url")
    api_key = RuntimeParameters.get("api_key")["apiToken"]

    # Can return any object as a placeholder for a model that we can
    # then use again in the `score()` function.
    return SimpleNamespace(**locals())


def _get_genai_completion(**kwargs: Any) -> Any:
    return completion(
        clientId=kwargs.get("clientId"),
        model=kwargs.get("model"),
        messages=kwargs.get("messages"),
        timeout=kwargs.get("timeout"),
        temperature=kwargs.get("temperature"),
        top_p=kwargs.get("top_p"),
        n=kwargs.get("n"),
        stream=kwargs.get("stream"),
        stream_options=kwargs.get("stream_options"),
        stop=kwargs.get("stop"),
        max_completion_tokens=kwargs.get("max_completion_tokens"),
        max_tokens=kwargs.get("max_tokens"),
        modalities=kwargs.get("modalities"),
        prediction=kwargs.get("prediction"),
        audio=kwargs.get("audio"),
        presence_penalty=kwargs.get("presence_penalty"),
        frequency_penalty=kwargs.get("frequency_penalty"),
        logit_bias=kwargs.get("logit_bias"),
        user=kwargs.get("user"),
        reasoning_effort=kwargs.get("reasoning_effort"),
        response_format=kwargs.get("response_format"),
        seed=kwargs.get("seed"),
        tools=kwargs.get("tools"),
        tool_choice=kwargs.get("tool_choice"),
        logprobs=kwargs.get("logprobs"),
        top_logprobs=kwargs.get("top_logprobs"),
        parallel_tool_calls=kwargs.get("parallel_tool_calls"),
        deployment_id=kwargs.get("deployment_id"),
        extra_headers=kwargs.get("extra_headers"),
        functions=kwargs.get("functions"),
        function_call=kwargs.get("function_call"),
        base_url=kwargs.get("base_url"),
        api_version=kwargs.get("api_version"),
        api_key=kwargs.get("api_key"),
        model_list=kwargs.get("model_list"),
        thinking=kwargs.get("thinking"),
    )


def score(data: pd.DataFrame, model: SimpleNamespace, **kwargs: Any) -> pd.DataFrame:
    predictions = list()

    for _, row in data.iterrows():
        prediction = _get_genai_completion(
            model=model.model,
            clientId=model.client_id,
            base_url=model.base_url,
            api_key=model.api_key,
            messages=[{"role": "user", "content": row["promptText"]}],
        )
        predictions.append(prediction)

    return pd.DataFrame.from_dict({"resultText": predictions})


def chat(
    completion_create_params: CompletionCreateParams,
    model: SimpleNamespace,
    **kwargs: Any,
) -> Any:
    return _get_genai_completion(
        model=model.model,
        clientId=model.client_id,
        base_url=model.base_url,
        api_key=model.api_key,
        **completion_create_params,
    )
