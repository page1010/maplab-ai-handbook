from .adapters.gemini_adapter import GeminiAdapter
from .adapters.ollama_adapter import OllamaAdapter


def select_runtime(confidence: float, cross_file_reasoning: bool) -> str:
    if cross_file_reasoning or confidence < 0.78:
        return "gemini-2.5-flash-lite"
    return "ollama"


def get_adapter(name: str):
    if name.startswith("gemini"):
        return GeminiAdapter(model=name)
    return OllamaAdapter()

