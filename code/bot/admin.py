import os

import bot.keyboards as kb
import pandas as pd
import bot.config as cfg
import database.requests as db
import bot.notification as  notify

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from re import search, compile


EMPTY = None


# Чтобы не писать dispatcher 2-й раз заменим его на роутер
admin = Router()


# Создаём класс (фильтр) для проверки админа
class AdminProtect(Filter):
    async def __call__(self, message: Message):
        return await db.check_admin(chat_id=message.from_user.id)


# Создаём класс (фильтр) для проверки мероприятий
class EventCheck(Filter):
    async def __call__(self, message: Message):
        return await db.check_event_by_name(NAME=message.text)


# Создаём класс (состояние) для рассылки
class Mailing(StatesGroup):
    message = State()
    photo = State()
    confirm = State()


class BanUser(StatesGroup):
    id = State()


class UnbanUser(StatesGroup):
    id = State()


class AddAdmin(StatesGroup):
    id = State()


class DelAdmin(StatesGroup):
    id = State()


class AddEvent(StatesGroup):
    name = State()
    date_and_time = State()
    description = State()
    confirm = State()


class DelEvent(StatesGroup):
    id = State()
    confirm = State()


class EventChoice(StatesGroup):
    event_name = State()


@admin.message(AdminProtect(), CommandStart())
async def start_command(message: Message):
    await message.answer_sticker("CAACAgIAAxkBAAEFm5ZmTgIqpv3A8pzMD_lR3EsFPA0u8gACXAwAAj0zCEiRSKTz6TfmmDUE")
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}!", reply_markup=await kb.get_start_menu(RIGHTS="admin"))


@admin.message(AdminProtect(), F.text == "⚙️Админ панель")
async def btn_ADMIN_PANEL_click(message: Message):
    await message.answer("Открываю админ.панель", reply_markup=kb.ADMIN_PANEL)


@admin.message(AdminProtect(), F.text == "🤖Назад")
async def btn_back_to_start_menu_click(message: Message):
    await message.answer("Открываю меню", reply_markup=await kb.get_start_menu(RIGHTS="admin"))


@admin.message(AdminProtect(), F.text == "🚫Забанить пользователя")
async def btn_ban_user_click(message: Message, state: FSMContext):
    await message.answer("Отправьте айди пользователя...", reply_markup=kb.ADMIN_CANCEL_MARKUP)
    await state.set_state(BanUser.id)


@admin.message(F.text == "❌Отмена")
async def btn_cancel_action_click(message: Message, state: FSMContext):
    await message.answer("Отменяю действие", reply_markup=kb.ADMIN_PANEL)
    await state.clear()


@admin.message(BanUser.id)
async def wait_id_to_ban_user(message: Message, state: FSMContext):
    
    chat_id = message.text
    
    # Проверяем сообщение на корректность
    if chat_id is not EMPTY and chat_id.isdigit():
        
        await state.clear()
        
        chat_id = int(message.text)
        
        if await db.check_ban(CHAT_ID=chat_id):
            await message.answer("Пользователь уже находиться в бане!", reply_markup=kb.ADMIN_PANEL)
            
        elif await db.check_admin(chat_id=chat_id):
            await message.answer("Нельзя забанить администратора!", reply_markup=kb.ADMIN_PANEL)
            
        else:
            
            await db.add_in_ban(CHAT_ID=chat_id)
            await message.answer("Пользователь забанен!", reply_markup=kb.ADMIN_PANEL)
            
    else:
        await message.answer("Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(AdminProtect(), F.text == "✅Разбанить пользователя")
async def btn_unban_user_click(message: Message, state: FSMContext):
    await message.answer("Отправьте айди пользователя...", reply_markup=kb.ADMIN_CANCEL_MARKUP)
    await state.set_state(UnbanUser.id)


@admin.message(UnbanUser.id)
async def wait_id_to_unban_user(message: Message, state: FSMContext):
    
    chat_id = message.text
    
    if chat_id is not EMPTY and chat_id.isdigit():
        
        await state.clear()
        
        chat_id = int(message.text)
        
        if await db.check_ban(CHAT_ID=chat_id):
            
            await db.del_from_ban(CHAT_ID=chat_id)
            await message.answer("Пользователь разбанен!", reply_markup=kb.ADMIN_PANEL)
            
        else:
            await message.answer("Пользователь никогда не был забанен!", reply_markup=kb.ADMIN_PANEL)
            
    else:
        await message.answer("Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(AdminProtect(), F.text == "➕Добавить админа")
async def btn_add_adm_click(message: Message, state: FSMContext):
    await message.answer("Отправьте айди пользователя...", reply_markup=kb.ADMIN_CANCEL_MARKUP)
    await state.set_state(AddAdmin.id)


@admin.message(AddAdmin.id)
async def wait_chat_id_to_add_admin(message: Message, state: FSMContext):
    
    chat_id = message.text
    
    if chat_id is not EMPTY and chat_id.isdigit():
        
        await state.clear()
        
        chat_id = int(message.text)
        
        if await db.check_admin(chat_id=chat_id):
            await message.answer("Пользователь уже является админом!", reply_markup=kb.ADMIN_PANEL)
            
        else:
            
            await db.add_in_admin(CHAT_ID=chat_id)
            await message.answer("Администратор добавлен!", reply_markup=kb.ADMIN_PANEL)
            
    else:
        await message.answer("Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(AdminProtect(), F.text == "➖Удалить админа")
async def btn_del_adm_click(message: Message, state: FSMContext):
   await message.answer("Отправьте айди пользователя...", reply_markup=kb.ADMIN_CANCEL_MARKUP)
   await state.set_state(DelAdmin.id)

  
@admin.message(DelAdmin.id)
async def wait_chat_id_to_del_admin(message: Message, state: FSMContext):
    
    chat_id = message.text
    
    if chat_id is not EMPTY and chat_id.isdigit():
        
        await state.clear()
        
        chat_id = int(message.text)
        
        if await db.check_admin(chat_id=chat_id):
            
            await db.del_from_admin(CHAT_ID=chat_id)
            await message.answer("Администратор удалён!", reply_markup=kb.ADMIN_PANEL)
            
        else:
            await message.answer("Такого администратора не существует!", reply_markup=kb.ADMIN_PANEL)
            
    else:
        await message.answer("Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(AdminProtect(), F.text == "🗣️Сделать рассылку")
async def btn_mailing_click(message: Message, state: FSMContext):
    await state.set_state(Mailing.message)
    await message.answer("Отправьте сообщение для рассылки...", reply_markup=kb.ADMIN_CANCEL_MARKUP)


@admin.message(Mailing.message)
async def wait_mailing_message(message: Message, state: FSMContext):
    
    MAILING_MESSAGE = message.text
    
    if MAILING_MESSAGE is not EMPTY:
        
        # Сохраняем сообщение и просим подтвердить рассылку
        await state.update_data(message=MAILING_MESSAGE)
        
        await message.answer("Хотите добавить фоотграфию к рассылке?"
                             "\nЕсли да, то прикрепите её url-адресс."
                             "\nВ противном случае отправьте знак '-' следующим сообщением без кавычек",
                             reply_markup=kb.ADMIN_CANCEL_MARKUP)
        
        await state.set_state(Mailing.photo)
        
    else:
        await message.answer("Некорректное сообщение для рассылки!\nПопробуйте ещё раз!")


@admin.message(Mailing.photo)
async def wait_mailing_photo(message: Message, state: FSMContext):
    
    STATE_DATA: dict = await state.get_data()
    MAILING_MESSAGE: str = STATE_DATA.get("message")
    PHOTO_URL = message.text
    NO_PHOTO_URL = "-"
    URL_REGEXP = "^(https|http)://.+/impg/.+$"
    
    if PHOTO_URL is not EMPTY:
        
        if PHOTO_URL == NO_PHOTO_URL:
            
            await message.answer(f"Подтвердите рассылку!\n\n{MAILING_MESSAGE}", 
                                 reply_markup=await kb.get_confirm_menu(CALLBACK="confirm_mailing"))
            
            await state.set_state(Mailing.confirm)
        
        elif search(compile(URL_REGEXP), PHOTO_URL): 
            
            await state.update_data(photo=PHOTO_URL) 
            
            await message.answer_photo(f"{PHOTO_URL}", caption=f"Подтвердите рассылку!\n\n{MAILING_MESSAGE}", 
                                       reply_markup=await kb.get_confirm_menu(CALLBACK="confirm_mailing"))
            
            await state.set_state(Mailing.confirm)
        
        else:
            await message.answer("Некорректный url адрес фотографии!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            
    else:
        await message.answer("Некорректное сообщение!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)


# Обработаем кнопку для подтверждения/отмены рассылки 
@admin.callback_query(Mailing.confirm)
async def confirm_mailing_callback(callback: CallbackQuery, state: FSMContext):
   
   await callback.message.delete()
   
   if callback.data == "confirm_mailing":
        
        MAILING_USERS = await db.get_mailing_users()
        STATE_DATA: dict = await state.get_data()
        MESSAGE: str = STATE_DATA.get("message")
        PHOTO_URL: str = STATE_DATA.get("photo")
        
        for mailing_user in MAILING_USERS:
            
            try:
                
                if PHOTO_URL is EMPTY:
                    await cfg.BOT.send_message(chat_id=mailing_user.chat_id, text=MESSAGE)
                    
                else:
                    await cfg.BOT.send_photo(chat_id=mailing_user.chat_id, photo=PHOTO_URL, caption=MESSAGE)
                    
            except:
                
                # удаляем человека из рассылки, поскольку он заблокировал бота
                await db.del_from_mailing(chat_id=mailing_user.chat_id)
                
        await callback.message.answer("Рассылка завершена!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()
        
   else:
        
        await callback.message.answer("Отменяю рассылку!\nВведите новое сообщение!",
                                      reply_markup=kb.ADMIN_CANCEL_MARKUP)
        
        await state.set_state(Mailing.message)


@admin.message(AdminProtect(), F.text == "🎇Создать мероприятие")
async def btn_create_event_click(message: Message, state: FSMContext):
    await state.set_state(AddEvent.name)
    await message.answer("Отправьте название!", reply_markup=kb.ADMIN_CANCEL_MARKUP)


@admin.message(AddEvent.name)
async def waiting_event_name(message: Message, state: FSMContext):
    
    EVENT_NAME = message.text
    
    if EVENT_NAME is not EMPTY:
        
        if await db.check_event_by_name(NAME=EVENT_NAME) is EMPTY:
            
            await state.update_data(name=EVENT_NAME)
            
            await message.answer("Введите дату и время мероприятия!"
                                 "\nПример: 12.02.2024 15:00", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            
            await state.set_state(AddEvent.date_and_time)
            
        else:
            
            await message.answer("Мероприятие с таким названием уже существует!", reply_markup=kb.ADMIN_PANEL)
            await state.clear()
            
    else:
        await message.answer("Некорректное название!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)


@admin.message(AddEvent.date_and_time)
async def waiting_date_of_event(message: Message, state: FSMContext):
    
    # Шаблон для даты дд.мм.гггг чч.мм
    DATE_REGEXP = "^(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).20([2][4]|[2-9][0-9]) ([0-1][0-9]|[2][0-3]):[0-5][0-9]$"
    DATE_AND_TIME = message.text
    
    if DATE_AND_TIME is not EMPTY and search(compile(DATE_REGEXP), DATE_AND_TIME) : 
        
        last_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        DATE = DATE_AND_TIME.split()[0]
        DAY = int(DATE[:2])
        MONTH = int(DATE[3:5])
        YEAR = int(DATE[6:])
        LAST_FEBRUARY_DAY_IN_LEAP_YEAR = 29
        
        # Проверка года на високосность
        if (YEAR % 4 == 0 and YEAR % 100 != 0 or YEAR % 400 == 0):
            last_days_in_month[1] = LAST_FEBRUARY_DAY_IN_LEAP_YEAR 
        
        LAST_DAY_IN_USER_MONTH =  last_days_in_month[MONTH-1]
         
        # Проверяем введённую дату на корректность    
        if (DAY <= LAST_DAY_IN_USER_MONTH):
            
            await state.update_data(date_and_time=DATE_AND_TIME)
            await message.answer("Введите описание мероприятия!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            await state.set_state(AddEvent.description)
            
        else:
            await message.answer("Некорректная дата!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            
    else:
        await message.answer("Некорректная дата и время!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)


@admin.message(AddEvent.description)
async def waiting_event_desc(message: Message, state: FSMContext):
    
    DESCRIPTION = message.text
    
    if DESCRIPTION is not EMPTY:
        
        STATE_DATA: dict = await state.get_data()
        NAME: str = STATE_DATA.get("name")
        DATE_AND_TIME: str = STATE_DATA.get("date_and_time")
        
        await state.update_data(description=DESCRIPTION)   
        
        await message.answer(f"Подтвердите создание мероприятия!"
                             f"\nНазвание : {NAME}"
                             f"\nДата и время: {DATE_AND_TIME}"
                             f"\nОписание : {DESCRIPTION}",
                             reply_markup=await kb.get_confirm_menu(CALLBACK="confirm_add_event"))
        
        await state.set_state(AddEvent.confirm)
        
    else:
        await message.answer("Некорректное описание!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)


# Обработаем нажатие на кнопку для подтверждения/отмены создания мероприятия
@admin.callback_query(AddEvent.confirm)
async def confirm_create_event_callback(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.delete()
    
    if callback.data == "confirm_add_event":
        
        STATE_DATA: dict = await state.get_data()
        NAME: str = STATE_DATA.get("name")
        DATE_AND_TIME: str = STATE_DATA.get("date_and_time")
        DESCRIPTION: str = STATE_DATA.get("description")
        
        await db.add_event(NAME=NAME, DESCRIPTION=DESCRIPTION, DATE_AND_TIME=DATE_AND_TIME)
        
        notify.schedule_notifications(event_time=DATE_AND_TIME, EVENT_NAME=NAME)
        
        await callback.message.answer("Мероприятие добавлено!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()
        
    else:
        
        await callback.message.answer("Отменяю создание!\nВведите название мероприятия!",
                                      reply_markup=kb.ADMIN_CANCEL_MARKUP)
        
        await state.set_state(AddEvent.name)


@admin.message(AdminProtect(), F.text == "🎆Удалить мероприятие")
async def btn_delete_event_click(message: Message, state: FSMContext):
    
    NO_EVENTS = 0
    
    if await db.get_events_count() is not NO_EVENTS:
        
        events_enumerate: str = ""
        
        for event in await db.get_events():
            events_enumerate += f"{event.id}. {event.name}\n"
        
        await message.answer(f"Отправьте номер мероприятия!\n{events_enumerate}", 
                             reply_markup=kb.ADMIN_CANCEL_MARKUP)
        
        await state.set_state(DelEvent.id)
        
    else:
        await message.answer("Нет мероприятий,которые можно удалить!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()


@admin.message(DelEvent.id)
async def waiting_event_id(message: Message, state: FSMContext):
    
    event_id = message.text
    
    if event_id is not EMPTY and event_id.isdigit():
        
        event_id = int(event_id)
        
        if await db.check_event_by_id(ID=event_id):
            
            await state.update_data(id=event_id)
            
            await message.answer(f"Подтвердите удаление мероприятия!\n{event_id}. "
                                 f"{(await db.get_event_name_by_id(ID=event_id)).name}", 
                                 reply_markup=await kb.get_confirm_menu(CALLBACK="confirm_del_event"))
            
            await state.set_state(DelEvent.confirm)
        else:
            await message.answer("Мероприятия с таким номером не существует!", reply_markup=kb.ADMIN_PANEL)
            await state.clear()
    else:
        await message.answer("Некорректный номер!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)


@admin.callback_query(DelEvent.confirm)
async def confirm_del_event_callback(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.delete()
    
    if callback.data == "confirm_del_event":
        
        STATE_DATA: dict = await state.get_data()
        event_id: str = STATE_DATA.get("id")
        event_id: int = int(event_id)
        
        await db.delete_event(ID=event_id)
        await callback.message.answer("Мероприятие удалено!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()
        
    else:
        
        await callback.message.answer("Отменяю удаление!\nВведите другой порядковый номер!",
                                      reply_markup=kb.ADMIN_CANCEL_MARKUP)
        
        await state.set_state(DelEvent.id)


@admin.message(AdminProtect(), F.text == "👈Назад")
async def btn_back_click(message: Message, state: FSMContext):
    await message.answer("Открываю меню", reply_markup=await kb.get_start_menu(RIGHTS="admin"))
    await state.clear()


# Обработаем нажатие по одному из мероприятий
@admin.message(AdminProtect(), EventCheck())
async def btn_event_name_click(message: Message, state: FSMContext):
    
    EVENT_NAME = message.text
    EVENT_INFO = await db.get_event_info_by_name(NAME=EVENT_NAME)
    EVENT_DESCRIPTION = EVENT_INFO.description
    EVENT_DATE_AND_TIME = EVENT_INFO.date_and_time
    
    await state.update_data(event_name=EVENT_NAME)
    await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")
    
    await message.answer(f"🎉Название мероприятия : {EVENT_NAME}"
                         f"\n📆Дата и время проведения: {EVENT_DATE_AND_TIME}"
                         f"\n🎊Описание: {EVENT_DESCRIPTION} "
                         f"\n✏️Запись: {"открыта" if await db.check_is_signup_open(EVENT_NAME=EVENT_NAME) is not EMPTY else "закрыта"}", 
                         reply_markup=await kb.get_event_menu(RIGHTS="admin"))
    
    await state.set_state(EventChoice.event_name)


@admin.message(AdminProtect(), EventChoice.event_name, F.text == "❌Закрыть запись")
async def btn_close_event_signup(message: Message, state: FSMContext):
    
    STATE_DATA: dict = await state.get_data()
    EVENT_NAME: str = STATE_DATA.get("event_name")
    
    if await db.check_is_signup_open(EVENT_NAME=EVENT_NAME) is not EMPTY:
        
        await message.answer(f"Подтвердите закрытие записи на мероприятие: {EVENT_NAME}\nУчтите, что" 
                             " в дальнейшем будет невозможно открыть запись!", 
                             reply_markup=await kb.get_confirm_menu(CALLBACK="confirm_close_event"))
        
    else:
        await message.answer("Мероприятие уже закрыто!")


@admin.callback_query(EventChoice.event_name)
async def confirm_close_event_callback(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.delete()
    
    if callback.data == "confirm_close_event":
        
        STATE_DATA: dict = await state.get_data()
        EVENT_NAME: str = STATE_DATA.get("event_name")
        
        await db.close_event_signup(NAME=EVENT_NAME)
        await callback.message.answer("Запись закрыта!", reply_markup=await kb.get_event_menu(RIGHTS="admin"))
        
    else:
        await callback.message.answer("Отменяю закрытие!", reply_markup=await kb.get_event_menu(RIGHTS="admin"))


@admin.message(AdminProtect(), EventChoice.event_name, F.text == "👥Записавшиеся")
async def btn_signup_click(message: Message, state: FSMContext):
    
    STATE_DATA: dict = await state.get_data()
    EVENT_NAME: str = STATE_DATA.get("event_name")
    NO_ONE_SIGNUP = 0
    
    if await db.get_signup_count(EVENT_NAME=EVENT_NAME) == NO_ONE_SIGNUP:
        await message.answer("На мероприятие никто не записался!")
        
    else:
        
        # Приводим данные в объект класса DataFrame 
        table = pd.DataFrame(await db.get_signup_people(EVENT_NAME=EVENT_NAME))
        
        # Создаём excel файл с нашими данными в текущей папке проекта
        table.to_excel(f"{EVENT_NAME}.xlsx", sheet_name="Записавшиеся",index=False)
        
        # Отправляем файл с данными        
        await message.answer_document(document=FSInputFile(path=os.path.join(os.getcwd(), f"{EVENT_NAME}.xlsx")))
        
        # Удаляем файл из текущей директории
        os.remove(os.path.join(os.getcwd(), f"{EVENT_NAME}.xlsx"))       