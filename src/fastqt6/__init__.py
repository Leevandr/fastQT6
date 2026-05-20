"""Fast helpers for PyQt6 training and small database applications."""

from .db import DBConfig, SQLDatabase
from .designer import DesignerForm, write_auth_ui, write_form_ui, write_main_window_ui
from .fields import Choice, FieldSpec, field
from .forms import DynamicForm, DynamicFormDialog

__version__ = "0.1.0"

__all__ = [
    "Choice",
    "DBConfig",
    "DesignerForm",
    "DynamicForm",
    "DynamicFormDialog",
    "FieldSpec",
    "SQLDatabase",
    "field",
    "write_auth_ui",
    "write_form_ui",
    "write_main_window_ui",
]
