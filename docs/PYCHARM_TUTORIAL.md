# FastQT6: урок для PyCharm с нуля

Этот урок для человека, который поставил библиотеку через `pip install fastqt6`
и хочет быстро открыть проект в PyCharm, получить окно, таблицу, формы и файлы
Qt Designer.

## 1. Создай проект

Открой PyCharm:

```text
File -> New Project
```

Выбери:

```text
Pure Python
```

Оставь галочку создания виртуального окружения `.venv`, если PyCharm ее предлагает.
После создания проекта открой вкладку `Terminal` внизу PyCharm.

## 2. Установи библиотеку

В терминале PyCharm:

```bash
python -m pip install fastqt6
```

Проверка:

```bash
python -c "import fastqt6; print(fastqt6.__version__)"
```

Если версия вывелась, библиотека установлена правильно.

## 3. Создай готовый стартовый проект

Находясь в папке проекта, выполни:

```bash
fastqt6 scaffold .
```

Если терминал пишет, что команда `fastqt6` не найдена:

```bash
python -m fastqt6.cli scaffold .
```

В проекте появится файл:

```text
main.py
```

Запусти его через зеленую кнопку Run в PyCharm. Откроется простое окно для
добавления, редактирования и удаления товаров. По умолчанию пример использует
SQLite-файл `app.db`, поэтому MySQL для первого запуска не нужен.

## 4. Что внутри main.py

Главная идея такая:

```python
from PyQt6.QtWidgets import QApplication
from fastqt6 import SQLDatabase, field
from fastqt6.widgets import CrudWindow
```

`SQLDatabase` отвечает за запросы в базу, `field(...)` описывает поля формы, а
`CrudWindow` строит готовое окно с таблицей и кнопками.

Пример поля:

```python
field("title", "Название", required=True)
field("price", "Цена", "float", min_value=0)
field("stock", "Остаток", "int", min_value=0)
```

Типы полей:

```text
text       обычное текстовое поле
password   поле пароля
int        SpinBox
float      DoubleSpinBox
date       DateEdit
combo      ComboBox
multiline  большой текст
bool       CheckBox
```

## 5. SQLite-запросы

SQLite удобен для тренировки без сервера:

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

## 6. MySQL-запросы

Для учебных вариантов с phpMyAdmin/MySQL:

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

## 7. Своя форма без Qt Designer

Если хочешь быстро сделать форму прямо кодом:

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
        ("Фитнес", 3),
    ]),
]

dialog = DynamicFormDialog(fields, title="Товар")
if dialog.exec():
    data = dialog.get_data()
    print(data)
```

## 8. Генерация файлов Qt Designer

Создай папки:

```bash
mkdir ui gen
```

Окно авторизации:

```bash
fastqt6 ui-auth ui/auth.ui
```

Главное окно с вкладками:

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
  --field stock:int:Остаток \
  --field description:multiline:Описание
```

Файлы `.ui` можно открыть в Qt Designer, если он установлен, или сразу
конвертировать в Python:

```bash
pyuic6 ui/product.ui -o gen/product.py
```

Если `pyuic6` не находится:

```bash
python -m PyQt6.uic.pyuic ui/product.ui -o gen/product.py
```

## 9. Мини-шаблон для своего варианта

Допустим, у тебя есть таблица `products`. Тогда быстрый CRUD:

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

## 10. Частые проблемы

Если `No module named fastqt6`:

```bash
python -m pip install fastqt6
```

И проверь, что в PyCharm выбран тот же интерпретатор:

```text
Settings -> Project -> Python Interpreter
```

Если `fastqt6` как команда не запускается:

```bash
python -m fastqt6.cli scaffold .
```

Если MySQL не подключается, проверь:

```text
имя базы
логин root
пароль
порт 3306 или 3308
запущен ли MySQL
```

Если `.ui` не открывается в Designer, всё равно можно использовать файл:

```bash
pyuic6 ui/main.ui -o gen/main.py
```

## 11. Самый короткий путь

```bash
python -m pip install fastqt6
fastqt6 scaffold .
python main.py
```

Дальше меняй таблицу, поля и SQL под свое задание.
