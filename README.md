<p align="center">
  <a href="https://github.com/datarobot-community/af-component-llm">
    <img src="https://af.datarobot.com/img/datarobot_logo.avif" width="600px" alt="DataRobot Logo"/>
  </a>
</p>
<p align="center">
    <span style="font-size: 1.5em; font-weight: bold; display: block;">af-component-llm</span>
</p>

<p align="center">
  <a href="https://datarobot.com">Homepage</a>
  ·
  <a href="https://af.datarobot.com">Documentation</a>
  ·
  <a href="https://docs.datarobot.com/en/docs/get-started/troubleshooting/general-help.html">Support</a>
</p>

<p align="center">
  <a href="https://github.com/datarobot-community/af-component-llm/tags">
    <img src="https://img.shields.io/github/v/tag/datarobot-community/af-component-llm?label=version" alt="Latest Release">
  </a>
  <a href="/LICENSE">
    <img src="https://img.shields.io/github/license/datarobot-community/af-component-llm" alt="License">
  </a>
  <a href="https://join.slack.com/t/datarobot-community/shared_invite/zt-3uzfp8k50-SUdMqeux25ok9_5wr4okrg">
    <img src="https://img.shields.io/badge/%23applications-a?label=Slack&labelColor=30373D&color=81FBA6" alt="Slack #applications">
  </a>
</p>

The LLM inference component. Deploys and/or configures LLM models or uses the DataRobot LLM Gateway for other components to leverage

The `af-component-llm` component adds LLM inference capabilities to any [DataRobot App Framework](https://af.datarobot.com) project. It is intended for application developers building AI-powered apps on DataRobot who need a flexible, governed path to LLM access — whether through the DataRobot LLM Gateway, an already-deployed custom model, or an external provider such as Azure OpenAI, AWS Bedrock, or Google Vertex AI.

The component ships a Pulumi-based infrastructure module and a DataRobot CLI configuration file. When applied with `dr component add` (or `uvx copier copy`), it generates a Python infrastructure module, a CLI metadata file, and a stored answers file scoped to your chosen LLM configuration strategy. Because the component is repeatable, you can apply it multiple times to the same project to configure separate LLM instances under different names.


# Table of contents

- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Component dependencies](#component-dependencies)
- [Configuration strategies](#configuration-strategies)
- [Local development](#local-development)
- [End-to-end tests](#end-to-end-tests)
- [Updating](#updating)
- [Troubleshooting](#troubleshooting)
- [Next steps and cross-links](#next-steps-and-cross-links)
- [Contributing, changelog, support, and legal](#contributing-changelog-support-and-legal)


# Prerequisites

Before applying this component, make sure you have the following tools and access in place.

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) installed
- [`dr`](https://cli.datarobot.com) installed
- The [`af-component-base`](https://github.com/datarobot-community/af-component-base) component already applied to your project.
- A DataRobot account with access to the LLM Gateway or the ability to deploy custom models (depending on the configuration strategy you choose).
- For external LLM providers (Azure, Bedrock, Vertex AI, Anthropic, Cohere, TogetherAI): valid credentials for the chosen provider.


# Quick start

Run the following command in your project directory:

```bash
dr component add https://github.com/datarobot-community/af-component-llm .
```

If you need additional control, you can run this to use copier directly:

```bash
uvx copier copy datarobot-community/af-component-llm .
```

The interactive prompt asks for:

- A Python-friendly name for this LLM instance (for example, `llm` generates `liballm.py`).
- The path to your base component answers file.
- The LLM configuration strategy (see [Configuration strategies](#configuration-strategies)).
- Provider-specific credentials or identifiers depending on the strategy chosen.


# Component dependencies

This component has one required dependency that must be applied to your project before adding the LLM component.

## Required

The following components must be applied to the project **before** this component:

| Name | Repository | Repeatable |
|------|-----------|------------|
| `base` | [https://github.com/datarobot-community/af-component-base](https://github.com/datarobot-community/af-component-base) | No |


# Configuration strategies

During setup, the interactive prompt asks you to choose one of five LLM configuration strategies. Each generates a different Pulumi infrastructure module tailored to the selected approach.

| Strategy | Description |
|----------|-------------|
| `gateway_direct` | Simplest option. Uses the DataRobot LLM Gateway directly with a model you specify by ID. |
| `deployed_llm` | Points to an existing DataRobot custom model deployment. Requires a deployment ID. |
| `blueprint_with_external_llm` | Creates an LLM Blueprint backed by an external provider (Azure, Bedrock, Vertex AI, Anthropic, Cohere, or TogetherAI). |
| `blueprint_with_llm_gateway` | Full governance path: combines the LLM Gateway with an external model and registers it as a DataRobot deployment. |
| `registered_model` | Uses an existing registered model with an LLM Blueprint. |
| `nim_deployed_llm` | Points to an existing NVIDIA NIM deployment (manual provisioning; optional in maintainer E2E). |

Each strategy exports a Pulumi stack output with the deployment ID and model identifier your application can consume at runtime.


# Local development

The following tasks are available for working on the component itself. Run them from the repository root after cloning.

Install development dependencies (renders the Copier template into `.rendered/` and syncs the project):

```bash
task install-dev
```

Check linting and type errors:

```bash
task lint-check
```

Apply Apache 2.0 license headers to all source files:

```bash
task copyright
```

Verify license headers are present:

```bash
task copyright-check
```

Validate that template filenames contain no Windows-illegal characters:

```bash
task validate-windows-compatibility
```

The rendered template lands in `.rendered/infra/`. You can inspect or run the generated Pulumi code there before contributing changes upstream. The `render-template` task (called automatically by `install-dev`) drives this using Copier defaults.


# End-to-end tests

Maintainer E2E tests live in this repository (not in the Copier template). They render each LLM configuration, run `pulumi up` where needed, and smoke-test [`datarobot-genai`](https://github.com/datarobot-oss/datarobot-genai) `get_llm()` for CrewAI, LangGraph, and LlamaIndex.

**Prerequisites**

- [`task`](https://taskfile.dev) and [`uv`](https://docs.astral.sh/uv/)
- [Pulumi CLI](https://www.pulumi.com/docs/install/)
- DataRobot credentials and configuration-specific secrets (see [`.env.sample`](.env.sample))

**Run locally**

```bash
cp .env.sample .env   # fill in values
uv sync --extra e2e
task test-e2e:gateway-direct
```

List all tasks with `task --list` (prefix `test-e2e:`). Each task applies the correct environment masks for its configuration before deploy and pytest.

| Task | Configuration |
|------|----------------|
| `test-e2e:gateway-direct` | `gateway_direct` |
| `test-e2e:blueprint-with-llm-gateway` | `blueprint_with_llm_gateway` |
| `test-e2e:deployed-llm` | `deployed_llm` |
| `test-e2e:blueprint-with-external-llm` | `blueprint_with_external_llm` |
| `test-e2e:registered-model` | `registered_model` |

**NIM (manual only)** — requires a running NIM deployment; not run in CI:

```bash
RUN_NIM_E2E=1 task test-e2e:nim-deployed-llm
```

**CI** — [`.github/workflows/afcomponentllm-e2e-test.yaml`](.github/workflows/afcomponentllm-e2e-test.yaml) runs the five standard configurations on push/PR to `main` using repository/organization CI secrets. Pulumi stacks are named `pr-e2e-test-llm-{config}-run-{id}` (PRs) or `e2e-test-llm-{config}-run-{id}` (main) for alignment with recipe cleanup cron.


# Updating

All components should be regularly updated to pick up bug fixes, new features, and compatibility with the latest DataRobot App Framework.

For automatic updates to the latest version, run the following command in your project directory:

```bash
dr component update .datarobot/answers/llm-LLM_NAME.yml
```

If you need more fine-grained control and prefer using copier directly, run this to have more control over the process:

```bash
uvx copier update -a .datarobot/answers/llm-LLM_NAME.yml -A
```


# Troubleshooting

The following are common issues you may encounter when setting up or using this component, along with their solutions.

**`ScannerError` when running the generator tool**
A YAML syntax error in `copier-module.yaml` (for example, a double closing quote on `short_description`) prevents the generator from running. Open the file and verify all quoted strings are properly terminated.

**"Model not found in LLM Gateway catalog"**
Check that `LLM_NAME_DEFAULT_MODEL` is set to a valid model ID (for example `datarobot/azure/gpt-5-mini-2025-08-07`) and that the model is active. Call `verify_llm_gateway_model_availability()` from `datarobot_pulumi_utils.common.llm_validation` to list available models.

**"Feature flags required but not enabled"**
Some configuration strategies require DataRobot platform feature flags (`MLOPS`, `TEXT_GENERATION`, and others). Contact DataRobot support to have the required flags enabled on your account.

**"Credential validation failed" for external providers**
Verify that the environment variables for your chosen provider are set correctly. The required variables differ per provider. The `ProviderCredential` class in `datarobot_pulumi_utils.pulumi.llm_credentials` lists the exact variable names.

**Windows file path issues during template rendering**
Run `task validate-windows-compatibility` to scan for template file names containing characters illegal on Windows (`< > : " | ? *`). The Jinja variable substitution in file names is designed to avoid these, but verify after adding new template files.

**Copier update conflicts**
If `uvx copier update` reports conflicts, review the diff carefully. Copier stores the original answers in `.datarobot/answers/llm-LLM_NAME.yml`; you can re-run the update with `-A` to skip all conflict prompts and accept the latest template version.

If you encounter issues not listed here, [open a GitHub issue](https://github.com/datarobot-community/af-component-llm/issues) or [contact DataRobot support](https://docs.datarobot.com/en/docs/get-started/troubleshooting/general-help.html).


# Next steps and cross-links

After applying the component, use these resources to configure LLM access and continue building your application.

- [App Framework documentation](https://af.datarobot.com)&mdash;full reference for building and deploying App Framework projects.
- [af-component-base](https://github.com/datarobot-community/af-component-base)&mdash;required prerequisite component.
- [DataRobot CLI reference](https://cli.datarobot.com)&mdash;`dr component add`, `dr deploy`, and other commands.
- [DataRobot LLM Gateway docs](https://docs.datarobot.com/en/docs/agentic-ai/agentic-develop/index.html)&mdash;model catalog, governance, and monitoring.
- [LiteLLM documentation](https://docs.litellm.ai)&mdash;the multi-provider LLM library used by the generated infrastructure module.
- [Pulumi DataRobot provider](https://www.pulumi.com/registry/packages/datarobot/)&mdash;Pulumi resource reference for DataRobot.


# Contributing, changelog, support, and legal

This section covers how to contribute, where to find changelogs, and how to get help or report security issues.

**Contributing**&mdash;bug reports and pull requests are welcome. Open an issue first to discuss significant changes. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide and the [Code of Conduct](CODE_OF_CONDUCT.md).

**Changelog and versioning**&mdash;releases are tagged on the [GitHub repository](https://github.com/datarobot-community/af-component-llm/tags). The project follows semantic versioning; breaking changes are noted in release notes.

**Getting help**&mdash;open an issue on [GitHub](https://github.com/datarobot-community/af-component-llm/issues) or [contact DataRobot support](https://docs.datarobot.com/en/docs/get-started/troubleshooting/general-help.html).

**Security**&mdash;review [SECURITY.md](.github/SECURITY.md) for the security policy and responsible disclosure process.

**License**&mdash;Apache 2.0. See [LICENSE](/LICENSE).

---
