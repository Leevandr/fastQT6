"""Ready-to-use generic PyQt6 windows."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .db import SQLDatabase
from .fields import FieldSpec
from .forms import DynamicFormDialog


class LoginWindow(QWidget):
    """Simple configurable login window."""

    def __init__(
        self,
        db: SQLDatabase,
        *,
        users_table: str = "users",
        on_success: Callable[[dict[str, Any]], None] | None = None,
    ):
        super().__init__()
        self.db = db
        self.users_table = users_table
        self.on_success = on_success

        self.setWindowTitle("Вход")
        layout = QVBoxLayout(self)
        self.lineEdit_login = QLineEdit()
        self.lineEdit_login.setObjectName("lineEdit_login")
        self.lineEdit_pass = QLineEdit()
        self.lineEdit_pass.setObjectName("lineEdit_pass")
        self.lineEdit_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.pushButton_login = QPushButton("Войти")
        self.pushButton_login.setObjectName("pushButton_login")
        layout.addWidget(QLabel("Логин"))
        layout.addWidget(self.lineEdit_login)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.lineEdit_pass)
        layout.addWidget(self.pushButton_login)
        self.pushButton_login.clicked.connect(self.login)

    def login(self) -> None:
        username = self.lineEdit_login.text().strip()
        password = self.lineEdit_pass.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        user = self.db.login(self.users_table, username, password)
        if not user:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        if self.on_success:
            self.on_success(user)


class CrudWindow(QWidget):
    """A compact CRUD table for one database table."""

    def __init__(
        self,
        db: SQLDatabase,
        *,
        table: str,
        fields: Iterable[FieldSpec],
        columns: Mapping[str, str] | None = None,
        order_by: str = "id",
        title: str | None = None,
    ):
        super().__init__()
        self.db = db
        self.table = table
        self.fields = list(fields)
        self.columns = dict(columns or {"id": "ID", **{spec.name: spec.title for spec in self.fields}})
        self.order_by = order_by
        self.rows: list[dict[str, Any]] = []

        self.setWindowTitle(title or table)
        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        self.button_add = QPushButton("Добавить")
        self.button_edit = QPushButton("Редактировать")
        self.button_delete = QPushButton("Удалить")
        self.button_reload = QPushButton("Обновить")
        for button in (self.button_add, self.button_edit, self.button_delete, self.button_reload):
            actions.addWidget(button)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.columns))
        self.table_widget.setHorizontalHeaderLabels(list(self.columns.values()))
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table_widget, 1)

        self.button_add.clicked.connect(self.add_row)
        self.button_edit.clicked.connect(self.edit_row)
        self.button_delete.clicked.connect(self.delete_row)
        self.button_reload.clicked.connect(self.reload)
        self.reload()

    def reload(self) -> None:
        self.rows = self.db.select(self.table, order_by=self.order_by)
        self.table_widget.setRowCount(len(self.rows))
        for row_index, row in enumerate(self.rows):
            for col_index, key in enumerate(self.columns):
                item = QTableWidgetItem("" if row.get(key) is None else str(row.get(key)))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row_index, col_index, item)
        self.table_widget.resizeColumnsToContents()

    def selected_row(self) -> dict[str, Any] | None:
        index = self.table_widget.currentRow()
        if index < 0 or index >= len(self.rows):
            return None
        return self.rows[index]

    def add_row(self) -> None:
        dialog = DynamicFormDialog(self.fields, title="Добавить")
        if dialog.exec():
            self.db.insert(self.table, dialog.get_data())
            self.reload()

    def edit_row(self) -> None:
        row = self.selected_row()
        if not row:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return
        dialog = DynamicFormDialog(self.fields, row, title="Редактировать")
        if dialog.exec():
            self.db.update(self.table, dialog.get_data(), "id=?", (row["id"],))
            self.reload()

    def delete_row(self) -> None:
        row = self.selected_row()
        if not row:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return
        answer = QMessageBox.question(self, "Подтверждение", "Удалить выбранную запись?")
        if answer == QMessageBox.StandardButton.Yes:
            self.db.delete(self.table, "id=?", (row["id"],))
            self.reload()
