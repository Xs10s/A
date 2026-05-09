from __future__ import annotations

from typing import Literal, TypedDict


MethodId = Literal[
    "western",
    "vedic",
    "bazi",
    "human-design",
    "maya",
    "energy-profile",
]

InputRequirement = Literal[
    "birthDate",
    "birthTime",
    "birthPlace",
    "timezone",
    "coordinates",
    "calculatedWesternChart",
    "calculatedVedicChart",
    "calculatedBaziChart",
    "calculatedHumanDesignChart",
    "calculatedMayaChart",
]

CalculationStatus = Literal[
    "ready",
    "missing-input",
    "calculation-failed",
    "unsupported",
    "planned",
    "not-applicable",
    "invalid-data",
]

CalculationComplexity = Literal["basic", "intermediate", "advanced"]

CalculationImplementationStatus = Literal[
    "implemented",
    "planned",
    "unsupported",
    "not-needed",
    "derived",
]


class CalculationFallback(TypedDict, total=False):
    missingInput: str
    calculationFailed: str
    unsupported: str
    planned: str
    invalidData: str
    notApplicable: str


class CalculationDefinition(TypedDict, total=False):
    id: str
    method: MethodId
    title: str
    description: str
    requiredInputs: list[InputRequirement]
    optionalInputs: list[InputRequirement]
    outputKeys: list[str]
    fillsResultFields: list[str]
    dependsOnCalculations: list[str]
    relatedStaticConcepts: list[str]
    templateIds: list[str]
    complexity: CalculationComplexity
    implementationStatus: CalculationImplementationStatus
    requiresExactBirthTime: bool
    requiresBirthPlace: bool
    derivedFrom: list[str]
    fallback: CalculationFallback


class CalculationResult(TypedDict, total=False):
    calculationId: str
    method: MethodId
    status: CalculationStatus
    data: object
    outputKeys: dict[str, object]
    missingInputs: list[InputRequirement]
    errorMessage: str
    userMessage: str


class CalculableValueDefinition(TypedDict, total=False):
    id: str
    method: MethodId
    category: str
    label: str
    description: str
    calculationId: str
    outputKey: str
    requiredInputs: list[InputRequirement]
    status: CalculationImplementationStatus
    derivedFrom: list[str]
    usedInResultFields: list[str]
    usedInEnergyProfile: bool
    fallbackMessage: str

