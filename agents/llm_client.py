import os
import json
from typing import Optional, Any, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class LLMClient:
    """
    Provider-agnostic LLM client using LiteLLM.
    Supports Gemini, OpenAI, Anthropic, Ollama, etc. configured via .env.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.getenv("LLM_MODEL", "gemini/gemini-2.0-flash")

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        response_json: bool = False,
    ) -> str:
        """
        Generate completion using the configured LLM.
        """
        import litellm

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_json:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = litellm.completion(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            # Check for common authentication or quota issues
            err_msg = str(e)
            if "AuthenticationError" in err_msg or "API key" in err_msg.lower():
                raise RuntimeError(
                    f"LLM API Authentication failed for model '{self.model}'.\n"
                    f"Please make sure your API key (e.g. GEMINI_API_KEY or OPENAI_API_KEY) is set in your .env file.\n"
                    f"Original error: {e}"
                ) from e
            raise
