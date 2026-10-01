"""Model client factory: pick the provider with MODEL_PROVIDER in .env."""

import warnings

from autogen_core.models import ChatCompletionClient, ModelInfo

from config.settings import get_setting, require_setting

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Capabilities for non-OpenAI models (Ollama, OpenRouter), which AutoGen can't look up itself.
OPEN_MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=True,
    json_output=True,
    structured_output=True,
    family="unknown",
)


def get_model_client() -> ChatCompletionClient:
    """Return a chat completion client for the provider set in MODEL_PROVIDER."""
    provider = get_setting("MODEL_PROVIDER", "ollama").lower()

    if provider == "ollama":
        from autogen_ext.models.ollama import OllamaChatCompletionClient

        return OllamaChatCompletionClient(
            model=require_setting("OLLAMA_MODEL"),
            host=get_setting("OLLAMA_HOST", "http://localhost:11434"),
            model_info=OPEN_MODEL_INFO,
        )

    if provider == "openai":
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        return OpenAIChatCompletionClient(
            model=require_setting("OPENAI_MODEL"),
            api_key=require_setting("OPENAI_API_KEY"),
        )

    if provider == "openrouter":
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        model = require_setting("OPENROUTER_MODEL")
        fallback = get_setting("OPENROUTER_FALLBACK_MODEL")
        extra_args = {}
        if fallback:
            # OpenRouter tries these in order, so an overloaded free model doesn't fail the turn.
            extra_args["extra_body"] = {"models": [model, fallback]}
            # AutoGen warns whenever the answering model differs from the requested one.
            warnings.filterwarnings("ignore", message="Resolved model mismatch")

        return OpenAIChatCompletionClient(
            model=model,
            api_key=require_setting("OPENROUTER_API_KEY"),
            base_url=OPENROUTER_BASE_URL,
            model_info=OPEN_MODEL_INFO,
            **extra_args,
        )

    if provider == "azure":
        from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

        deployment = require_setting("AZURE_OPENAI_DEPLOYMENT")
        return AzureOpenAIChatCompletionClient(
            azure_deployment=deployment,
            model=get_setting("AZURE_OPENAI_MODEL") or deployment,
            api_version=require_setting("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=require_setting("AZURE_OPENAI_ENDPOINT"),
            api_key=require_setting("AZURE_OPENAI_API_KEY"),
        )

    raise ValueError(
        f"Unknown MODEL_PROVIDER '{provider}'. Use one of: ollama, openai, openrouter, azure."
    )
