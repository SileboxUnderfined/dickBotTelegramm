# DickBotTelegramm

## Бот для вашей группы в телеграмм.

Реализованный с помощью бибилотеки **pyTelegramBotAPI** бот даёт вашей беседе безграничные возможность создания т.н. ~~членов~~ коков.

### Установка (Linux):
     1. 
     2. 

### Системные значения:
   + `BOT_TOKEN` - токен вашего бота
   + `start_rand` - нижний порог генератора рандомных чисел. **Число**
   + `end_rand` - верхний порог генератора рандомных чисел. **Число**
   + `KD` - КД для команды `/dick`. **Вводить в часах**
   + `GL_TOP_END` - верхний порог команды `/global_top`. **Число**

### Команды:
   + `/start` - стартовая команда для бота
   + `/dick` - отращивает ~~член~~ кок в диапазоне от `start_rand` и `end_rand`
   + `/my_dick` - получить размер кока в данный момент
   + `/top` - топ коководов
   + `/graph` - график коководов в виде пирога
   + `/dice` - соревнование используя эмоджи кубика
   + `/global_top` - выводит топ коководов вообще в количестве равном `GL_TOP_END`
   + `/fancy_ops` - переключает возможность использования новых операций
   + `/give_dick` - позволяет отдать немного своего кока другому игроку. Синтаксис: `/give_dick {размер} @{получатель}`

### Файлы:
   + `main.py` - главный файл с полной имплементацией бота
   + `data.db` - файл базы данных sqlite3. Создавать вручную, иначе бот не запустится
   + `botFuncs.py` - вспомогательные функции бота
   + `logs` - папка с логами. Логи сохраняются в формате `.log`. Создаётся автоматически

### Структура *data.db*:
   + Таблица `users`:
     + `user_id` - айди пользователя (`INTEGER`)
     + `chat_id` - айди чата (`INTEGER`)
     + `dick_length` - длина кока (`INTEGER`)
     + `next_date` - дата КД (`TEXT`)
   + Таблица `chats`:
     + `chat_id` - айди чата (`INTEGER`)
     + `fancy_operations` - возможность использовать сложные операции (`INTEGER`)
     + `admin` - айди админа (`INTEGER`)

### Используемые библиотеки:
   + [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/)
   + [asyncio](https://pypi.org/project/asyncio/)
   + [aiohttp](https://pypi.org/project/aiohttp/)
   + [aiosqlite](https://aiosqlite.omnilib.dev/en/stable/)
   + [quickchart.io](https://quickchart.io)