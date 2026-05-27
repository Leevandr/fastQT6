Вход для клиента:
client1
client123
Для админа:
admin1
admin123
Для менеджера:
manager1
manager123

запуск 
python -m authwindow

Способ 1: --onedir (самый простой)
Просто не используй --onefile, тогда картинки лежат рядом с exe и обычные пути работают:
bash
pyinstaller --windowed main.py
В папке dist/main/ будет:
dist/main/
├── main.exe   ✅
└── images/    ← скопируй сюда свои картинки вручную
    └── photo.png