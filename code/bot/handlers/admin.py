import os
import bot.keyboards as kb
import pandas as pd
import bot.configs.telegram_bot_config as cfg
import database.requests as db
import bot.services.notification as notify
import bot.utils as utils
import bot.constants.han_admin as const

from datetime import datetime
from re import compile
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.handlers.user import IsEventName
from bot.configs.logger_config import log_admin_action

admin = Router()


class IsAdmin(Filter):
    """
    Фильтр для проверки, является ли пользователь администратором.
    """

    async def __call__(self, message: Message):
        """
        Проверяет, является ли пользователь администратором.

        :param message: Сообщение от пользователя.
        :type message: Message

        :return: True, если пользователь является администратором, иначе False.
        :rtype: bool
        """

        return await db.is_user_admin(chat_id=message.from_user.id)


class IsTextFromQr(Filter):
    """
    Фильтр для проверки текста, полученного от QR-кода.
    """

    async def __call__(self, message: Message):
        """
        Проверяет, является ли текст сообщения действительным QR-кодом.

        :param message: Сообщение от пользователя.
        :type message: Message

        :return: True, если текст является действительным QR-кодом, иначе False.
        :rtype: bool
        """

        event_id, user_id = message.text.split("-")

        return await db.is_qr_text_valid(user_id=user_id, event_id=event_id)


class Mailing(StatesGroup):
    """
    Состояние для рассылки сообщений.
    """
    message = State()  # Сообщение для рассылки
    photo = State()    # Фото для рассылки
    confirm = State()  # Подтверждение рассылки


class AddEvent(StatesGroup):
    """
    Состояние для добавления события.
    """

    name = State()  # Название события
    date_and_time = State()  # Дата и время события
    description = State()  # Описание события
    theme = State()  # Тематика события
    users_limit = State()  # Лимит пользователей
    confirm = State()  # Подтверждение добавления события


class DelEvent(StatesGroup):
    """
    Состояние для удаления события.
    """

    id = State()  # ID события для удаления
    confirm = State()  # Подтверждение удаления события


class CollectFeedback(StatesGroup):
    """
    Состояние для сбора обратной связи.
    """

    event_name = State()  # Название события
    google_link = State()  # Ссылка на Google форму
    confirm = State()  # Подтверждение сбора обратной связи


class Event(StatesGroup):
    """
    Состояние для работы с событиями.
    """

    event_name = State()  # Название события
    mark_by_qr = State()  # Отметка по QR-коду


class BanUser(StatesGroup):
    """
    Состояние для бана пользователя.
    """

    id = State()  # ID пользователя для бана


class UnbanUser(StatesGroup):
    """
    Состояние для разбана пользователя.
    """

    id = State()  # ID пользователя для разбана


class AddAdmin(StatesGroup):
    """
    Состояние для добавления администратора.
    """

    id = State()  # ID пользователя для добавления в администраторы


class DelAdmin(StatesGroup):
    """
    Состояние для удаления администратора.
    """

    id = State()  # ID пользователя для удаления из администраторов


@admin.message(IsAdmin(), CommandStart())
async def start_command(message: Message):
    """
    Обработчик команды /start для администратора.

    :param message: Сообщение от пользователя.
    :type message: Message
    """

    await message.answer_sticker("CAACAgIAAxkBAAEFm5ZmTgIqpv3A8pzMD_lR3EsFPA0u8gACXAwAAj0zCEiRSKTz6TfmmDUE")
    await message.answer(f"👋 Добро пожаловать, {message.from_user.first_name}!", reply_markup=await kb.get_start_menu(rights="admin"))


@admin.message(IsAdmin(), F.text == "⚙️Админ панель")
async def btn_admin_panel_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Админ панель".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await state.clear()
    await message.answer("🔧 Открываю админ.панель", reply_markup=kb.ADMIN_PANEL)


@admin.message(IsAdmin(), F.text == "🤖Назад")
async def btn_back_to_start_menu_click(message: Message):
    """
    Обработчик нажатия на кнопку "Назад" в админ панели.

    :param message: Сообщение от пользователя.
    :type message: Message
    """

    await message.answer("🔑Открываю меню", reply_markup=await kb.get_start_menu(rights="admin"))


@admin.message(IsAdmin(), F.text == "👈Назад")
async def btn_back_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Назад" в других меню админ панели.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("📂 Открываю меню", reply_markup=await kb.get_start_menu(rights="admin"))
    await state.clear()


@admin.message(F.text == "❌Отмена")
async def btn_cancel_action_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Отмена".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("🙅‍♂️ Отменяю действие", reply_markup=await kb.get_events_names_buttons())
    await state.clear()

@admin.message(IsAdmin(), F.text == "🚫Забанить пользователя")
async def btn_ban_user_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Забанить пользователя".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("📨 Отправьте айди пользователя...", reply_markup=kb.ADMIN_PANEL_MARKUP)
    await state.set_state(BanUser.id)


@admin.message(BanUser.id)
async def process_ban_user_by_id(message: Message, state: FSMContext):
    """
    Обработчик получения ID пользователя для бана.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    chat_id = utils.process_id(id_=message.text)

    if chat_id:
        await state.clear()
        message_for_admin = ""

        if not await db.is_user_registered(chat_id=chat_id):
            message_for_admin += "❌ Пользователь не зарегистрирован!"

        elif await db.is_user_banned(chat_id=chat_id):
            message_for_admin += "🚫 Пользователь уже находиться в бане!"

        elif await db.is_user_admin(chat_id=chat_id):
            message_for_admin += "⚠️ Нельзя забанить администратора!"

        else:
            await db.set_ban_status(chat_id=chat_id, ban_status=const.USER_IS_BANNED)
            log_admin_action(message.from_user.id, f"Забанил пользователя с ID {chat_id}")
            message_for_admin += "✅ Пользователь забанен!"

        await message.answer(message_for_admin, reply_markup=kb.ADMIN_PANEL)

    else:
        await message.answer("❗ Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(IsAdmin(), F.text == "✅Разбанить пользователя")
async def btn_unban_user_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Разбанить пользователя".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("📨 Отправьте айди пользователя...", reply_markup=kb.ADMIN_PANEL_MARKUP)
    await state.set_state(UnbanUser.id)


@admin.message(UnbanUser.id)
async def process_unban_user_by_id(message: Message, state: FSMContext):
    """
    Обработчик получения ID пользователя для разбана.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    chat_id = utils.process_id(id_=message.text)

    if chat_id:
        await state.clear()
        message_for_admin = ""

        if not await db.is_user_registered(chat_id=chat_id):
            message_for_admin += "❌ Пользователь не зарегистрирован!"

        elif await db.is_user_banned(chat_id=chat_id):
            await db.set_ban_status(chat_id=chat_id, ban_status=const.USER_NOT_BANNED)
            log_admin_action(message.from_user.id, f"Разбанил пользователя с ID {chat_id}")
            message_for_admin += "✅ Пользователь разбанен!"

        else:
            message_for_admin += "⚠️ Пользователь никогда не был забанен!"

        await message.answer(message_for_admin, reply_markup=kb.ADMIN_PANEL)

    else:
        await message.answer("❗ Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(IsAdmin(), F.text == "➕Добавить админа")
async def btn_add_adm_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Добавить админа".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("📨 Отправьте айди пользователя...", reply_markup=kb.ADMIN_PANEL_MARKUP)
    await state.set_state(AddAdmin.id)


@admin.message(AddAdmin.id)
async def process_add_admin_by_id(message: Message, state: FSMContext):
    """
    Обработчик получения ID пользователя для добавления в администраторы.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    chat_id = utils.process_id(id_=message.text)

    if chat_id:
        await state.clear()
        message_for_admin = ""

        if not await db.is_user_registered(chat_id=chat_id):
            message_for_admin += "❌ Пользователь не зарегистрирован!"

        elif await db.is_user_admin(chat_id=chat_id):
            message_for_admin += "⚠️ Пользователь уже является админом!"

        else:
            await db.set_admin_status(chat_id=chat_id, admin_status=const.USER_IS_ADMIN)
            log_admin_action(message.from_user.id, f"Добавил админа с ID {chat_id}")
            message_for_admin += "✅ Администратор добавлен!"

        await message.answer(message_for_admin, reply_markup=kb.ADMIN_PANEL)

    else:
        await message.answer("❗ Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(IsAdmin(), F.text == "➖Удалить админа")
async def btn_del_adm_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Удалить админа".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("📨 Отправьте айди пользователя...", reply_markup=kb.ADMIN_PANEL_MARKUP)
    await state.set_state(DelAdmin.id)


@admin.message(DelAdmin.id)
async def process_del_admin_by_id(message: Message, state: FSMContext):
    """
    Обработчик получения ID пользователя для удаления из администраторов.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    chat_id = utils.process_id(id_=message.text)

    if chat_id:
        await state.clear()
        message_for_admin = ""

        if not await db.is_user_registered(chat_id=chat_id):
            message_for_admin += "❌ Пользователь не зарегистрирован!"

        elif await db.is_user_admin(chat_id=chat_id):
            await db.set_admin_status(chat_id=chat_id, admin_status=const.USER_NOT_ADMIN)
            log_admin_action(message.from_user.id, f"Удалил админа с ID {chat_id}")
            message_for_admin += "✅ Администратор удалён!"

        else:
            message_for_admin += "⚠️ Такого администратора не существует!"

        await message.answer(message_for_admin, reply_markup=kb.ADMIN_PANEL_MARKUP)

    else:
        await message.answer("❗ Некорректное айди пользователя!\nПопробуйте ещё раз!")


@admin.message(IsAdmin(), IsEventName())
async def btn_event_name_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на событие из списка.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    event_name: str = message.text

    await state.update_data(event_name=event_name)

    await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")

    await message.answer(
                         await utils.get_event_message(event_name=event_name),
                         reply_markup=await kb.get_event_menu(rights="admin", event_status="")
    )

    await state.update_data(event_name=event_name)
    await state.set_state(Event.event_name)


@admin.message(IsAdmin(), F.text == "🗣️Сделать рассылку")
async def btn_mailing_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Сделать рассылку".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await state.set_state(Mailing.message)
    await message.answer("📤 Отправьте сообщение для рассылки...", reply_markup=kb.ADMIN_PANEL_MARKUP)


@admin.message(Mailing.message)
async def process_mailing_message(message: Message, state: FSMContext):
    """
    Обработчик получения сообщения для рассылки.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    mailing_message = message.text

    if mailing_message:
        await state.update_data(message=mailing_message)
        await message.answer("📸 Хотите добавить фотографию к рассылке? Если да, то отправьте её в этом чате, иначе отправьте знак '-'")
        await state.set_state(Mailing.photo)

    else:
        await message.answer("❗ Некорректное сообщение для рассылки!\nПопробуйте ещё раз!")


@admin.message(Mailing.photo, F.content_type == 'photo')
async def process_mailing_photo(message: Message, state: FSMContext):
    """
    Обработчик получения фотографии для рассылки.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    photo_id = message.photo[-1].file_id
    state_data: dict = await state.get_data()
    mailing_message: str = state_data.get("message")

    file = await cfg.BOT.get_file(photo_id)
    file_path = file.file_path
    photo_file = await cfg.BOT.download_file(file_path)
    photo_bytes = photo_file.read()
    photo = BufferedInputFile(photo_bytes, filename="photo.jpg")

    await state.update_data(photo=photo_bytes)

    await message.answer_photo(
        photo=photo,
        caption=f"📢Подтвердите рассылку!\n\n{mailing_message}",
        reply_markup=ReplyKeyboardRemove()
    )

    await message.answer("👇 Нажмите кнопку ниже:", reply_markup=await kb.get_confirm_menu(callback="confirm_mailing"))

    await state.set_state(Mailing.confirm)


@admin.message(Mailing.photo, F.content_type == 'text')
async def process_mailing_photo(message: Message, state: FSMContext):
    """
    Обработчик получения текстовой ссылки на фотографию для рассылки.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    photo_url: str = message.text

    if photo_url and photo_url is const.NO_PHOTO_URL:
        state_data: dict = await state.get_data()
        mailing_message: str = state_data.get("message")

        await state.update_data(photo=photo_url)
        await message.answer(f"📢 Подтвердите рассылку!\n\n{mailing_message}", reply_markup=ReplyKeyboardRemove())
        await message.answer("👇 Нажмите кнопку ниже:", reply_markup=await kb.get_confirm_menu(callback="confirm_mailing"))
        await state.set_state(Mailing.confirm)

    else:
        await message.answer("😕 Я тебя не понимаю!")


@admin.callback_query(Mailing.confirm)
async def confirm_mailing_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения рассылки.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_mailing":
        users = await db.get_users()
        state_data: dict = await state.get_data()
        mailing_message: str = state_data.get("message")
        photo_url: str = state_data.get("photo")

        if photo_url != const.NO_PHOTO_URL:
            photo_url = BufferedInputFile(photo_url, filename="photo.jpg")

        for user in users:
            try:
                if photo_url is const.NO_PHOTO_URL:
                    await cfg.BOT.send_message(chat_id=user.chat_id, text=mailing_message)
                else:
                    await cfg.BOT.send_photo(chat_id=user.chat_id, photo=photo_url, caption=mailing_message)
            except:
                # удаляем человека из рассылки, если он заблокировал бота
                await db.del_user(chat_id=user.chat_id)

        # Логирование действия
        log_admin_action(callback.from_user.id, "сделал рассылку")
        await callback.message.answer("✅ Рассылка завершена!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()

    else:
        await callback.message.answer("❌ Отменяю рассылку!\nВведите новое сообщение!",
                                      reply_markup=kb.ADMIN_PANEL_MARKUP)
        await state.set_state(Mailing.message)


@admin.message(IsAdmin(), F.text == "🎇Создать мероприятие")
async def btn_create_event_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Создать мероприятие".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await state.set_state(AddEvent.name)
    await message.answer("📝 Отправьте название!", reply_markup=kb.ADMIN_PANEL_MARKUP)


@admin.message(AddEvent.name)
async def process_event_name(message: Message, state: FSMContext):
    """
    Обработчик получения названия события.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    event_name = message.text

    if event_name and not await db.get_event_info_by_name(name=event_name):
        await state.update_data(name=event_name)
        await message.answer("📅 Введите дату и время мероприятия! Пример: 24.12.2024 15:00")
        await state.set_state(AddEvent.date_and_time)

    else:
        await message.answer("❗ Некорректное название!\nПопробуйте ещё раз!")


@admin.message(AddEvent.date_and_time)
async def process_event_date(message: Message, state: FSMContext):
    """
    Обработчик получения даты и времени события.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    date_and_time = message.text

    if utils.is_valid_date_and_time(date_and_time=date_and_time):
        date_and_time: datetime = datetime.strptime(date_and_time, const.DATE_AND_TIME_FORMAT)
        await state.update_data(date_and_time=date_and_time)
        await message.answer("✨ Введите описание мероприятия!")
        await state.set_state(AddEvent.description)

    else:
        await message.answer("❗ Некорректная дата и время!\nПопробуйте ещё раз!")


@admin.message(AddEvent.description)
async def process_event_desc(message: Message, state: FSMContext):
    """
    Обработчик получения описания события.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    description = message.text

    if description:
        await message.answer("🎯 Введите тематику мероприятия!")
        await state.update_data(description=description)
        await state.set_state(AddEvent.theme)

    else:
        await message.answer("❗ Некорректное описание!\nПопробуйте ещё раз!")


@admin.message(AddEvent.theme)
async def process_event_theme(message: Message, state: FSMContext):
    """
    Обработчик получения тематики события.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    theme = message.text

    if theme:

        if not await db.is_theme_exists(theme_name=theme):
            await db.add_theme(theme_name=theme)

        await message.answer("👤 Введите лимит на участников!")
        await state.update_data(theme=theme)
        await state.set_state(AddEvent.users_limit)

    else:
        await message.answer("❗ Некорректная тематика мероприятия!\nПопробуйте ещё раз!")


@admin.message(AddEvent.users_limit)
async def process_users_limit(message: Message, state: FSMContext):
    """
    Обработчик получения лимита участников на событие.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    users_limit = message.text

    if users_limit and users_limit.isdigit() and int(users_limit) > 0:
        state_data: dict = await state.get_data()
        name: str = state_data.get("name")
        description: str = state_data.get("description")
        date_and_time: str = state_data.get("date_and_time")
        theme: str = state_data.get("theme")

        await message.answer("🔍 Подтвердите создание мероприятия!"
                             f"\nНазвание : {name}"
                             f"\nОписание : {description}"
                             f"\nТематика : {theme}"
                             f"\nКоличество мест : {users_limit}"
                             f"\nДата и время: {date_and_time}",
                             reply_markup=ReplyKeyboardRemove())

        await message.answer("👇 Нажмите кнопку ниже:",
                             reply_markup=await kb.get_confirm_menu(callback="confirm_add_event"))
        await state.update_data(users_limit=users_limit)
        await state.set_state(AddEvent.confirm)

    else:
        await message.answer("❗ Некорректный лимит участников!\nПопробуйте ещё раз!")


@admin.callback_query(AddEvent.confirm)
async def confirm_create_event_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения создания события.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_add_event":
        state_data: dict = await state.get_data()
        name: str = state_data.get("name")
        date_and_time: str = state_data.get("date_and_time")
        description: str = state_data.get("description")
        theme: str = state_data.get("theme")
        users_limit: str = state_data.get("users_limit")
        theme_id = await db.get_theme_id_by_name(theme_name=theme)

        await db.add_event(name=name, desc=description, date_n_time=date_and_time,
                           theme_id=theme_id, users_limit=users_limit)

        # Логирование действия
        log_admin_action(callback.from_user.id, f"Создал мероприятие с названием {name}")
        notify.start_notifications(event_time=date_and_time, event_name=name)

        await callback.message.answer("✅ Мероприятие добавлено!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()

    else:
        await callback.message.answer("❌ Отменяю создание!\nВведите название мероприятия!",
                                      reply_markup=kb.ADMIN_PANEL_MARKUP)
        await state.set_state(AddEvent.name)


@admin.message(IsAdmin(), Event.event_name, F.text == "📷Отметка по QR-коду")
async def btn_mark_by_qr_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Отметка по QR-коду".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer("Введите текст с qr-кода!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
    await state.set_state(Event.mark_by_qr)


@admin.message(IsAdmin(), Event.mark_by_qr)
async def btn_mark_by_qr_click(message: Message):
    """
    Обработчик текста QR-кода для отметки пользователя на событии.

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    text_from_qr = message.text
    event_id, user_id = text_from_qr.split('-')

    if text_from_qr and await db.is_qr_text_valid(event_id=event_id, user_id=user_id):

        if not await db.is_user_arrived(user_id=user_id, event_id=event_id):
            user_chat_id = await db.get_chat_id_from_user_id(user_id=user_id)
            event_name = (await db.get_event_info_by_id(event_id=event_id)).name

            await db.change_arrival_status(event_id=event_id, user_id=user_id)

            # Логирование действия
            log_admin_action(message.from_user.id, f"Отметил пользователя {user_chat_id} с мероприятия {event_name}")
            await message.answer("😊 Вы успешно отметили пользователя!")

        else:
            await message.answer("✅ Пользователь уже отметился!")

    else:
        await message.answer("❗ Некорректный qr-код!")


@admin.message(IsAdmin(), Event.event_name, F.text == "📊Собрать обратную связь")
async def btn_collect_feedback_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Собрать обратную связь".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    state_data: dict = await state.get_data()
    name: str = state_data.get("event_name")
    event_info = await db.get_event_info_by_name(name=name)
    is_feedback_collected = event_info.is_feedback_collected
    is_signup_open = event_info.is_signup_open

    if not is_feedback_collected:

       if not is_signup_open:
            await message.answer("📎 Введите ссылку на гугл формы!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
            await state.set_state(CollectFeedback.google_link)
            await state.update_data(event_name=name)

       else:
            await message.answer("❗ Закройте запись на мероприятие, прежде чем собрать обратную связь!")

    else:
        await message.answer("❗ Вы уже собрали обратную связь!")


@admin.message(IsAdmin(), CollectFeedback.google_link)
async def process_google_link(message: Message, state: FSMContext):
    """
    Обработчик получения ссылки на Google форму для сбора обратной связи.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    google_link = message.text

    if google_link and (compile(const.GOOGLE_FORM_REGEXP), message.text):
        await message.answer("Подтвердите сбор обратной связи!", reply_markup=ReplyKeyboardRemove())
        await message.answer("👇 Нажмите кнопку ниже:", reply_markup=await kb.get_confirm_menu(callback="collect_feedback_confirm"))
        await state.update_data(google_link=google_link)
        await state.set_state(CollectFeedback.confirm)

    else:
        await message.answer("Введённая вами ссылка некорректна!")


@admin.callback_query(CollectFeedback.confirm)
async def confirm_feedback_collect_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения сбора обратной связи.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "collect_feedback_confirm":
        state_data: dict = await state.get_data()
        name: str = state_data.get("event_name")
        google_link = state_data.get("google_link")
        event_id = (await db.get_event_info_by_name(name=name)).id
        participants = await db.get_all_event_participants(event_id=event_id)

        for person in participants:
            chat_id = await db.get_chat_id_from_user_id(user_id=person.user_id)
            message_for_user = utils.get_feedback_message_by_event_status(person, google_link, name)
            await cfg.BOT.send_message(chat_id=chat_id, text=message_for_user)

        await db.set_feedback_collected(event_name=name)

        # Логирование действия
        log_admin_action(callback.from_user.id, f"Собрал обратную связь с мероприятия {name}")

        await callback.message.answer("✅ Рассылка обратной связи успешна!",
                                      reply_markup=await kb.get_event_menu(rights="admin", event_status=""))

        await state.set_state(Event.event_name)
        await state.update_data(event_name=name)

    else:
        await callback.message.answer("❌ Отменяю сбор обратной связи!\nВведите другую ссылку на гугл формы!", reply_markup=kb.ADMIN_CANCEL_MARKUP)
        await state.set_state(CollectFeedback.google_link)


@admin.message(IsAdmin(), F.text == "🎆Удалить мероприятие")
async def btn_delete_event_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Удалить мероприятие".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    if await db.is_events_exist():
        events = await db.get_events()
        events_enumerate = utils.get_events_enumerate(events=events)

        await message.answer("🗑️ Отправьте номер мероприятия для его удаления!"
                             f"\n{events_enumerate}",
                             reply_markup=kb.ADMIN_PANEL_MARKUP)

        await state.set_state(DelEvent.id)

    else:
        await message.answer("❗ Нет мероприятий, которые можно удалить!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()


@admin.message(DelEvent.id)
async def process_del_event_by_id(message: Message, state: FSMContext):
    """
    Обработчик получения ID мероприятия для удаления.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    event_id = utils.process_id(id_=message.text)

    if event_id:

        event_info = await db.get_event_info_by_id(event_id=event_id)

        # Проверяем, существует ли мероприятие с таким ID
        if event_info:
            event_name = event_info.name

            await state.update_data(id=event_id)
            await message.answer(f"🗑️ Подтвердите удаление мероприятия!\n{event_name}", reply_markup=ReplyKeyboardRemove())
            await message.answer("👇 Нажмите кнопку ниже:", reply_markup=await kb.get_confirm_menu(callback="confirm_del_event"))
            await state.set_state(DelEvent.confirm)

        else:
            await message.answer("❌ Мероприятия с таким номером не существует!", reply_markup=kb.ADMIN_PANEL)
            await state.clear()

    else:
        await message.answer("❗ Некорректный номер!\nПопробуйте ещё раз!", reply_markup=kb.ADMIN_PANEL_MARKUP)


@admin.callback_query(DelEvent.confirm)
async def confirm_del_event_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения удаления мероприятия.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_del_event":

        state_data: dict = await state.get_data()
        event_id: str = state_data.get("id")
        event_id: int = int(event_id)
        event_info = await db.get_event_info_by_id(event_id=event_id)
        event_name = event_info.name

        utils.delete_excel_file_with_participants(event_name=event_name)
        utils.delete_qr_codes_by_event_id(event_id=event_id)

        await db.delete_event(event_id=event_id)

        # Логирование действия
        log_admin_action(callback.from_user.id, f"Удалил мероприятие с названием {event_name}")
        await callback.message.answer("✅ Мероприятие удалено!", reply_markup=kb.ADMIN_PANEL)
        await state.clear()

    else:
        await callback.message.answer("❌ Отменяю удаление!\nВведите другой порядковый номер!", reply_markup=kb.ADMIN_PANEL_MARKUP)
        await state.set_state(DelEvent.id)


@admin.message(IsAdmin(), Event.event_name, F.text == "🔐Закрыть запись")
async def btn_close_event_signup(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Закрыть запись на мероприятие".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    state_data: dict = await state.get_data()
    event_name: str = state_data.get("event_name")

    if await db.is_event_signup_open(event_name=event_name):

        await message.answer(f"🔒 Подтвердите закрытие записи на мероприятие: {event_name}"
                             f"\nУчтите, что в дальнейшем будет невозможно открыть запись!",
                             reply_markup=ReplyKeyboardRemove())

        await message.answer("👇 Нажмите кнопку ниже:",
                             reply_markup=await kb.get_confirm_menu(callback="confirm_close_event"))

    else:
        await message.answer("❌ Мероприятие уже закрыто!")


@admin.callback_query(Event.event_name)
async def confirm_close_event_signup_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения закрытия записи на мероприятие.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await callback.message.delete()
    message_for_admin = ""

    if callback.data == "confirm_close_event":
        state_data: dict = await state.get_data()
        event_name: str = state_data.get("event_name")

        await db.close_event_signup(name=event_name)
        # Логирование действия
        log_admin_action(callback.from_user.id, f"Закрыл запись на мероприятие {event_name}")
        message_for_admin += "✅ Запись закрыта!"

    else:
        message_for_admin += "❌ Отменяю закрытие!"

    await callback.message.answer(message_for_admin, reply_markup=await kb.get_event_menu(rights="admin"))


@admin.message(IsAdmin(), Event.event_name, F.text == "👥Отчёт")
async def btn_get_signup_people_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Отчёт".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    state_data: dict = await state.get_data()
    event_name: str = state_data.get("event_name")
    event_id = (await db.get_event_info_by_name(name=event_name)).id

    if not await db.get_event_participants_count(event_id=event_id):
        await message.answer("😢 На мероприятие никто не записался!")

    else:
        report_message: str = await utils.process_report_message(event_id=event_id)
        # Путь к файлу в папке report_tables
        filepath = os.path.join("report_tables", f"{event_name}.xlsx")

        await utils.create_report_excel_file(event_name=event_name)
        # Логирование действия

        log_admin_action(message.from_user.id, f"Получил отчёт по мероприятию {event_name}")

        # Отправка файла
        await message.answer_document(document=FSInputFile(path=filepath), caption=report_message)