"""Shared types for per-method personal explanation generators."""

from __future__ import annotations

from typing import TypedDict


METHOD_EXPLANATION_VERSION = "1.0.0"


class ExplanationBlock(TypedDict, total=False):
    """One readable unit: what the chart says + what it tends to mean for a person."""

    id: str
    title: str
    headline: str
    personal_layer: str
    reflection_questions: list[str]


class MethodExplanationBundle(TypedDict, total=False):
    """Full narrative payload for one method tab / PDF section."""

    method_id: str
    locale: str
    version: str
    overview: str
    blocks: list[ExplanationBlock]
    closing_note: str
