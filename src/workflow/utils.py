from typing import Optional

from ..language_models import get_openai_token_provider, cloudgpt_available_models

def load_llm_cofig(model: cloudgpt_available_models, cache_seed: Optional[int] = None):
    """
    Load the language model configuration.

    Args:
        model (cloudgpt_available_models): available models from cloudgpt.
        cache_seed (Optional[int], optional): cache seed. Defaults to None.

    Returns:
        dict: language model configuration.
    """
    llm_config = {
        "model": model,
        "api_type": "azure",
        "cache_seed": cache_seed,
        "api_key": get_openai_token_provider()(),
        "base_url": "https://cloudgpt-openai.azure-api.net/",
        "api_version": "2024-06-01"
    }

    return llm_config

TERMINATE = lambda x: x.get("content", "").find("TERMINATE") != -1