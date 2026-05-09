"""AirLLM provider (in-process, optionele dependency).

AirLLM kan grote modellen op consumer-hardware draaien door layer-by-layer
inference. Het is een Python library (pip install airllm). Omdat deze
afhankelijkheid optioneel is, importeren we hem lazy en vallen we elegant
terug op een lege string als hij niet beschikbaar is.
"""

from __future__ import annotations


class AirLLMProvider:
    name = "airllm"

    def __init__(
        self,
        model: str = "garage-bAInd/Platypus2-7B",
        temperature: float = 0.4,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self._loaded_model = None
        self._available: bool | None = None

    def _ensure_loaded(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            from airllm import AutoModel  # type: ignore[import-not-found]
        except Exception:
            self._available = False
            return False
        try:
            self._loaded_model = AutoModel.from_pretrained(self.model)
            self._available = True
        except Exception:
            self._loaded_model = None
            self._available = False
        return bool(self._available)

    def generate_text(
        self,
        *,
        system: str,
        user: str,
        section: str = "",
        method: str = "",
        length: str = "medium",
    ) -> str:
        if not self._ensure_loaded() or self._loaded_model is None:
            return ""
        prompt = f"{system}\n\n{user}\n"
        try:
            input_tokens = self._loaded_model.tokenizer(  # type: ignore[attr-defined]
                prompt,
                return_tensors="pt",
                truncation=True,
            )
            max_new_tokens = 512 if length == "short" else (1024 if length == "medium" else 2048)
            output = self._loaded_model.generate(  # type: ignore[attr-defined]
                input_tokens["input_ids"],
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=self.temperature,
            )
            decoded = self._loaded_model.tokenizer.decode(  # type: ignore[attr-defined]
                output[0],
                skip_special_tokens=True,
            )
            return decoded[len(prompt):].strip() if decoded.startswith(prompt) else decoded
        except Exception:
            return ""
