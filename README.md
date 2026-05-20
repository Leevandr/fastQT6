# fastqt6

`fastqt6` - это небольшая библиотека-шаблон для PyQt6-проектов: динамические формы,
CRUD-окна, SQL-хелперы и генерация `.ui` файлов для Qt Designer.

Установка после публикации:

```bash
pip install fastqt6
```

Локальная установка из репозитория:

```bash
python -m pip install -e .
```

## Быстрый пример

```python
from PyQt6.QtWidgets import QApplication
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
)
window.show()
app.exec()
```

## SQL-хелперы

SQLite:

```python
from fastqt6 import SQLDatabase

db = SQLDatabase.sqlite("app.db")
db.insert("products", {"article": "A-1", "title": "Мяч", "price": 1000})
rows = db.select("products", where="price > ?", params=(500,), order_by="title")
db.update("products", {"price": 1200}, "id=?", (1,))
db.delete("products", "id=?", (1,))
```

MySQL:

```python
from fastqt6 import SQLDatabase

db = SQLDatabase.mysql("sportplus_kvalik", user="root", password="")
user = db.login("users", "admin", "admin")
rows = db.fetch_all("select * from products where title like ?", ("%мяч%",))
```

В запросах можно писать `?` как универсальный placeholder. Для MySQL библиотека
сама заменит его на `%s`.

## Динамические формы

```python
from fastqt6 import field
from fastqt6.forms import DynamicFormDialog

fields = [
    field("article", "Артикул", required=True),
    field("title", "Название", required=True),
    field("price", "Цена", "float", min_value=0),
    field("category_id", "Категория", "combo", choices=[("Мячи", 1), ("Обувь", 2)]),
]

dialog = DynamicFormDialog(fields, title="Товар")
if dialog.exec():
    data = dialog.get_data()
```

## Генерация файлов Qt Designer

Создать `auth.ui`:

```bash
fastqt6 ui-auth ui/auth.ui
```

Создать главное окно с вкладками:

```bash
fastqt6 ui-main ui/main.ui --tabs "Каталог,Мои заказы,Все заказы,Статистика"
```

Создать форму:

```bash
fastqt6 ui-form ui/product.ui \
  --title "Товар" \
  --class-name "ProductDialog" \
  --field article:text:Артикул \
  --field title:text:Название \
  --field price:float:Цена \
  --field stock:int:Остаток
```

После этого файл можно открыть в Qt Designer или конвертировать:

```bash
pyuic6 ui/product.ui -o gen/product.py
```

## CLI

```text
fastqt6 scaffold my_app
fastqt6 ui-auth ui/auth.ui
fastqt6 ui-main ui/main.ui
fastqt6 ui-form ui/form.ui --field title:text:Название
```

## Что вводить на PyPI Trusted Publisher

Для репозитория `git@github.com:Leevandr/fastQT6.git` заполни форму так:

```text
PyPI Project Name: fastqt6
Owner: Leevandr
Repository name: fastQT6
Workflow name: publish.yml
Environment name: pypi
```

Workflow уже лежит в `.github/workflows/publish.yml`. В GitHub желательно создать
environment с названием `pypi`: `Settings -> Environments -> New environment`.

Публикация пойдет через GitHub Actions без API-токена: после настройки Trusted
Publisher создай GitHub Release или запусти workflow вручную.
