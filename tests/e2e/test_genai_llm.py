# Copyright 2026 DataRobot, Inc.
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

import os

import pytest

if os.environ.get("RUN_E2E") != "1":
    pytest.skip("Set RUN_E2E=1 to enable LLM end-to-end tests.", allow_module_level=True)

SMOKE_PROMPT = "Reply with exactly one short word: ok"


@pytest.mark.e2e
def test_crewai_get_llm() -> None:
    from datarobot_genai.crewai.llm import get_llm

    # TODO (BUZZOK-31662): datarobot-genai _crewai_model_factory always sets stream_options
    # (include_usage=True) even when stream is off; Azure via LLM Gateway rejects that.
    # Drop this parameters= workaround once genai only sends stream_options with stream=True.
    response = get_llm(parameters={"stream": True}).call(SMOKE_PROMPT)
    assert isinstance(response, str) and response.strip()


@pytest.mark.e2e
def test_langgraph_get_llm() -> None:
    from langchain_core.messages import HumanMessage

    from datarobot_genai.langgraph.llm import get_llm

    message = get_llm(streaming=False).invoke([HumanMessage(content=SMOKE_PROMPT)])
    content = message.content
    if isinstance(content, list):
        text = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    else:
        text = content
    assert isinstance(text, str) and text.strip()


@pytest.mark.e2e
def test_llamaindex_get_llm() -> None:
    from datarobot_genai.llama_index.llm import get_llm

    response = get_llm().complete(SMOKE_PROMPT)
    text = getattr(response, "text", None) or str(response)
    assert isinstance(text, str) and text.strip()
