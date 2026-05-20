from PyQt6.QtWidgets import QApplication
from fastqt6 import SQLDatabase, field
from fastqt6.widgets import CrudWindow


SCHEMA = """
create table if not exists products (
    id integer primary key autoincrement,
    article text not null,
    title text not null,
    category text,
    brand text,
    supplier text,
    price real not null default 0,
    stock integer not null default 0,
    discount real not null default 0
);
"""


if __name__ == "__main__":
    app = QApplication([])
    db = SQLDatabase.sqlite("sportshop.db")
    db.run_script(SCHEMA)

    window = CrudWindow(
        db,
        table="products",
        title="Спорттовары",
        fields=[
            field("article", "Артикул", required=True),
            field("title", "Название", required=True),
            field("category", "Категория"),
            field("brand", "Бренд"),
            field("supplier", "Поставщик"),
            field("price", "Цена", "float", min_value=0),
            field("stock", "Остаток", "int", min_value=0),
            field("discount", "Скидка", "float", min_value=0, max_value=100),
        ],
    )
    window.resize(900, 480)
    window.show()
    app.exec()
