from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.requests import get_events


# Кнопки со ссылками на контакты
our_contacts = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(
                                        text="ВКонтакте", url="https://vk.com/progressor45")],
                                    [InlineKeyboardButton(
                                        text="Телеграм", url="https://t.me/progressor45")]
                                    ])

# Кнопки со ссылками на техническую поддержку
tech_support = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(
                                        text="ВКонтакте", url="https://vk.com/parap3t")],
                                    [InlineKeyboardButton(
                                        text="Телеграм", url="https://t.me/parap3t")]
                                    ])

# Панель администратора
admin_panel = ReplyKeyboardMarkup(keyboard=[
                                  [KeyboardButton(text="🎇Создать мероприятие"), KeyboardButton(
                                      text="🎆Удалить мероприятие")],
                                  [KeyboardButton(text="🚫Забанить пользователя"), KeyboardButton(
                                      text="✅Разбанить пользователя")],
                                  [KeyboardButton(text="➕Добавить админа"), KeyboardButton(
                                      text="➖Удалить админа")],
                                  [KeyboardButton(text="🗣️Сделать рассылку")],
                                  [KeyboardButton(text="🤖Назад")],
                                  ], input_field_placeholder="Выберите пункт меню...", resize_keyboard=True)

# Кнопка для отмены действия админа
admin_cancel_markup = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="❌Отмена")]
], input_field_placeholder="Нажмите кнопку,если передумаете...",
    resize_keyboard=True)


async def get_event_menu(*, rights: str, event_status: str = "", event_name: str = ""):
    keyboard = ReplyKeyboardBuilder()
    if rights == "admin":
        keyboard.add(KeyboardButton(text="👥Записавшиеся"))
        keyboard.add(KeyboardButton(text="❌Закрыть запись"))
    else:
        if event_status == "unsigned":
            keyboard.add(KeyboardButton(text=f"📝Записаться"))
        elif event_status == "signed":
            keyboard.add(KeyboardButton(text="❌Я не приду"))
    keyboard.add(KeyboardButton(text="🔄Обновить список"))
    keyboard.add(KeyboardButton(text="🔙Назад"))

    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


async def get_user_cancel_button(*, addition: str = ""):
    keyboard = ReplyKeyboardBuilder()
    if addition == "phone":
        keyboard.add(KeyboardButton(text="📞Отправить", request_contact=True))
    keyboard.add(KeyboardButton(text="🚫Отмена"))
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Нажмите на кнопку,если передумаете...")


async def get_start_menu(*, rights: str):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🎉Мероприятия"))
    if rights == "admin":
        keyboard.add(KeyboardButton(text=f"⚙️Админ панель"))
    else:
        keyboard.add(KeyboardButton(text="👤Наши контакты"))
    keyboard.add(KeyboardButton(text="💻Тех поддержка"))
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


async def get_confirm_menu(callback: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(
                                        text="✅Подтвердить", callback_data=f"{callback}")],
                                    [InlineKeyboardButton(
                                        text="❌Отменить", callback_data='un' + callback)]
                                    ])
    return keyboard

# Создаём меню с мероприятиями


async def get_events_names_buttons():
    keyboard = ReplyKeyboardBuilder()
    for event in await get_events():
        keyboard.add(KeyboardButton(text=f"{event.name}"))
    keyboard.add(KeyboardButton(text="👈Назад"))
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")
