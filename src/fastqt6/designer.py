"""Generate Qt Designer .ui files from Python field descriptions."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from xml.dom import minidom
from xml.etree import ElementTree as ET

from .fields import FieldSpec


class DesignerForm:
    """A small builder for QWidget .ui files."""

    def __init__(self, class_name: str = "Form", width: int = 520, height: int = 420):
        self.class_name = class_name
        self.width = width
        self.height = height
        self.root = _base_ui(class_name, width, height)
        self.main_layout = ET.SubElement(self.root.find("./widget"), "layout", {"class": "QVBoxLayout", "name": "verticalLayout"})

    def add_title(self, text: str, object_name: str = "label_title") -> "DesignerForm":
        item = ET.SubElement(self.main_layout, "item")
        widget = ET.SubElement(item, "widget", {"class": "QLabel", "name": object_name})
        _property(widget, "text", text)
        return self

    def add_form(self, fields: Iterable[FieldSpec], layout_name: str = "formLayout") -> "DesignerForm":
        item = ET.SubElement(self.main_layout, "item")
        form_layout = ET.SubElement(item, "layout", {"class": "QFormLayout", "name": layout_name})
        for spec in fields:
            _form_row(form_layout, spec)
        return self

    def add_buttons(self, buttons: Iterable[tuple[str, str]]) -> "DesignerForm":
        item = ET.SubElement(self.main_layout, "item")
        layout = ET.SubElement(item, "layout", {"class": "QHBoxLayout", "name": "horizontalLayout_buttons"})
        for text, object_name in buttons:
            button_item = ET.SubElement(layout, "item")
            button = ET.SubElement(button_item, "widget", {"class": "QPushButton", "name": object_name})
            _property(button, "text", text)
        return self

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_pretty_xml(self.root), encoding="utf-8")
        return target


def write_form_ui(
    path: str | Path,
    fields: Iterable[FieldSpec],
    *,
    class_name: str = "Form",
    title: str = "Форма",
    buttons: Iterable[tuple[str, str]] = (("Сохранить", "pushButton_save"), ("Отмена", "pushButton_cancel")),
) -> Path:
    return DesignerForm(class_name).add_title(title).add_form(fields).add_buttons(buttons).write(path)


def write_auth_ui(path: str | Path, *, class_name: str = "Auth", title: str = "Авторизация") -> Path:
    from .fields import field

    fields = [
        field("login", "Логин", object_name="lineEdit_login"),
        field("pass", "Пароль", "password", object_name="lineEdit_pass"),
    ]
    return write_form_ui(
        path,
        fields,
        class_name=class_name,
        title=title,
        buttons=(("Войти", "pushButton_login"), ("Гость", "pushButton_guest")),
    )


def write_main_window_ui(
    path: str | Path,
    *,
    class_name: str = "MainWindow",
    tabs: Iterable[str] = ("Каталог", "Мои заказы", "Все заказы", "Статистика"),
) -> Path:
    root = _base_ui(class_name, 900, 650)
    widget = root.find("./widget")
    main_layout = ET.SubElement(widget, "layout", {"class": "QVBoxLayout", "name": "verticalLayout"})

    top_item = ET.SubElement(main_layout, "item")
    top = ET.SubElement(top_item, "layout", {"class": "QHBoxLayout", "name": "horizontalLayout_top"})
    for cls, name, text in (
        ("QLabel", "label_title", class_name),
        ("QLabel", "label_user", "Пользователь"),
        ("QPushButton", "pushButton_logout", "Выйти"),
    ):
        item = ET.SubElement(top, "item")
        child = ET.SubElement(item, "widget", {"class": cls, "name": name})
        _property(child, "text", text)

    tab_item = ET.SubElement(main_layout, "item")
    tab_widget = ET.SubElement(tab_item, "widget", {"class": "QTabWidget", "name": "tabWidget"})
    for index, tab_title in enumerate(tabs):
        tab = ET.SubElement(tab_widget, "widget", {"class": "QWidget", "name": f"tab_{index}"})
        _attribute(tab, "title", tab_title)
        layout = ET.SubElement(tab, "layout", {"class": "QVBoxLayout", "name": f"verticalLayout_tab_{index}"})
        scroll_item = ET.SubElement(layout, "item")
        scroll = ET.SubElement(scroll_item, "widget", {"class": "QScrollArea", "name": f"scrollArea_{index}"})
        _property(scroll, "widgetResizable", True)
        content = ET.SubElement(scroll, "widget", {"class": "QWidget", "name": f"scrollAreaWidgetContents_{index}"})
        _rect_property(content, "geometry", 0, 0, 760, 420)
        ET.SubElement(content, "layout", {"class": "QVBoxLayout", "name": f"verticalLayout_content_{index}"})

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_pretty_xml(root), encoding="utf-8")
    return target


def _base_ui(class_name: str, width: int, height: int) -> ET.Element:
    root = ET.Element("ui", {"version": "4.0"})
    class_node = ET.SubElement(root, "class")
    class_node.text = class_name
    widget = ET.SubElement(root, "widget", {"class": "QWidget", "name": class_name})
    _rect_property(widget, "geometry", 0, 0, width, height)
    _property(widget, "windowTitle", class_name)
    ET.SubElement(root, "resources")
    ET.SubElement(root, "connections")
    return root


def _form_row(form_layout: ET.Element, spec: FieldSpec) -> None:
    label_item = ET.SubElement(form_layout, "item", {"row": str(_row_count(form_layout)), "column": "0"})
    label = ET.SubElement(label_item, "widget", {"class": "QLabel", "name": f"label_{spec.name}"})
    _property(label, "text", spec.title)

    field_item = ET.SubElement(form_layout, "item", {"row": str(_row_count(form_layout) - 1), "column": "1"})
    widget = ET.SubElement(field_item, "widget", {"class": _widget_class(spec), "name": spec.qt_object_name})
    if spec.placeholder and spec.kind in ("text", "password", "multiline"):
        _property(widget, "placeholderText", spec.placeholder)
    if spec.kind == "password":
        prop = ET.SubElement(widget, "property", {"name": "echoMode"})
        enum = ET.SubElement(prop, "enum")
        enum.text = "QLineEdit::EchoMode::Password"
    if spec.kind in ("int", "float") and spec.max_value is not None:
        _property(widget, "maximum", spec.max_value)
    if spec.kind in ("int", "float") and spec.min_value is not None:
        _property(widget, "minimum", spec.min_value)
    if spec.kind == "combo":
        for choice in spec.choices:
            item = ET.SubElement(widget, "item")
            _property(item, "text", choice.label)


def _widget_class(spec: FieldSpec) -> str:
    return {
        "text": "QLineEdit",
        "password": "QLineEdit",
        "int": "QSpinBox",
        "float": "QDoubleSpinBox",
        "date": "QDateEdit",
        "combo": "QComboBox",
        "multiline": "QTextEdit",
        "bool": "QCheckBox",
    }[spec.kind]


def _row_count(layout: ET.Element) -> int:
    rows = [int(item.attrib.get("row", 0)) for item in layout.findall("item")]
    return max(rows, default=-1) + 1


def _property(parent: ET.Element, name: str, value: object) -> None:
    prop = ET.SubElement(parent, "property", {"name": name})
    if isinstance(value, bool):
        node = ET.SubElement(prop, "bool")
        node.text = "true" if value else "false"
    elif isinstance(value, int):
        node = ET.SubElement(prop, "number")
        node.text = str(value)
    elif isinstance(value, float):
        node = ET.SubElement(prop, "double")
        node.text = str(value)
    else:
        node = ET.SubElement(prop, "string")
        node.text = str(value)


def _attribute(parent: ET.Element, name: str, value: str) -> None:
    attr = ET.SubElement(parent, "attribute", {"name": name})
    node = ET.SubElement(attr, "string")
    node.text = value


def _rect_property(parent: ET.Element, name: str, x: int, y: int, width: int, height: int) -> None:
    prop = ET.SubElement(parent, "property", {"name": name})
    rect = ET.SubElement(prop, "rect")
    for tag, value in (("x", x), ("y", y), ("width", width), ("height", height)):
        node = ET.SubElement(rect, tag)
        node.text = str(value)


def _pretty_xml(root: ET.Element) -> str:
    rough = ET.tostring(root, encoding="utf-8")
    return minidom.parseString(rough).toprettyxml(indent=" ")
