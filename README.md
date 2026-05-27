# fastqt6

`fastqt6` - небольшая библиотека для подготовки к PyQt6/MySQL-проектам на демоэкзамене 09.02.07: готовые шаблоны, CRUD-окна, генерация `.ui` файлов и офлайн-документы.

## Установка

```bash
python -m pip install fastqt6
```

Локально из репозитория:

```bash
python -m pip install -e .
```

## Готовый проект «Обувь»

Создать полный шаблон проекта для демоэкзамена:

```bash
fastqt6 exam-obuv demo_exam_obuv
cd demo_exam_obuv
python -m venv .venv
.\.venv\Scripts\activate.ps1
python -m pip install -r requirements.txt
python -m src.main
```

Если команда `fastqt6` не находится:

```bash
python -m fastqt6.cli exam-obuv demo_exam_obuv
```

Внутри шаблона уже есть:

- `src/` - PyQt6-приложение с авторизацией, ролями, товарами и заказами;
- `ui/` - исходные `.ui` файлы Qt Designer и сгенерированные Python-файлы;
- `sql/shoes.sql` - база данных MySQL для импорта;
- `resources/images/` - изображения и заглушка товара;
- `docs/DEMO_EXAM_OBUV_GUIDE.md` - чек-лист требований, баллов и ручной проверки;
- `docs/er_diagram.pdf` - ER-диаграмма для сдачи;
- `docs/algorithm.pdf` - блок-схема алгоритма для сдачи.

База в шаблоне рассчитана на MySQL: база `shoes`, порт `3308`, пользователь `root`, пароль пустой. Эти значения легко поменять в `src/db.py`.

Тестовые пользователи:

| Роль | Логин | Пароль |
|---|---|---|
| Администратор | `admin` | `1` |
| Администратор | `levandr` | `1` |
| Менеджер | `manager` | `1` |
| Клиент | `client` | `1` |
| Гость | кнопка гостевого входа | без пароля |

## Вариант demo_28

Создать проект из публичного репозитория `yulechkamsk1/demo_28`:

```bash
fastqt6 demo-28 demo_28
cd demo_28
python -m pip install -r requirements.txt
python -m authwindow
```

Этот вариант скачивается с GitHub при выполнении команды. Код не упакован внутрь wheel напрямую, потому что в исходном репозитории нет отдельного файла лицензии. Команда добавляет в созданную папку `FASTQT6_README.md`, `.gitignore` и `requirements.txt`.

## Офлайн-гайд по демоэкзамену

Показать путь к гайду внутри установленной библиотеки:

```bash
fastqt6 exam-guide
```

Скопировать гайд в текущий проект:

```bash
fastqt6 exam-guide --copy
```

Вывести текст прямо в терминал:

```bash
fastqt6 exam-guide --print
```

## Минимальный CRUD-шаблон

```bash
fastqt6 scaffold my_app
cd my_app
python main.py
```

Он создает маленькое SQLite-приложение с таблицей товаров. Это удобно, если нужно быстро вспомнить базовую механику `fastqt6`, без большого экзаменационного проекта.

## Генерация `.ui` файлов

Создать окно авторизации:

```bash
fastqt6 ui-auth ui/Auth.ui
```

Создать главное окно с вкладками:

```bash
fastqt6 ui-main ui/MainWidget.ui --tabs "Товары,Заказы"
```

Создать форму:

```bash
fastqt6 ui-form ui/ItemDialog.ui \
  --title "Товар" \
  --class-name ItemDialog \
  --field article:text:Артикул \
  --field title:text:Название \
  --field price:float:Цена
```

Конвертация `.ui` в Python:

```bash
pyuic6 ui/ItemDialog.ui -o ui/gen/ItemDialog.py
```

## SQL-хелпер

SQLite:

```python
from fastqt6 import SQLDatabase

db = SQLDatabase.sqlite("app.db")
db.insert("products", {"article": "A-1", "title": "Кроссовки", "price": 2500})
rows = db.select("products", where="price > ?", params=(1000,), order_by="title")
```

MySQL:

```python
from fastqt6 import SQLDatabase

db = SQLDatabase.mysql("shoes", user="root", password="", port=3308)
user = db.login("users", "admin", "1")
rows = db.fetch_all("select * from products where title like ?", ("%кросс%",))
```

В запросах можно писать `?` как универсальный placeholder. Для MySQL библиотека сама заменит его на `%s`.

## Динамические формы

```python
from fastqt6 import field
from fastqt6.forms import DynamicFormDialog

fields = [
    field("article", "Артикул", required=True),
    field("title", "Название", required=True),
    field("price", "Цена", "float", min_value=0),
    field("category_id", "Категория", "combo", choices=[("Кроссовки", 1), ("Туфли", 2)]),
]

dialog = DynamicFormDialog(fields, title="Товар")
if dialog.exec():
    data = dialog.get_data()
```

## Публикация на PyPI

Для Trusted Publisher на PyPI:

```text
PyPI Project Name: fastqt6
Owner: Leevandr
Repository name: fastQT6
Workflow name: publish.yml
Environment name: pypi
```

Workflow уже лежит в `.github/workflows/publish.yml`. После пуша и создания GitHub Release публикация пойдет через GitHub Actions без API-токена.
