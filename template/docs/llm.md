# LLM component

The LLM component provides the language model integration for your application. It supports multiple ways to connect an LLM, from zero-configuration gateway access to fully governed deployments with external provider credentials.

During project setup (`dr start` or `dr dotenv setup`), the CLI prompts you to choose one of five LLM integration options. Each option creates different DataRobot resources and requires different configuration.

| Option | Best for | Deploys resources? | Requires credentials? |
|---|---|---|---|
| [LLM Gateway](#llm-gateway) | Getting started quickly | No | No |
| [DataRobot Deployed LLM](#datarobot-deployed-llm) | Using an existing deployment | No (references existing) | No |
| [External LLM](#external-llm) | Bringing your own provider (Azure, Bedrock, etc.) | Yes | Yes |
| [LLM Blueprint with LLM Gateway](#llm-blueprint-with-llm-gateway) | Production use with full governance | Yes | No |
| [LLM from a Registered Model](#llm-from-a-registered-model) | Deploying a registered model (e.g. NVIDIA NIM) | Yes | No |

## LLM Gateway

The simplest option. Uses DataRobot's managed LLM Gateway directly with no custom model deployment. Good for prototyping and getting started.

### Resources created

This option deploys no DataRobot resources. The application calls the LLM Gateway API directly at runtime.

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `<LLM>_DEFAULT_MODEL` | Yes | `datarobot/azure/gpt-5-mini-2025-08-07` | Model ID from the LLM Gateway catalog. |

To list available models:

```python
import datarobot
dr_client = datarobot.Client()
response = dr_client.get("genai/llmgw/catalog/")
data = response.json()
for model in data["data"]:
    if model["isActive"]:
        print(model["model"])
```

### Runtime parameters exported

| Parameter | Value |
|---|---|
| `USE_DATAROBOT_LLM_GATEWAY` | `1`. |
| `<LLM>_DEFAULT_MODEL` | Selected model ID. |

## DataRobot Deployed LLM

Use this option when you already have a custom model deployed as an LLM in DataRobot and have the deployment ID. The component pulls the existing deployment into a playground and use case without creating new infrastructure.

### Resources created

| Resource | Type | Description |
|---|---|---|
| LLM Playground | `datarobot.Playground` | Playground linked to the use case. |

The component references the existing deployment and its prediction environment rather than creating new ones.

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `<LLM>_DEPLOYMENT_ID` | Yes | -- | Deployment ID of the existing LLM (e.g. `6510c7b7c4f3f9407e24a849`). |
| `<LLM>_DEFAULT_MODEL` | No | `datarobot/datarobot-deployed-llm` | Model identifier. |

**Note:** The deployment ID variable was formerly named `TEXTGEN_DEPLOYMENT_ID`. Use `<LLM>_DEPLOYMENT_ID` in current templates.

### Runtime parameters exported

| Parameter | Value |
|---|---|
| `<LLM>_DEPLOYMENT_ID` | The deployment ID. |
| `<LLM>_DEFAULT_MODEL` | Model identifier. |
| `<LLM>_DEFAULT_MODEL_FRIENDLY_NAME` | Deployment label. |
| `USE_DATAROBOT_LLM_GATEWAY` | `0`. |

### Stack outputs

Surfaced by `task infra:info` or `pulumi stack output`:

| Output | Description |
|---|---|
| `Deployment ID [LLM_APP_NAME]` | ID of the referenced deployment. |

## External LLM

Use your own LLM provider credentials (Azure OpenAI, AWS Bedrock, GCP VertexAI, Anthropic, Cohere, or TogetherAI) with full DataRobot governance, monitoring, and guard model support.

### Resources created

| Resource | Type | Description |
|---|---|---|
| LLM Playground | `datarobot.Playground` | Playground linked to the use case. |
| LLM Blueprint | `datarobot.LlmBlueprint` | Blueprint configured with the external LLM. |
| LLM Custom Model | `datarobot.CustomModel` | Text generation custom model sourced from the blueprint. |
| Prediction Environment | `datarobot.PredictionEnvironment` | Serverless prediction environment (or existing if `DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT` is set). |
| Registered Model | `datarobot.RegisteredModel` | Registered model version for deployment. |
| LLM Deployment | `datarobot.Deployment` | Serverless deployment with monitoring and data collection enabled. |

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `<LLM>_DEFAULT_MODEL` | No | `azure-openai-gpt-5-mini` | External LLM model name. |
| `<LLM>_DEFAULT_LLM_ID` | No | `azure-openai-gpt-5-mini` | LLM ID used in the Playground. |
| `<LLM>_DEFAULT_LLM_NAME` | No | `Azure OpenAI GPT-5 Mini` | Friendly name shown in the UI. |

You must also configure credentials for your chosen provider:

#### Azure OpenAI

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | API key. |
| `OPENAI_API_BASE` | Base URL (e.g. `https://ENDPOINT.openai.azure.com`). |
| `OPENAI_API_DEPLOYMENT_ID` | Deployment ID (e.g. `gpt-5-mini`). |
| `OPENAI_API_VERSION` | API version (e.g. `2024-08-01-preview`). |

#### AWS Bedrock

| Variable | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key ID. |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key. |
| `AWS_REGION_NAME` | AWS region (e.g. `us-east-1`). |

#### Google VertexAI

| Variable | Description |
|---|---|
| `VERTEXAI_APPLICATION_CREDENTIALS` | Path to credentials JSON file. |
| `VERTEXAI_SERVICE_ACCOUNT` | Google service account email. |
| `GOOGLE_REGION` | Optional. Region for Vertex AI calls; defaults to `us-west1`. |

#### Anthropic

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key. |

#### Cohere

| Variable | Description |
|---|---|
| `COHERE_API_KEY` | API key. |

#### TogetherAI

| Variable | Description |
|---|---|
| `TOGETHERAI_API_KEY` | API key. |

**Note:** The stock `blueprint_with_external_llm.py` template calls `verify_llm(f"azure/{os.getenv('OPENAI_API_DEPLOYMENT_ID')}")`, which is hardcoded to Azure OpenAI. For non-Azure providers, edit that line to the matching LiteLLM prefix&mdash;see the [LiteLLM providers reference](https://docs.litellm.ai/docs/providers).

### Runtime parameters exported

| Parameter | Value |
|---|---|
| `<LLM>_DEPLOYMENT_ID` | Deployment ID. |
| `<LLM>_DEFAULT_MODEL` | Model identifier. |
| `<LLM>_DEFAULT_MODEL_FRIENDLY_NAME` | Friendly name. |

### Stack outputs

Surfaced by `task infra:info` or `pulumi stack output`:

| Output | Description |
|---|---|
| `Deployment ID [LLM_APP_NAME]` | ID of the deployed LLM. |
| `Deployment Console [LLM_APP_NAME]` | URL to the Deployment Console page. |
| `RAG Playground URL [LLM_APP_NAME]` | URL to the Playground comparison chat. |

## LLM Blueprint with LLM Gateway

The most production-ready option. Combines a full LLM Blueprint deployment with the DataRobot LLM Gateway, giving you governance, monitoring, guard models, and the ability to swap models through the gateway catalog without redeploying.

### Resources created

| Resource | Type | Description |
|---|---|---|
| LLM Playground | `datarobot.Playground` | Playground linked to the use case. |
| LLM Blueprint | `datarobot.LlmBlueprint` | Blueprint configured with the LLM Gateway model. |
| LLM Custom Model | `datarobot.CustomModel` | Text generation custom model sourced from the blueprint. |
| Prediction Environment | `datarobot.PredictionEnvironment` | Serverless prediction environment (or existing if `DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT` is set). |
| Registered Model | `datarobot.RegisteredModel` | Registered model version for deployment. |
| LLM Deployment | `datarobot.Deployment` | Serverless deployment with monitoring and data collection enabled. |

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `<LLM>_DEFAULT_MODEL` | Yes | `datarobot/azure/gpt-5-mini-2025-08-07` | Model ID from the LLM Gateway catalog. |
| `<LLM>_DEFAULT_LLM_ID` | No | `azure-openai-gpt-5-mini` | LLM ID used in the Playground. |

### Runtime parameters exported

| Parameter | Value |
|---|---|
| `<LLM>_DEPLOYMENT_ID` | Deployment ID. |
| `USE_DATAROBOT_LLM_GATEWAY` | `1`. |
| `<LLM>_DEFAULT_MODEL` | Selected model ID. |

### Stack outputs

Surfaced by `task infra:info` or `pulumi stack output`:

| Output | Description |
|---|---|
| `Deployment ID [LLM_APP_NAME]` | ID of the deployed LLM. |
| `Deployment Console [LLM_APP_NAME]` | URL to the Deployment Console page. |
| `RAG Playground URL [LLM_APP_NAME]` | URL to the Playground comparison chat. |

## LLM from a Registered Model

Use this option when you have an existing registered model (not yet deployed) that you want to wrap in an LLM Blueprint and deploy. This is the path for NVIDIA NIM models: pick a model from the NVIDIA gallery, specify the registered model ID, and this option deploys it, creates an LLM Blueprint and RAG Playground around it, then connects it to the application.

This option creates two deployments:

1. **Proxy deployment**&mdash;deploys the registered model so it can be validated.
2. **Blueprint deployment**&mdash;creates an LLM Blueprint from the validated model, builds a new custom model from that blueprint, and deploys it with full monitoring.

### Resources created

| Resource | Type | Description |
|---|---|---|
| LLM Playground | `datarobot.Playground` | Playground linked to the use case. |
| Proxy Deployment | `datarobot.Deployment` | Initial deployment of the registered model for validation. |
| LLM Validation | `datarobot.CustomModelLlmValidation` | Validates the deployed model can serve as an LLM. |
| LLM Blueprint | `datarobot.LlmBlueprint` | Blueprint created from the validated custom model LLM. |
| LLM Custom Model | `datarobot.CustomModel` | Text generation custom model sourced from the blueprint. |
| Prediction Environment | `datarobot.PredictionEnvironment` | Serverless prediction environment (or existing if `DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT` is set). |
| Registered Model | `datarobot.RegisteredModel` | New registered model from the blueprint custom model. |
| LLM Deployment | `datarobot.Deployment` | Final deployment with monitoring and data collection enabled. |

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TEXTGEN_REGISTERED_MODEL_ID` | Yes | -- | ID of the registered model. |
| `<LLM>_DEFAULT_MODEL` | No | `datarobot/datarobot-deployed-llm` | Model identifier. |
| `DATAROBOT_TIMEOUT_MINUTES` | No | `30` | Timeout in minutes for DataRobot operations. |

### Runtime parameters exported

| Parameter | Value |
|---|---|
| `<LLM>_DEPLOYMENT_ID` | Deployment ID. |
| `<LLM>_DEFAULT_MODEL` | Model identifier. |
| `<LLM>_DEFAULT_MODEL_FRIENDLY_NAME` | Registered model name. |

### Stack outputs

Surfaced by `task infra:info` or `pulumi stack output`:

| Output | Description |
|---|---|
| `Deployment ID [LLM_APP_NAME]` | ID of the proxy deployment created from the registered model. |

## Switching between options

### During project setup

Run `dr start` or `dr dotenv setup` and select the desired option from the interactive prompt.

### Using the symlink

```sh
ln -sf ../configurations/CONFIG_FILE infra/infra/llm.py
```

Available configuration files:

| File | Option |
|---|---|
| `gateway_direct.py` | LLM Gateway |
| `deployed_llm.py` | DataRobot Deployed LLM |
| `blueprint_with_external_llm.py` | External LLM |
| `blueprint_with_llm_gateway.py` | LLM Blueprint with LLM Gateway |
| `registered_model.py` | LLM from a Registered Model |

### Using the environment variable

Set `INFRA_ENABLE_LLM` in your `.env` file:

```sh
INFRA_ENABLE_LLM=gateway_direct.py
```

## Common configuration

All options that deploy resources share these behaviors:

- **Prediction environment**&mdash;if `DATAROBOT_DEFAULT_PREDICTION_ENVIRONMENT` is set, the component uses that existing environment; otherwise, it creates a new serverless environment.
- **Scaling**&mdash;deployments default to `min_computes=0` and `max_computes=2`.
- **Data collection**&mdash;all deployments enable prediction data collection.
- **Association IDs**&mdash;deployments use `association_id` for tracking predictions.

### Required feature flags

All options require these DataRobot feature flags to be enabled:

- `ENABLE_MLOPS`
- `ENABLE_CUSTOM_INFERENCE_MODEL`
- `ENABLE_PUBLIC_NETWORK_ACCESS_FOR_ALL_CUSTOM_MODELS`
- `ENABLE_MLOPS_TEXT_GENERATION_TARGET_TYPE`

LLM Gateway (direct) additionally requires:

- `ENABLE_MLOPS_RESOURCE_REQUEST_BUNDLES`

## Variable naming

In the tables above, `<LLM>` is a placeholder for your LLM app name in uppercase (e.g. if your app name is `llm`, variables are prefixed with `LLM_`). This is set by the `llm_app_name` template variable during project setup.

`USE_DATAROBOT_LLM_GATEWAY` tells downstream consumers (e.g. the agent) whether to route LLM calls through the DataRobot LLM Gateway. It's exported as `1` by the gateway-based options (LLM Gateway, LLM Blueprint with LLM Gateway) and as `0` by DataRobot Deployed LLM. External LLM and LLM from a Registered Model don't export it; consumers fall back to their own default.

## Further reading

- [Playground overview](https://docs.datarobot.com/en/docs/gen-ai/playground-tools/playground-overview.html)&mdash;what a Playground is and how LLM blueprints fit in.
- [Build LLM blueprints](https://docs.datarobot.com/en/docs/gen-ai/playground-tools/build-llm-blueprints.html)&mdash;LLM blueprint settings (base LLM, prompting, vector database).
- [Deploy an LLM](https://docs.datarobot.com/en/docs/gen-ai/playground-tools/deploy-llm.html)&mdash;deploying an LLM blueprint for production use.
- [LLM gateway model configuration](https://docs.datarobot.com/en/docs/reference/gen-ai-ref/llm-gateway-config.html)&mdash;admin guide to provisioning provider credentials for the LLM gateway.
- [LiteLLM providers](https://docs.litellm.ai/docs/providers)&mdash;reference for the model-string prefixes used by the `verify_llm` check.
