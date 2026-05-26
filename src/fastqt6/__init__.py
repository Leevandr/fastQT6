"""Fast helpers for PyQt6 training and small database applications."""

from .db import DBConfig, SQLDatabase
from .designer import DesignerForm, write_auth_ui, write_form_ui, write_main_window_ui
from .exam import copy_demo_exam_guide, scaffold_demo_exam_obuv
from .fields import Choice, FieldSpec, field
from .forms import DynamicForm, DynamicFormDialog

__version__ = "0.2.1"

__all__ = [
    "Choice",
    "DBConfig",
    "DesignerForm",
    "DynamicForm",
    "DynamicFormDialog",
    "FieldSpec",
    "SQLDatabase",
    "copy_demo_exam_guide",
    "field",
    "scaffold_demo_exam_obuv",
    "write_auth_ui",
    "write_form_ui",
    "write_main_window_ui",
]
