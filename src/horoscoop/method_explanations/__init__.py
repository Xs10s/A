"""Per-method personal explanation generators (headline + personal layer)."""

from __future__ import annotations

from .builder import build_method_explanations
from .types import METHOD_EXPLANATION_VERSION, ExplanationBlock, MethodExplanationBundle

__all__ = [
    "METHOD_EXPLANATION_VERSION",
    "ExplanationBlock",
    "MethodExplanationBundle",
    "build_method_explanations",
]
