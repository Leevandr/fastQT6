"""Project scaffold helpers."""

from __future__ import annotations

from pathlib import Path


MAIN_PY = '''from PyQt6.QtWidgets import QApplication
from fastqt6 import SQLDatabase, field
from fastqt6.widgets import CrudWindow


SCHEMA = """
create table if not exists products (
    id integer primary key autoincrement,
    article text not null,
    title text not null,
    price real not null default 0,
    stock integer not null default 0
);
"""


if __name__ == "__main__":
    app = QApplication([])
    db = SQLDatabase.sqlite("app.db")
    db.run_script(SCHEMA)

    window = CrudWindow(
        db,
        table="products",
        fields=[
            field("article", "Артикул", required=True),
            field("title", "Название", required=True),
            field("price", "Цена", "float", min_value=0),
            field("stock", "Остаток", "int", min_value=0),
        ],
        title="FastQT6 demo",
    )
    window.resize(760, 420)
    window.show()
    app.exec()
'''


def scaffold_basic_app(target_dir: str | Path) -> Path:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "main.py").write_text(MAIN_PY, encoding="utf-8")
    return target
