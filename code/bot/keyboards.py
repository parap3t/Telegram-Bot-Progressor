from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.requests import get_events


OUR_CONTACTS = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="ВКонтакте", url="https://vk.com/progressor45")],
                                    [InlineKeyboardButton(text="Телеграм", url="https://t.me/progressor45")]
                                    ])


TECH_SUPPORT = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="ВКонтакте", url="https://vk.com/parap3t")],
                                    [InlineKeyboardButton(text="Телеграм", url="https://t.me/parap3t")]
                                    ])


ADMIN_PANEL = ReplyKeyboardMarkup(keyboard=[
                                  [KeyboardButton(text="🎇Создать мероприятие"), KeyboardButton(text="🎆Удалить мероприятие")],
                                  [KeyboardButton(text="🚫Забанить пользователя"), KeyboardButton(text="✅Разбанить пользователя")],
                                  [KeyboardButton(text="➕Добавить админа"), KeyboardButton(text="➖Удалить админа")],
                                  [KeyboardButton(text="🗣️Сделать рассылку")],
                                  [KeyboardButton(text="🤖Назад")],
                                  ], input_field_placeholder="Выберите пункт меню...", resize_keyboard=True)


ADMIN_CANCEL_MARKUP = ReplyKeyboardMarkup(keyboard=[
                                    [KeyboardButton(text="❌Отмена")]
                                    ], input_field_placeholder="Нажмите кнопку,если передумаете...",
                                    resize_keyboard=True)


async def get_event_menu(*, RIGHTS: str, EVENT_STATUS: str = ""):
    
    keyboard = ReplyKeyboardBuilder()
    
    if RIGHTS == "admin":
        
        keyboard.add(KeyboardButton(text="👥Записавшиеся"))
        keyboard.add(KeyboardButton(text="❌Закрыть запись"))
        
    else:
        
        if EVENT_STATUS == "unsigned":
            keyboard.add(KeyboardButton(text="📝Записаться"))
        
        elif EVENT_STATUS == "signed":
            keyboard.add(KeyboardButton(text="❌Я не приду"))
            
    keyboard.add(KeyboardButton(text="🔙Назад"))
    
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


async def get_user_cancel_button(addition: str = ""):
    
    keyboard = ReplyKeyboardBuilder()
    
    if addition == "phone":
        keyboard.add(KeyboardButton(text="📞Отправить", request_contact=True))
    
    keyboard.add(KeyboardButton(text="🚫Отмена"))
    
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Нажмите на кнопку,если передумаете...")


async def get_start_menu(*, RIGHTS: str):
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🎉Мероприятия"))
    
    if RIGHTS == "admin":
        keyboard.add(KeyboardButton(text=f"⚙️Админ панель"))
        
    else:
        keyboard.add(KeyboardButton(text="👤Наши контакты"))
        
    keyboard.add(KeyboardButton(text="💻Тех поддержка"))
    
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


async def get_confirm_menu(*, CALLBACK: str):
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="✅Подтвердить", callback_data=f"{CALLBACK}")],
                                    [InlineKeyboardButton(text="❌Отменить", callback_data=f"{"un" + CALLBACK}")]
                                    ])
    
    return keyboard


# Создаём меню с мероприятиями
async def get_events_names_buttons():
    
    keyboard = ReplyKeyboardBuilder()
    
    for event in await get_events():
        keyboard.add(KeyboardButton(text=f"{event.name}"))  
    
    keyboard.add(KeyboardButton(text="👈Назад"))
    
    return keyboard.adjust(1).as_markup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")