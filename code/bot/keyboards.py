import bot.constants.keyboards as const
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.requests import get_events


# Инлайн клавиатуры с контактами
OUR_CONTACTS = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ВКонтакте", url=const.ADMIN_VK_URL)],
    [InlineKeyboardButton(text="Телеграм", url=const.ADMIN_TG_URL)]
])


TECH_SUPPORT = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ВКонтакте", url=const.PUBLIC_VK_URL)],
    [InlineKeyboardButton(text="Телеграм", url=const.PUBLIC_TG_URL)]
])


# Клавиатура для админ панели
ADMIN_PANEL = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🎇Создать мероприятие"), KeyboardButton(text="🎆Удалить мероприятие")],
    [KeyboardButton(text="🚫Забанить пользователя"), KeyboardButton(text="✅Разбанить пользователя")],
    [KeyboardButton(text="➕Добавить админа"), KeyboardButton(text="➖Удалить админа")],
    [KeyboardButton(text="🗣️Сделать рассылку")],
    [KeyboardButton(text="🤖Назад")],
], input_field_placeholder="Выберите пункт меню...", resize_keyboard=True)


# Клавиатура для админ панели с минимальным выбором
ADMIN_PANEL_MARKUP = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⚙️Админ панель")]
], input_field_placeholder="Нажмите кнопку,если передумаете...", resize_keyboard=True)


# Клавиатура для отмены
ADMIN_CANCEL_MARKUP = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="❌Отмена")]
], input_field_placeholder="Нажмите кнопку,если передумаете...", resize_keyboard=True)


# Клавиатура для отправки номера телефона
USER_PHONE_MARKUP = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📞Отправить", request_contact=True)]
], input_field_placeholder="Нажмите кнопку, чтобы отправить свой номер телефона", resize_keyboard=True)


async def get_event_menu(*, rights: str, event_status: str = "") -> ReplyKeyboardMarkup:
    """
    Создаёт меню для выбора действий с мероприятием.

    :param rights: Права пользователя, могут быть 'admin' или другие.
    :param event_status: Статус мероприятия ('unsigned', 'signed' или пусто).
    :return: Клавиатура для меню.
    """

    keyboard = ReplyKeyboardBuilder()

    if rights == "admin":
        keyboard.add(KeyboardButton(text="👥Отчёт"))
        keyboard.add(KeyboardButton(text="📊Собрать обратную связь"))
        keyboard.add(KeyboardButton(text="🔐Закрыть запись"))
        keyboard.add(KeyboardButton(text="📷Отметка по QR-коду"))

    else:

        if event_status == "unsigned":
            keyboard.add(KeyboardButton(text="📝Записаться"))

        elif event_status == "signed":
            keyboard.add(KeyboardButton(text="❌Я не приду"))

    keyboard.add(KeyboardButton(text="🔙Назад"))

    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


async def get_user_cancel_button(addition: str = "") -> ReplyKeyboardMarkup:
    """
    Создаёт клавиатуру для отмены действия с возможностью отправки контакта.

    :param addition: Дополнительный параметр для отображения кнопки отправки контакта.
    :return: Клавиатура с кнопкой отмены.
    """

    keyboard = ReplyKeyboardBuilder()

    if addition == "phone":
        keyboard.add(KeyboardButton(text="📞Отправить", request_contact=True))

    keyboard.add(KeyboardButton(text="🚫Отмена"))

    return keyboard.adjust(1).as_markup(resize_keyboard=True,
                                        input_field_placeholder="Нажмите на кнопку,если передумаете...")


async def get_start_menu(*, rights: str) -> ReplyKeyboardMarkup:

    """
    Создаёт стартовое меню с кнопками для пользователя или админа.

    :param rights: Права пользователя, могут быть 'admin' или другие.
    :return: Клавиатура для стартового меню.
    """

    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🎉Мероприятия"))

    if rights == "admin":
        keyboard.add(KeyboardButton(text=f"⚙️Админ панель"))

    else:
        keyboard.add(KeyboardButton(text="❓Помощь"))
        keyboard.add(KeyboardButton(text="👤Наши контакты"))

    keyboard.add(KeyboardButton(text="💻Тех поддержка"))

    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


async def get_confirm_menu(*, callback: str) -> InlineKeyboardMarkup:
    """
    Создаёт меню для подтверждения действия с кнопками "Подтвердить" и "Отменить".

    :param callback: Данные, которые будут переданы при нажатии на кнопки.
    :return: Клавиатура для подтверждения.
    """

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅Подтвердить", callback_data=f"{callback}")],
        [InlineKeyboardButton(text="❌Отменить", callback_data=f"un{callback}")]
    ])

    return keyboard


async def get_events_names_buttons() -> ReplyKeyboardMarkup:
    """
    Создаёт меню с кнопками для выбора названия мероприятий.

    :return: Клавиатура с названиями мероприятий.
    """

    keyboard = ReplyKeyboardBuilder()

    # Проходимся по списку с мероприятиями
    for event in await get_events():
        keyboard.add(KeyboardButton(text=f"{event.name}"))  # добавляем название мероприятия в клавиатуру

    keyboard.add(KeyboardButton(text="👈Назад"))

    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")