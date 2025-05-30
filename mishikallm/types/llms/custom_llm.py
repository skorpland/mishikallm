from typing import List

from typing_extensions import Dict, Required, TypedDict, override

from mishikallm.llms.custom_llm import CustomLLM


class CustomLLMItem(TypedDict):
    provider: str
    custom_handler: CustomLLM
