"""Dynamic PyQt6 forms based on FieldSpec objects."""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable, Mapping

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .fields import FieldSpec


class DynamicForm(QWidget):
    """Build and read a form dynamically from field specs."""

    def __init__(self, fields: Iterable[FieldSpec], data: Mapping[str, Any] | None = None):
        super().__init__()
        self.fields = list(fields)
        self.widgets: dict[str, QWidget] = {}
        self.layout = QFormLayout(self)

        for spec in self.fields:
            widget = self._make_widget(spec)
            widget.setObjectName(spec.qt_object_name)
            self.widgets[spec.name] = widget
            self.layout.addRow(spec.title, widget)

        self.set_data(data or {spec.name: spec.default for spec in self.fields})

    def get_data(self) -> dict[str, Any]:
        return {spec.name: self.value(spec.name) for spec in self.fields}

    def set_data(self, data: Mapping[str, Any]) -> None:
        for spec in self.fields:
            self.set_value(spec.name, data.get(spec.name, spec.default))

    def value(self, name: str) -> Any:
        widget = self.widgets[name]
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        if isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        if isinstance(widget, QSpinBox):
            return widget.value()
        if isinstance(widget, QDoubleSpinBox):
            return widget.value()
        if isinstance(widget, QDateEdit):
            return widget.date().toString("yyyy-MM-dd")
        if isinstance(widget, QComboBox):
            return widget.currentData()
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        return None

    def set_value(self, name: str, value: Any) -> None:
        widget = self.widgets[name]
        if isinstance(widget, QLineEdit):
            widget.setText("" if value is None else str(value))
        elif isinstance(widget, QTextEdit):
            widget.setPlainText("" if value is None else str(value))
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value or 0))
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value or 0))
        elif isinstance(widget, QDateEdit):
            widget.setDate(_to_qdate(value))
        elif isinstance(widget, QComboBox):
            index = widget.findData(value)
            if index >= 0:
                widget.setCurrentIndex(index)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))

    def validate(self) -> tuple[bool, str]:
        for spec in self.fields:
            if not spec.required:
                continue
            value = self.value(spec.name)
            if value in (None, ""):
                return False, f"Заполните поле: {spec.title}"
        return True, ""

    def _make_widget(self, spec: FieldSpec) -> QWidget:
        if spec.kind == "password":
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            widget.setPlaceholderText(spec.placeholder)
            return widget
        if spec.kind == "text":
            widget = QLineEdit()
            widget.setPlaceholderText(spec.placeholder)
            return widget
        if spec.kind == "multiline":
            widget = QTextEdit()
            widget.setPlaceholderText(spec.placeholder)
            return widget
        if spec.kind == "int":
            widget = QSpinBox()
            widget.setMinimum(int(spec.min_value if spec.min_value is not None else -2147483648))
            widget.setMaximum(int(spec.max_value if spec.max_value is not None else 2147483647))
            return widget
        if spec.kind == "float":
            widget = QDoubleSpinBox()
            widget.setDecimals(spec.decimals)
            widget.setMinimum(float(spec.min_value if spec.min_value is not None else -999999999))
            widget.setMaximum(float(spec.max_value if spec.max_value is not None else 999999999))
            return widget
        if spec.kind == "date":
            widget = QDateEdit()
            widget.setDisplayFormat("yyyy-MM-dd")
            widget.setCalendarPopup(True)
            return widget
        if spec.kind == "combo":
            widget = QComboBox()
            for choice in spec.choices:
                widget.addItem(choice.label, choice.value)
            return widget
        if spec.kind == "bool":
            return QCheckBox()
        return QLabel(f"Unsupported field: {spec.kind}")


class DynamicFormDialog(QDialog):
    """Dialog wrapper around DynamicForm."""

    def __init__(
        self,
        fields: Iterable[FieldSpec],
        data: Mapping[str, Any] | None = None,
        *,
        title: str = "Форма",
        save_text: str = "Сохранить",
        cancel_text: str = "Отмена",
    ):
        super().__init__()
        self.setWindowTitle(title)
        self.form = DynamicForm(fields, data)

        layout = QVBoxLayout(self)
        layout.addWidget(self.form)

        buttons = QHBoxLayout()
        self.button_save = QPushButton(save_text)
        self.button_cancel = QPushButton(cancel_text)
        buttons.addStretch(1)
        buttons.addWidget(self.button_save)
        buttons.addWidget(self.button_cancel)
        layout.addLayout(buttons)

        self.button_save.clicked.connect(self._save)
        self.button_cancel.clicked.connect(self.reject)

    def get_data(self) -> dict[str, Any]:
        return self.form.get_data()

    def _save(self) -> None:
        valid, message = self.form.validate()
        if not valid:
            QMessageBox.warning(self, "Ошибка", message)
            return
        self.accept()


def _to_qdate(value: Any) -> QDate:
    if isinstance(value, QDate):
        return value
    if isinstance(value, date):
        return QDate(value.year, value.month, value.day)
    parsed = QDate.fromString(str(value or ""), "yyyy-MM-dd")
    return parsed if parsed.isValid() else QDate.currentDate()
