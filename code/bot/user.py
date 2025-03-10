import bot.keyboards as kb
import database.requests as db

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from re import compile, search


EMPTY = None

# Чтобы не писать dispatcher 2-й раз заменим его на роутер
user = Router()


# Создаём класс (фильтр) для того, чтобы проверить забанен-ли пользователь
class BannedProtect(Filter):
    async def __call__(self, message: Message):
        return await db.check_ban(CHAT_ID=message.from_user.id)


# Создаём класс (фильтр) для проверки является-ли сообщение названием мероприятия
class EventCheck(Filter):
    async def __call__(self, message: Message):
        return await db.check_event_by_name(NAME=message.text)


# Создаём класс (состояние) для записи на мероприятие
class EventSignUp(StatesGroup):
    event_name = State()
    full_name = State()
    id = State()
    phone = State()
    confirm = State()


# Обработаем команду айди
@user.message(Command("id"))
async def id_command(message: Message):
    await message.answer(f"Ваш айди: {message.from_user.id}")


# Обработка сообщений от забаненного пользователя
@user.message(BannedProtect())
async def show_message_to_ban_user(message: Message):
    await message.answer("Вы забанены за плохое поведение!")


@user.message(CommandStart())
async def execute_start_command(message: Message):
    await db.add_in_mailing(CHAT_ID=message.from_user.id)
    await message.answer_sticker("CAACAgIAAxkBAAEDJLZlt3nrHgcV-CbOkU3EuAhDVSg4GQACkQ8AAo7aAAFIhPeRyUFm2n40BA")
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}!", reply_markup=await kb.get_start_menu(RIGHTS="user"))
    
    
@user.message(F.text == "🚫Отмена")
async def btn_cancel_click(message: Message, state: FSMContext):
    await state.set_state(EventSignUp.event_name)
    await message.answer("Отменяю действие", reply_markup=await kb.get_event_menu(RIGHTS="user", EVENT_STATUS="unsigned"))


@user.message(F.text == "👤Наши контакты")
async def btn_contacts_click(message: Message):
    await message.answer("Наши контакты:", reply_markup=kb.OUR_CONTACTS)


@user.message(F.text == "💻Тех поддержка")
async def btn_support_click(message: Message):
    await message.answer("Техническая поддержка:", reply_markup=kb.TECH_SUPPORT)


@user.message(F.text == "🎉Мероприятия")
async def btn_events_click(message: Message):
    
    NO_EVENTS_COUNT = 0
    
    # Проверяем количество существующих мероприятий
    if await db.get_events_count() == NO_EVENTS_COUNT:
        await message.answer("Нет мероприятий на которые можно записаться!")
        
    else:
        
        await message.answer("Выберите интересующее вас мероприятие!",
                             reply_markup=await kb.get_events_names_buttons())


@user.message(F.text == "👈Назад")
async def btn_back_click(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Открываю меню", reply_markup=await kb.get_start_menu(RIGHTS="user"))


# Обработка нажатий кнопок с названием мероприятий
@user.message(EventCheck())
async def btn_event_name_click(message: Message, state: FSMContext):
    
    await state.set_state(EventSignUp.event_name)
    await state.update_data(event_name=message.text)
    await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")
    
    EVENT_NAME = message.text
    EVENT_INFO = await db.get_event_info_by_name(NAME=EVENT_NAME)
    IS_SIGNUP_OPEN = await db.check_is_signup_open(EVENT_NAME=EVENT_NAME)
    CHAT_ID = message.from_user.id
    EVENT_DATE_AND_TIME = EVENT_INFO.date_and_time
    EVENT_DESC = EVENT_INFO.description
    
    message_for_user = (f"🎉Название мероприятия: {EVENT_NAME}"
              f"\n📆Дата и время проведения: {EVENT_DATE_AND_TIME}"
              f"\n🎊Описание: {EVENT_DESC}"
              f"\n✏️Запись: {"открыта" if IS_SIGNUP_OPEN is not EMPTY else "закрыта"}")
    
    # Проверяем записан-ли пользователь на мероприятия
    if await db.check_signup(EVENT_NAME=EVENT_NAME, CHAT_ID=CHAT_ID) is EMPTY:
        
        await message.answer(message_for_user,
                             reply_markup= await kb.get_event_menu(RIGHTS="user", 
                             EVENT_STATUS=f"{"unsigned" if IS_SIGNUP_OPEN is not EMPTY else ""}"))
        
    else:
        
        SIGNUP_USER_FULL_INFO = await db.get_signup_user_full_info(
                                                                    EVENT_NAME=EVENT_NAME, 
                                                                    CHAT_ID=CHAT_ID
                                                                    )
        
        SIGNUP_USER_FULL_NAME = SIGNUP_USER_FULL_INFO.full_name
        SIGNUP_USER_PHONE = SIGNUP_USER_FULL_INFO.phone
        
        message_for_user += (f"\n📁Ваши данные :\n👤Ф.И: {SIGNUP_USER_FULL_NAME}"
                    f"\n📞Телефон: {SIGNUP_USER_PHONE}")
        
        # Проверяем отменил-ли пользователь запись
        if await db.check_go_to_event(EVENT_NAME=EVENT_NAME, CHAT_ID=CHAT_ID) is not EMPTY:
            
            message_for_user += f" \n🛎Статус : пойду"
            
            await message.answer(message_for_user, reply_markup=await kb.get_event_menu(RIGHTS="user", EVENT_STATUS="signed"))
            
        else:
            
            message_for_user += f"\n🛎Статус : не пойду"
            
            await message.answer(message_for_user, reply_markup=await kb.get_event_menu(RIGHTS="user"))


@user.message(F.text == "❌Я не приду", EventSignUp.event_name)
async def btn_cancel_signup_click(message: Message, state: FSMContext):
    
    STATE_DATA: dict = await state.get_data()
    EVENT_NAME: str = STATE_DATA.get("event_name")
    CHAT_ID = message.from_user.id
    
    if await db.check_signup(EVENT_NAME=EVENT_NAME, CHAT_ID=CHAT_ID) is EMPTY:
        await message.answer("Для начала запишитесь на мероприятие!")
        
    else:
        
        if await db.check_go_to_event(EVENT_NAME=EVENT_NAME, CHAT_ID=CHAT_ID) is not EMPTY:
            
            await state.update_data(id=CHAT_ID)
            
            await message.answer("Вы точно не пойдёте на мероприятие?"
                                 "\nПримечание: после подтверждения вы больше не сможете"
                                 "записаться на это мероприятие!", 
                                 reply_markup=await kb.get_confirm_menu(CALLBACK="cofirm_dont_go_to_event"))
            
        else:
            await message.answer("Вы уже отменили запись!")


# Обработаем нажатие кнопок для отмены записи на мероприятие
@user.callback_query(EventSignUp.event_name)
async def confirm_cancel_signup_callback(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.delete() 
    
    if callback.data == "cofirm_dont_go_to_event": 
        
        STATE_DATA: dict = await state.get_data()
        EVENT_NAME: str = STATE_DATA.get("event_name")
        CHAT_ID: str = STATE_DATA.get("id")
        
        await db.change_signup_status(EVENT_NAME=EVENT_NAME, CHAT_ID=CHAT_ID)
        await callback.message.answer("Вы успешно отменили запись!", reply_markup=await kb.get_events_names_buttons())
        await state.clear()
        
    else:
        
        await callback.message.answer("Отменяю действие!", 
                                      reply_markup=await kb.get_event_menu(RIGHTS="user", EVENT_STATUS="signed"))

# Обработаем кнопку выхода из мероприятия
@user.message(F.text == "🔙Назад")
async def btn_exit_from_events_click(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Перехожу назад", reply_markup=await kb.get_events_names_buttons())


@user.message(F.text == "📝Записаться", EventSignUp.event_name)
async def btn_signup_click(message: Message, state: FSMContext):
    
    STATE_DATA: dict = await state.get_data()
    EVENT_NAME: str = STATE_DATA.get("event_name")
    
    # Проверка открыта-ли запись
    if await db.check_is_signup_open(EVENT_NAME=EVENT_NAME) is not EMPTY:
        
        CHAT_ID = message.from_user.id
        
        # Проверка записи на мерпориятие
        if await db.check_signup(EVENT_NAME=EVENT_NAME, CHAT_ID=CHAT_ID) is EMPTY:
            
            await message.answer("Введите фамилию и имя!\nПример : Иванов Иван", 
                                 reply_markup=await kb.get_user_cancel_button())
            
            await state.set_state(EventSignUp.full_name)
            
        else:
            await message.answer("Вы уже записались на это мерпориятие!")
            
    else:
        await message.answer("Запись на мероприятие уже закрыта!")


@user.message(EventSignUp.full_name)
async def wait_full_name(message: Message, state: FSMContext):
    
    FULL_NAME = message.text
    FULL_NAME_REGEXP = "^[а-яёА-ЯЁ]{3,25}? [а-яёА-ЯЁ]{3,25}?$"
    
    if FULL_NAME is not EMPTY and search(compile(FULL_NAME_REGEXP), FULL_NAME):
        
        await state.update_data(full_name=FULL_NAME)
        
        await message.answer("Поделитесь своим номером телефона, нажав на кнопку '📞Отправить' ",
                             reply_markup=await kb.get_user_cancel_button(addition="phone"))
        
        await state.set_state(EventSignUp.phone)
        
    else:
        await message.answer("Некорректные ф.и!\nПопробуйте ещё раз!")


@user.message(EventSignUp.phone)
async def wait_phone(message: Message, state: FSMContext):
    
    PHONE_REQUEST = message.contact
    
    if PHONE_REQUEST is not EMPTY:
        
        USER_PHONE = PHONE_REQUEST.phone_number
        
        await state.update_data(phone=USER_PHONE)
        await state.update_data(id=message.from_user.id)
        
        STATE_DATA: dict = await state.get_data()
        EVENT_NAME: str = STATE_DATA.get("event_name")
        FULL_NAME: str = STATE_DATA.get("full_name")
        
        await message.answer(f"Подтвердите запись на мероприятие!"
                             f"\n🎉Название мероприятия : {EVENT_NAME}"
                             f"\n📒Ваши данные : "
                             f"\n👤Ф.И : {FULL_NAME}"
                             f"\n📞Номер телефона : {USER_PHONE}",
                             reply_markup=await kb.get_confirm_menu(CALLBACK="confirm_signup"))
        
        await state.set_state(EventSignUp.confirm)
        
    else:
        
        await message.answer("Некорректный номер телефона!\nПопробуйте ещё раз!",
                             reply_markup=await kb.get_user_cancel_button(addition="phone"))


# Обработаем кнопку для подтверждения/отмены удаления мероприятия
@user.callback_query(EventSignUp.confirm)
async def confirm_signup_callback(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.delete()
    
    if callback.data == "confirm_signup":
        
        STATE_DATA: dict = await state.get_data()
        EVENT_NAME: str = STATE_DATA.get("event_name")
        USER_FULL_NAME: str = STATE_DATA.get("full_name")
        USER_PHONE: str = STATE_DATA.get("phone")
        USER_CHAT_ID: str = STATE_DATA.get("id")
        
        await db.add_signup_user(EVENT_NAME=EVENT_NAME, FULL_NAME=USER_FULL_NAME, PHONE=USER_PHONE, CHAT_ID=USER_CHAT_ID)
        await callback.message.answer("Вы успешно записались!", reply_markup=await kb.get_events_names_buttons())
        await state.clear()
        
    else:
        
        await callback.message.answer("Отменяю запись!\nВведите фамилию и имя!",
                                      reply_markup=await kb.get_user_cancel_button())
        
        await state.set_state(EventSignUp.full_name)