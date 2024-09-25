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
* `aiosqlite`   
* `openpyxl`
* `aiogram`  
* `asyncio`
* `pandas`   
* `re`
* `os`
___

## Функционал бота
* [Пользователь](https://disk.yandex.ru/i/0d4Ewud2nw5xkw)
* [Админ](https://disk.yandex.ru/i/9dAWvtFI-34tHg)
___
## Структура проекта
* ``code`` - Главная папка проекта со всеми файлами  
    * ``bot`` - Папка с основными элементами бота
        * ``admin.py`` - Файл с обработчиками сообщений админа
        * ``keyboards.py`` - Файл со всеми меню(кнопками) бота
        * ``user.py`` - Файл с обработчиками сообщений пользователя
        * ``config.py`` - Файл с API токеном бота и айди чатом админа
    * ``database`` - Папка для работы с базой данных 
        *  ``models.py`` - Файл для создания моделей(таблиц) 
        *  ``requests.py`` - Файл для sql - запросов 
    * ``run.py`` - Файл для запуска бота
___

## Зависимости
### Скопируем проект и перейдём в него
```python
git clone https://github.com/parap3t/Telegram-Bot-Progressor
cd Telegram-Bot-Progressor
```
## Windows

### Создаём виртуальное окружение
```python
python -m venv .venv
```
### Активируем виртуальное окружение
```python
.venv\Scripts\activate
```
### Устанавим необходимые фреймворки
```python
pip install -r requirements.txt
```
___

## Linux/macOS
### Создаём виртуальное окружение
```python
python3 -m venv .venv
```
### Активируем виртуальное окружение
```python
source bin/activate
```
### Устанавим необходимые фреймворки
```python
pip3 install -r requirements.txt
```
___


## Активация
Для полноценной работы проекта нужно:  
1.  Получить токен своего бота в телеграм боте *BotFather*
2. Вставить токен в файл ``config.py``, расположенный в папке ``bot``, в переменную ``BOT_API``
3. Включить бота, запустив файл ``run.py``, и отправить ему команду ``/id`` для получения айди чата
4. Полученное айди вставить в файл ``config.py`` в переменную ``ADMIN_CHAT_ID`` 
___
## Документация
* [sqlalchemy](https://www.sqlalchemy.org/)
* [xlsxwriter](https://xlsxwriter.readthedocs.io/introduction.html)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
* [aiogram](https://docs.aiogram.dev/en/latest/)
* [asyncio](https://docs.python.org/3/library/asyncio.html)
* [pandas](https://pandas.pydata.org/)
* [re](https://docs.python.org/3/library/re.html)
* [os](https://docs.python.org/3/library/os.html)
___
## Авторы
* [@parap3t](https://github.com/parap3t)
* [@cenittteee](https://github.com/cenittteee)
