import os
from gpt4all import GPT4All

MODEL_PATH = os.getenv("GPT4ALL_MODEL", "orca-mini-3b-gguf2-q4_0.gguf")

_model = None


def _ensure_model():
    global _model
    if _model is None:
        _model = GPT4All(MODEL_PATH)


def chat(prompt: str, max_tokens: int = 512) -> str:
    """Send a prompt to the local GPT4All model and return response text."""
    _ensure_model()
    with _model.chat_session():
        resp = _model.generate(prompt, max_tokens=max_tokens)
    if isinstance(resp, bytes):
        try:
            resp = resp.decode("utf-8")
        except Exception:
            resp = str(resp)
    return resp.strip()
