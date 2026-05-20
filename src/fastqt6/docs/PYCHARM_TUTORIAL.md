# FastQT6 offline tutorial

Этот файл лежит прямо внутри установленной библиотеки `fastqt6`.
Его можно открыть без интернета в PyCharm:

```text
External Libraries
  -> Python ...
  -> site-packages
  -> fastqt6
  -> docs
  -> PYCHARM_TUTORIAL.md
```

Можно также скопировать этот файл в свой проект:

```bash
fastqt6 tutorial --copy
```

Если команда `fastqt6` не находится:

```bash
python -m fastqt6.cli tutorial --copy
```

## 1. Установка до поездки

Пока интернет есть, скачай пакет:

```bash
python -m pip install fastqt6
```

Если нужно скачать файл пакета для переноса на флешке:

```bash
python -m pip download fastqt6 -d fastqt6_offline
```

На другом компьютере без интернета:

```bash
python -m pip install --no-index --find-links fastqt6_offline fastqt6
```

## 2. Создание проекта в PyCharm

1. Открой PyCharm.
2. Выбери `File -> New Project`.
3. Тип проекта: `Pure Python`.
4. Открой вкладку `Terminal` внизу PyCharm.

Проверь установку:

```bash
python -c "import fastqt6; print(fastqt6.__version__)"
```

## 3. Первый проект за минуту

В терминале PyCharm:

```bash
fastqt6 scaffold .
```

Появится файл:

```text
main.py
```

Запусти `main.py`. Откроется простое CRUD-окно с таблицей товаров.

## 4. Что делает scaffold

Он создает минимальный пример:

```python
from PyQt6.QtWidgets import QApplication
from fastqt6 import SQLDatabase, field
from fastqt6.widgets import CrudWindow

app = QApplication([])
db = SQLDatabase.sqlite("app.db")
```

SQLite используется для первого запуска, поэтому MySQL не нужен.

## 5. Поля формы

Поля описываются так:

```python
field("article", "Артикул", required=True)
field("title", "Название", required=True)
field("price", "Цена", "float", min_value=0)
field("stock", "Остаток", "int", min_value=0)
```

Типы:

```text
text       QLineEdit
password   QLineEdit с паролем
int        QSpinBox
float      QDoubleSpinBox
date       QDateEdit
combo      QComboBox
multiline  QTextEdit
bool       QCheckBox
```

## 6. SQLite-запросы

```python
from fastqt6 import SQLDatabase

db = SQLDatabase.sqlite("app.db")

db.run_script("""
create table if not exists products (
    id integer primary key autoincrement,
    title text not null,
    price real not null default 0
);
""")

db.insert("products", {"title": "Мяч", "price": 1000})
rows = db.select("products", order_by="title")
```

## 7. MySQL-запросы

```python
from fastqt6 import SQLDatabase

db = SQLDatabase.mysql(
    "sportplus_kvalik",
    user="root",
    password="",
)

products = db.fetch_all("select * from products order by title")
user = db.login("users", "admin", "admin")
```

В запросах можно писать `?`:

```python
rows = db.fetch_all("select * from products where title like ?", ("%мяч%",))
```

Для MySQL библиотека сама заменит `?` на `%s`.

## 8. Динамическая форма без Qt Designer

```python
from fastqt6 import field
from fastqt6.forms import DynamicFormDialog

fields = [
    field("article", "Артикул", required=True),
    field("title", "Название", required=True),
    field("price", "Цена", "float", min_value=0),
    field("category_id", "Категория", "combo", choices=[
        ("Мячи", 1),
        ("Обувь", 2),
    ]),
]

dialog = DynamicFormDialog(fields, title="Товар")
if dialog.exec():
    data = dialog.get_data()
    print(data)
```

## 9. Генерация .ui для Qt Designer

Создай папки:

```bash
mkdir ui gen
```

Окно авторизации:

```bash
fastqt6 ui-auth ui/auth.ui
```

Главное окно:

```bash
fastqt6 ui-main ui/main.ui --tabs "Каталог,Мои заказы,Все заказы,Статистика"
```

Форма товара:

```bash
fastqt6 ui-form ui/product.ui \
  --title "Товар" \
  --class-name ProductDialog \
  --field article:text:Артикул \
  --field title:text:Название \
  --field price:float:Цена \
  --field stock:int:Остаток
```

Конвертация:

```bash
pyuic6 ui/product.ui -o gen/product.py
```

Если `pyuic6` не находится:

```bash
python -m PyQt6.uic.pyuic ui/product.ui -o gen/product.py
```

## 10. Готовый CRUD под свою таблицу

```python
from PyQt6.QtWidgets import QApplication
from fastqt6 import SQLDatabase, field
from fastqt6.widgets import CrudWindow

app = QApplication([])
db = SQLDatabase.mysql("sportplus_kvalik", user="root", password="")

window = CrudWindow(
    db,
    table="products",
    title="Товары",
    fields=[
        field("article", "Артикул", required=True),
        field("title", "Название", required=True),
        field("price", "Цена", "float", min_value=0),
        field("stock", "Остаток", "int", min_value=0),
    ],
)
window.resize(900, 500)
window.show()
app.exec()
```

## 11. Частые проблемы

Если `No module named fastqt6`:

```bash
python -m pip install fastqt6
```

Проверь интерпретатор в PyCharm:

```text
Settings -> Project -> Python Interpreter
```

Если команда `fastqt6` не работает:

```bash
python -m fastqt6.cli scaffold .
```

Если MySQL не подключается, проверь:

```text
имя базы
логин
пароль
порт 3306 или 3308
запущен ли MySQL
```
