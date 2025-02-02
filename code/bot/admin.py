import os

import bot.keyboards as kb
import pandas as pd
import bot.config as cfg

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.requests import (check_ban, check_event_by_name, get_users_from_mailing, check_admin, add_in_ban,
                               del_from_ban, add_in_admin, del_from_admin, add_event, get_events,
                               check_event_by_id, get_event_name_by_id, delete_event, get_signup_count, 
                               del_from_mailing, get_event_info_by_name, get_signup_people,
                               check_is_signup_open, close_event_signup, get_events_count)
from re import search, compile


# Чтобы не писать dispatcher 2-й раз заменим его на роутер
admin = Router()


# Создаём класс (фильтр) для проверки админа
class AdminProtect(Filter):
    async def __call__(self, message: Message):
        return await check_admin(chat_id=message.from_user.id)

# Создаём класс (фильтр) для проверки мероприятий
class EventCheck(Filter):
    async def __call__(self, message: Message):
        return await check_event_by_name(event_name=message.text)

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
    date = State()
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
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}!", reply_markup=await kb.get_start_menu(rights="admin"))

@admin.message(AdminProtect(), F.text == "⚙️Админ панель")
async def btn_ADMIN_PANEL_click(message: Message):
    await message.answer("Открываю админ.панель", reply_markup=kb.ADMIN_PANEL)

@admin.message(AdminProtect(), F.text == "🤖Назад")
async def btn_back_to_start_menu_click(message: Message):
    await message.answer("Открываю меню", reply_markup=await kb.get_start_menu(rights="admin"))

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
    # Проверяем сообщение на корректность
    if message.text is not None and message.text.isdigit():
        await state.clear()
        chat_id = int(message.text)
        if await check_ban(chat_id=chat_id):
            await message.answer("Пользователь уже находиться в бане!", reply_markup=kb.ADMIN_PANEL)
        elif await check_admin(chat_id=chat_id):
            await message.answer("Нельзя забанить администратора!", reply_markup=kb.ADMIN_PANEL)
        else:
            await add_in_ban(chat_id=chat_id)
            await message.answer("Пользователь забанен!", reply_markup=kb.ADMIN_PANEL)
    else:
        await message.answer("Некорректное айди пользователя!\nПопробуйте ещё раз!")

@admin.message(AdminProtect(), F.text == "✅Разбанить пользователя")
async def btn_unban_user_click(message: Message, state: FSMContext):
    await message.answer("Отправьте айди пользователя...", reply_markup=kb.ADMIN_CANCEL_MARKUP)
    await state.set_state(UnbanUser.id)

@admin.message(UnbanUser.id)
async def wait_id_to_unban(message: Message, state: FSMContext):
    if message.text is not None and message.text.isdigit():
        await state.clear()
        chat_id = int(message.text)
        if await check_ban(chat_id=chat_id):
            await del_from_ban(chat_id=chat_id)
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
async def wait_id_to_add_admin(message: Message, state: FSMContext):
    if message.text is not None and message.text.isdigit():
        await state.clear()
        chat_id = int(message.text)
        if await check_admin(chat_id=chat_id):
            await message.answer("Пользователь уже является админом!", reply_markup=kb.ADMIN_PANEL)
        else:
            await add_in_admin(chat_id=chat_id)
            await message.answer("Администратор добавлен!", reply_markup=kb.ADMIN_PANEL)
    else:
        await message.answer("Некорректное айди пользователя!\nПопробуйте ещё раз!")

@admin.message(AdminProtect(), F.text == "➖Удалить админа")
async def btn_del_adm_click(message: Message, state: FSMContext):
   await message.answer("Отправьте айди пользователя...", reply_markup=kb.ADMIN_CANCEL_MARKUP)
   await state.set_state(DelAdmin.id)
  
@admin.message(DelAdmin.id)
async def wait_id_to_del_admin(message: Message, state: FSMContext):
    if message.text is not None and message.text.isdigit():
        await state.clear()
        chat_id = int(message.text)
        if await check_admin(chat_id=chat_id):
            await del_from_admin(chat_id=chat_id)
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
    if message.text is not None:
        # Сохраняем сообщение и просим подтвердить рассылку
        await state.update_data(message=message.text)
        await message.answer("Хотите добавить фоотграфию к рассылке?"
                             "\nЕсли да, то прикрепите её url-адресс."
                             "\nВ противном случае отправьте знак '-' следующим сообщением без кавычек",
                             reply_markup=kb.ADMIN_CANCEL_MARKUP)
        await state.set_state(Mailing.photo)
    else:
        await message.answer("Некорректное сообщение для рассылки!\nПопробуйте ещё раз!")

@admin.message(Mailing.photo)
async def wait_mailing_photo(message: Message, state: FSMContext):
    data_from_state: dict = await state.get_data()
    message_from_admin: str = data_from_state.get("message")
    url_of_photo = message.text
    if url_of_photo is not None:
        if url_of_photo == "-":
            await message.answer(f"Подтвердите рассылку!\n\n{message_from_admin}", 
                                 reply_markup=await kb.get_confirm_menu(callback="confirm_mailing"))
            await state.set_state(Mailing.confirm)
        elif search(compile("^(https|http)://.+/impg/.+$"), url_of_photo): 
            await state.update_data(photo=url_of_photo) 
            await message.answer_photo(f"{url_of_photo}", caption=f"Подтвердите рассылку!\n\n{message_from_admin}", 
                                       reply_markup=await kb.get_confirm_menu(callback="confirm_mailing"))
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
        # Получаем список пользователей
        users = await get_users_from_mailing()
        # Получаем сообщение админа
        data_from_state: dict = await state.get_data()
        message_from_admin: str = data_from_state.get("message")
        photo_from_admin: str = data_from_state.get("photo")
        for user in users:
            try:
                if photo_from_admin is None:
                    await cfg.BOT.send_message(chat_id=user.chat_id, text=message_from_admin)
                else:
                    await cfg.BOT.send_photo(chat_id=user.chat_id, photo=photo_from_admin, caption=message_from_admin)
            except:
                # удаляем человека из рассылки, поскольку он заблокировал бота
                await del_from_mailing(chat_id=user)
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
    event_name = message.text
    if event_name is not None:
        if await check_event_by_name(event_name=event_name) is None:
            await state.update_data(name=event_name)
            await message.answer("Введите дату и время мероприятия!\nПример: 12.02.2024 15:00", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            await state.set_state(AddEvent.date)
        else:
            await message.answer("Мероприятие с таким названием уже существует!", reply_markup=kb.ADMIN_PANEL)
            await state.clear()
    else:
        await message.answer("Некорректное название!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)

@admin.message(AddEvent.date)
async def waiting_date_of_event(message: Message, state: FSMContext):
    # Проверка на соответствие сообщения шаблону дд.мм.гггг чч.мм
    reg_exp = "^(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).20([2][4]|[2-9][0-9]) ([0-1][0-9]|[2][0-3]):[0-5][0-9]$"
    date = message.text
    if date is not None and search(compile(reg_exp), date) : 
        last_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        data_from_admin = date.split()[0]
        day = int(data_from_admin[:2])
        month = int(data_from_admin[3:5])
        year = int(data_from_admin[6:])
        # Проверка года на високосность
        if (year % 4 == 0 and year % 100 != 0 or year % 400 == 0):
            last_days_in_month[1] = 29            
        # Проверяем введённую дату на корректность    
        if (day <= last_days_in_month[month-1]):
            await state.update_data(date=date)
            await message.answer("Введите описание мероприятия!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            await state.set_state(AddEvent.description)
        else:
            await message.answer("Некорректная дата!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
    else:
        await message.answer("Некорректная дата и время!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)

@admin.message(AddEvent.description)
async def waiting_event_disc(message: Message, state: FSMContext):
    description = message.text
    if description is not None:
        data_from_state: dict = await state.get_data()
        event_name: str = data_from_state.get("name")
        event_date: str = data_from_state.get("date")
        await state.update_data(description=description)   
        await message.answer(f"Подтвердите создание мероприятия!"
                             f"\nНазвание : {event_name}"
                             f"\nДата и время: {event_date}"
                             f"\nОписание : {description}",
                             reply_markup=await kb.get_confirm_menu(callback="confirm_add_event"))
        await state.set_state(AddEvent.confirm)
    else:
        await message.answer("Некорректное описание!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_CANCEL_MARKUP)

# Обработаем нажатие на кнопку для подтверждения/отмены создания мероприятия
@admin.callback_query(AddEvent.confirm)
async def confirm_create_event_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == "confirm_add_event":
        data_from_state: dict = await state.get_data()
        event_name: str = data_from_state.get("name")
        event_date: str = data_from_state.get("date")
        event_description: str = data_from_state.get("description")
        await add_event(event_name=event_name, event_description=event_description, event_date=event_date)
        await callback.message.answer("Мероприятие добавлено!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()
    else:
        await callback.message.answer("Отменяю создание!\nВведите название мероприятия!",
                                      reply_markup=kb.ADMIN_CANCEL_MARKUP)
        await state.set_state(AddEvent.name)

@admin.message(AdminProtect(), F.text == "🎆Удалить мероприятие")
async def btn_delete_event_click(message: Message, state: FSMContext):
    if await get_events_count() > 0:
        events_enumerate: str = ""
        for event in await get_events():
            events_enumerate += f"{event.id}. {event.name}\n"
        await message.answer(f"Отправьте номер мероприятия!\n{events_enumerate}", reply_markup=kb.ADMIN_CANCEL_MARKUP)
        await state.set_state(DelEvent.id)
    else:
        await message.answer("Нет мероприятий,которые можно удалить!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()

@admin.message(DelEvent.id)
async def waiting_id_of_event(message: Message, state: FSMContext):
    event_id = message.text
    if event_id is not None and event_id.isdigit():
        if await check_event_by_id(event_id=int(event_id)):
            await state.update_data(id=event_id)
            await message.answer(f"Подтвердите удаление мероприятия!\n{event_id}. "
            f"{(await get_event_name_by_id(event_id=int(event_id))).name}", 
                reply_markup=await kb.get_confirm_menu(callback="confirm_del_event"))
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
        data_from_state: dict = await state.get_data()
        event_id: str = data_from_state.get("id")
        await delete_event(event_id=int(event_id))
        await callback.message.answer("Мероприятие удалено!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()
    else:
        await callback.message.answer("Отменяю удаление!\nВведите другой порядковый номер!",
                                      reply_markup=kb.ADMIN_CANCEL_MARKUP)
        await state.set_state(DelEvent.id)

@admin.message(AdminProtect(), F.text == "👈Назад")
async def btn_back_click(message: Message, state: FSMContext):
    await message.answer("Открываю меню", reply_markup=await kb.get_start_menu(rights="admin"))
    await state.clear()

# Обработаем нажатие по одному из мероприятий
@admin.message(AdminProtect(), EventCheck())
async def btn_event_name_click(message: Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")
    event_info = await get_event_info_by_name(event_name=message.text)
    await message.answer(f"🎉Название мероприятия : {message.text}"
                         f"\n📆Дата и время проведения: {event_info.date}"
                         f"\n🎊Описание: {event_info.description} "
                         f"\n✏️Запись: {"открыта" if await check_is_signup_open(event_name=message.text) is not None else "закрыта"}", 
                         reply_markup=await kb.get_event_menu(rights="admin"))
    await state.set_state(EventChoice.event_name)

@admin.message(AdminProtect(), EventChoice.event_name, F.text == "❌Закрыть запись")
async def btn_close_signup_event(message: Message, state: FSMContext):
    data_from_state: dict = await state.get_data()
    event_name: str = data_from_state.get("event_name")
    if await check_is_signup_open(event_name=event_name) is not None:
        await message.answer(f"Подтвердите закрытие записи на мероприятие: {event_name}\nУчтите, что" 
                             " в дальнейшем будет невозможно открыть запись!", 
                             reply_markup=await kb.get_confirm_menu("confirm_close_event"))
    else:
        await message.answer("Мероприятие уже закрыто!")

@admin.callback_query(EventChoice.event_name)
async def confirm_close_event_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == "confirm_close_event":
        data_from_state: dict = await state.get_data()
        event_name: str = data_from_state.get("event_name")
        await close_event_signup(event_name=event_name)
        await callback.message.answer("Запись закрыта!", reply_markup=await kb.get_event_menu(rights="admin"))
    else:
        await callback.message.answer("Отменяю закрытие!", reply_markup=await kb.get_event_menu(rights="admin"))

@admin.message(AdminProtect(), EventChoice.event_name, F.text == "👥Записавшиеся")
async def btn_signup_click(message: Message, state: FSMContext):
    data_from_state: dict = await state.get_data()
    event_name: str = data_from_state.get("event_name")
    if await get_signup_count(event_name=event_name) == 0:
        await message.answer("На мероприятие никто не записался!")
    else:
        # Приводим данные в объект класса DataFrame 
        table = pd.DataFrame(await get_signup_people(event_name=event_name))
        # Создаём excel файл с нашими данными в текущей папке проекта
        table.to_excel(f"{event_name}.xlsx", sheet_name="Записавшиеся",index=False)
        # Отправляем файл с данными        
        await message.answer_document(document=FSInputFile(path=os.path.join(os.getcwd(), f"{event_name}.xlsx")))
        # Удаляем файл из текущей директории
        os.remove(os.path.join(os.getcwd(), f"{event_name}.xlsx"))       
