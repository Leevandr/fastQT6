"""Field descriptions used by dynamic forms and Designer file generation."""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Iterable, Literal

FieldKind = Literal[
    "text",
    "password",
    "int",
    "float",
    "date",
    "combo",
    "multiline",
    "bool",
]


@dataclass(slots=True)
class Choice:
    label: str
    value: Any


@dataclass(slots=True)
class FieldSpec:
    name: str
    label: str | None = None
    kind: FieldKind = "text"
    required: bool = False
    default: Any = None
    choices: list[Choice] = dataclass_field(default_factory=list)
    min_value: float | int | None = None
    max_value: float | int | None = None
    decimals: int = 2
    placeholder: str = ""
    object_name: str | None = None

    @property
    def title(self) -> str:
        return self.label or self.name.replace("_", " ").title()

    @property
    def qt_object_name(self) -> str:
        if self.object_name:
            return self.object_name
        prefix = {
            "text": "lineEdit",
            "password": "lineEdit",
            "int": "spinBox",
            "float": "doubleSpinBox",
            "date": "dateEdit",
            "combo": "comboBox",
            "multiline": "textEdit",
            "bool": "checkBox",
        }[self.kind]
        return f"{prefix}_{self.name}"


def field(
    name: str,
    label: str | None = None,
    kind: FieldKind = "text",
    *,
    required: bool = False,
    default: Any = None,
    choices: Iterable[Choice | tuple[str, Any] | str] | None = None,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    decimals: int = 2,
    placeholder: str = "",
    object_name: str | None = None,
) -> FieldSpec:
    """Small shortcut for declaring fields in a readable way."""

    normalized_choices: list[Choice] = []
    for choice in choices or []:
        if isinstance(choice, Choice):
            normalized_choices.append(choice)
        elif isinstance(choice, tuple):
            normalized_choices.append(Choice(str(choice[0]), choice[1]))
        else:
            normalized_choices.append(Choice(str(choice), choice))

    return FieldSpec(
        name=name,
        label=label,
        kind=kind,
        required=required,
        default=default,
        choices=normalized_choices,
        min_value=min_value,
        max_value=max_value,
        decimals=decimals,
        placeholder=placeholder,
        object_name=object_name,
    )
