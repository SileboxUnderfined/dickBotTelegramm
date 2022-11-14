# DickBotTelegramm

## Бот для вашей группы в телеграмм.

Реализованный с помощью бибилотеки **pyTelegramBotAPI** бот даёт вашей беседе безграничные возможность создания т.н. ~~членов~~ коков.

### Системные значения:
   + `BOT_TOKEN` - токен вашего бота
   + `start_rand` - нижний порог генератора рандомных чисел. **Число**
   + `end_rand` - верхний порог генератора рандомных чисел. **Число**
   + `KD` - КД для команды `/dick`. **Вводить в часах**

### Команды:
   + `/start` - стартовая команда для бота
   + `/dick` - отращивает ~~член~~ кок в диапазоне от `start_rand` и `end_rand`
   + `/my_dick` - получить размер кока в данный момент
   + `/top` - топ коководов
   + `/graph` - график коководов в виде пирога
   + `/dice` - соревнование используя эмоджи кубика

### Файлы:
   + `main.py` - главный файл с полной имплементацией бота
   + `data.db` - файл базы данных sqlite3. Создавать вручную, иначе бот не запустится

### Структура *data.db*:
   + Таблица `users`
   + Колонки:
     + `user_id` - айди пользователя
     + `chat_id` - айди чата
     + `dick_length` - длина кока
     + `next_date` - дата КД

### Используемые библиотеки:
   + [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/)
   + [asyncio](https://pypi.org/project/asyncio/)
   + [aiohttp](https://pypi.org/project/aiohttp/)
   + [aiosqlite](https://aiosqlite.omnilib.dev/en/stable/)
   + [quickchart.io](https://quickchart.io)