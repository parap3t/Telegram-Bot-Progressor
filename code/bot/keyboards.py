# Импортируем недостающие модули
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.requests import getEvents

# Панель администратора
adminPanel = ReplyKeyboardMarkup(keyboard=[
                                  [KeyboardButton(text="🎇Создать мероприятие"),KeyboardButton(text="🎆Удалить мероприятие")],
                                  [KeyboardButton(text="🚫Забанить пользователя"),KeyboardButton(text="✅Разбанить пользователя")],
                                  [KeyboardButton(text="➕Добавить админа"),KeyboardButton(text="➖Удалить админа")],
                                  [KeyboardButton(text="🗣️Сделать рассылку")],
                                  [KeyboardButton(text="🤖Назад")],
                                  ],
                                  input_field_placeholder = "Выберите пункт меню...",
                                  resize_keyboard=True)

# Меню администратора
adminMenu = ReplyKeyboardMarkup(keyboard=[
                                [KeyboardButton(text="🎉Мероприятия")],
                                [KeyboardButton(text="⚙️Админ.панель")],
                                [KeyboardButton(text="💻Тех.поддержка")],
                                [KeyboardButton(text="👤Наши контакты")] 
                                ],
                                input_field_placeholder = "Выберите пункт меню...",
                                resize_keyboard=True)

# Панель админа для взаимодействия с мероприятиями
adminEventPanel = ReplyKeyboardMarkup(keyboard=[
                                [KeyboardButton(text="👥Записавшиеся")],
                                [KeyboardButton(text="🔙Назад")]
                                ],
                                input_field_placeholder = "Выберите пункт меню...",
                                resize_keyboard=True)

# Кнопка для отмены действия админа
adminCancelMarkup = ReplyKeyboardMarkup(keyboard=[
                                    [KeyboardButton(text="❌Отмена")]
                                    ],
                                    input_field_placeholder = "Нажмите кнопку,если передумаете...",
                                    resize_keyboard=True)

# Меню пользователя
userMenu = ReplyKeyboardMarkup(keyboard=[
                                [KeyboardButton(text="🎉Мероприятия")],
                                [KeyboardButton(text="💻Тех.поддержка")],
                                [KeyboardButton(text="👤Наши контакты")] 
                                ],
                                input_field_placeholder = "Выберите пункт меню...",
                                resize_keyboard=True)

# Меню для не записавшегося на мероприятие пользователя
eventUnSignUp = ReplyKeyboardMarkup(keyboard=[ 
                                [KeyboardButton(text="📝Записаться")],
                                [KeyboardButton(text="🔙Назад")]
                                ],
                                input_field_placeholder = "Выберите пункт меню...",
                                resize_keyboard=True)

# Меню для записавшегося на мероприятие пользователя
eventSignUp = ReplyKeyboardMarkup(keyboard=[
                                [KeyboardButton(text="❌Я не приду")],
                                [KeyboardButton(text="🔙Назад")]],
                                input_field_placeholder = "Выберите пункт меню...",
                                resize_keyboard=True)

# Кнопка для выхода с мероприятий
eventBack =  ReplyKeyboardMarkup(keyboard=[
                                [KeyboardButton(text="🔙Назад")]],
                                input_field_placeholder = "Выберите пункт меню...",
                                resize_keyboard=True)

# Кнопка для отмены действия пользователя
userCancelMarkup = ReplyKeyboardMarkup(keyboard=[
                                    [KeyboardButton(text="🚫Отмена")]
                                    ],
                                    input_field_placeholder = "Нажмите кнопку,если передумаете...",
                                    resize_keyboard=True)

# Кнопки с ссылками на контакты
ourContacts = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="ВКонтакте",url="https://vk.com/progressor45")],
                                    [InlineKeyboardButton(text="Телеграм",url="https://t.me/progressor45")]
                                    ])

# Кнопки с ссылками на техническую поддержку
techSupport = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="ВКонтакте",url="https://vk.com/parap3t")],
                                    [InlineKeyboardButton(text="Телеграм",url="https://t.me/parap3t")]
                                    ])

# Кнопки для подтверждения рассылки
mailingConfirm = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="✅Подтвердить",callback_data="confirm_mailing")],
                                    [InlineKeyboardButton(text="❌Отменить",callback_data="unconfirm_mailing")]
                                    ])

# Кнопки для подтверждения создания мероприятия
addEventConfirm = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="✅Подтвердить",callback_data="confirmAddEvent")],
                                    [InlineKeyboardButton(text="❌Отменить",callback_data="unConfirmAddEvent")]
                                    ])

# Кнопки для подтверждения удаления мероприятия
delEventConfirm = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="✅Подтвердить",callback_data="confirmDelEvent")],
                                    [InlineKeyboardButton(text="❌Отменить",callback_data="unConfirmDelEvent")]
                                    ])

# Кнопки для подтверждения записи на мероприятие
confirmSignUp = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="✅Подтвердить",callback_data="confirmSignUp")],
                                    [InlineKeyboardButton(text="❌Отменить",callback_data="unConfirmSignUp")]
                                    ])

# Кнопки для подтверждения отмены записи на мероприятие
confirmWontCome = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="✅Подтвердить",callback_data="confirmWontCome")],
                                    [InlineKeyboardButton(text="❌Отменить",callback_data="unConfirmWontCome")]
                                    ])

# Создаём меню с пероприятиями
async def getEventsButtons(): 
    keyboard  = ReplyKeyboardBuilder()
    checker : bool = False
    for event in await getEvents():
        keyboard.add(KeyboardButton(text=f"{event.name}"))
        checker = True
    if checker:
        keyboard.add(KeyboardButton(text="👈Назад"))
        return keyboard.adjust(1).as_markup(resize_keyboard = True,input_field_placeholder = "Выберите пункт меню...")
    else:
        return checker