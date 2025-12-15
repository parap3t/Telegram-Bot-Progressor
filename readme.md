# Telegram bot Progressor

## Описание
**Телеграм бот Progressor** - бот, 
который позволяет пользователям быстро и удобно записываться на различные 
мероприятия. Бот предоставляет возможность выбора и записи на мероприятия, а 
также информацию о месте проведения и информацию о предстоящем событии. 
Кроме того, бот может отправлять напоминания о предстоящих мероприятиях. 

## Используемые технологии:

* `Python 3.12`  
* `sqlalchemy`
* `xlsxwriter`  
* `python-dotenv`
* `qrcode`
* `pillow`
* `aiosqlite`   
* `openpyxl`
* `aiogram`  
* `asyncio`
* `pandas`
* `poetry`   
* `re`
* `os`
___

## Функционал бота
* [Пользователь](https://disk.yandex.ru/i/0d4Ewud2nw5xkw)
* [Админ](https://disk.yandex.ru/i/9dAWvtFI-34tHg)
___
## Структура проекта
- **`bot/configs/`** — содержит конфигурационные файлы с настройками бота
- **`bot/handlers/`** — обработчики сообщений, команд пользователей и администратора
- **`database/`** — модели данных и SQL-запросы для работы с базой
- **`qr_codes/`** — папка для QR-кодов
- **`report_tables/`** — папка для отчетов в форматах .xlsx
- **`pyproject.toml` + `poetry.lock`** — управление зависимостями через Poetry
___

## Зависимости
### Скопируем проект и перейдём в него
```python
git clone https://github.com/parap3t/Telegram-Bot-Progressor
cd Telegram-Bot-Progressor
```
## Windows

### Установим инструмент для управления зависимостями Poetry
```python
pip install poetry
```
### Установим зависимости
```python
poetry install
```
### Активируем окружение
```python
poetry shell
```
___

## Linux/macOS
### Установим инструмент для управления зависимостями Poetry
```python
pip3 install poetry
```
### Установим зависимости
```python
poetry install
```
### Активируем окружение
```python
poetry shell
```
___

## Активация
Для полноценной работы проекта нужно:  
1.  Получить токен своего бота в телеграм боте *BotFather*;
2.  Создать файл *.env*;
3.  Создать переменные: *BOT_API*, *ADMIN_CHAT_ID*, *ADMIN_FULL_NAME* и *ADMIN_PHONE*, а также внести в них соответствующие значения; 
___
## Документация
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [sqlalchemy](https://www.sqlalchemy.org/)
* [xlsxwriter](https://xlsxwriter.readthedocs.io/introduction.html)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
* [aiogram](https://docs.aiogram.dev/en/latest/)
* [asyncio](https://docs.python.org/3/library/asyncio.html)
* [pandas](https://pandas.pydata.org/)
* [poetry](https://python-poetry.org/docs/)
* [qrcode](https://pypi.org/project/qrcode/)
* [re](https://docs.python.org/3/library/re.html)
* [os](https://docs.python.org/3/library/os.html)