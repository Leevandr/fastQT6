# Публикация на PyPI

## 1. Настройка PyPI Trusted Publisher

На странице PyPI `Publishing -> Manage trusted publishers` выбери GitHub и заполни:

```text
PyPI Project Name: fastqt6
Owner: Leevandr
Repository name: fastQT6
Workflow name: publish.yml
Environment name: pypi
```

## 2. Настройка GitHub

В репозитории `Leevandr/fastQT6` создай environment:

```text
Settings -> Environments -> New environment -> pypi
```

Можно оставить без дополнительных правил.

## 3. Публикация

Вариант 1:

```text
GitHub -> Releases -> Draft a new release -> tag v0.1.0 -> Publish release
```

Вариант 2:

```text
GitHub -> Actions -> Publish to PyPI -> Run workflow
```

После успешного workflow установка будет:

```bash
pip install fastqt6
```
