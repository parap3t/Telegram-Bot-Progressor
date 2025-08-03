import bot.keyboards as kb
import database.requests as db
import bot.utils as utils
import bot.constants.han_users as const
import bot.configs.telegram_bot_config as cfg

from typing import Optional
from database.models import User
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from re import compile, search
from bot.configs.logger_config import log_user_action


# Чтобы не писать dispatcher 2-й раз заменим его на роутер
user = Router()


# Создаём класс (фильтр) для того, чтобы проверить забанен ли пользователь
class IsUserBanned(Filter):
    """
    Фильтр для проверки, забанен ли пользователь.

    Этот фильтр проверяет, находится ли пользователь в списке забаненных.
    Если пользователь забанен, то фильтр позволяет выполнить дальнейшие действия.
    """

    async def __call__(self, message: Message):
        """
        Проверяет, забанен ли пользователь.

        :param message: Сообщение от пользователя.
        :type message: Message

        :return: True, если пользователь забанен, иначе False.
        :rtype: bool
        """

        return await db.is_user_banned(chat_id=message.from_user.id)


# Создаём класс (фильтр) для проверки является ли сообщение названием мероприятия
class IsEventName(Filter):
    """
    Фильтр для проверки, является ли сообщение названием мероприятия.

    Этот фильтр проверяет, существует ли мероприятие с таким названием в базе данных.
    """

    async def __call__(self, message: Message):
        """
        Проверяет, существует ли мероприятие с данным названием.

        :param message: Сообщение от пользователя.
        :type message: Message

        :return: True, если мероприятие существует, иначе False.
        :rtype: bool
        """

        return await db.get_event_info_by_name(name=message.text)


# Создаём класс (фильтр) для проверки зарегистрирован ли пользователь
class IsUserRegistered(Filter):
    """
    Фильтр для проверки, зарегистрирован ли пользователь.

    Этот фильтр проверяет, зарегистрирован ли пользователь в системе.
    """

    async def __call__(self, message: Message):
        """
        Проверяет, зарегистрирован ли пользователь.

        :param message: Сообщение от пользователя.
        :type message: Message

        :return: True, если пользователь зарегистрирован, иначе False.
        :rtype: bool
        """

        return await db.is_user_registered(chat_id=message.from_user.id)


# Создаём класс (состояние) для записи на мероприятие
class EventSignUp(StatesGroup):
    """
    Состояние для записи на мероприятие.

    Это состояние используется для взаимодействия с пользователем в процессе записи на мероприятие.
    """

    event_name = State()  # Название мероприятия
    confirm = State()  # Подтверждение записи


# Создаём класс (состояние) для регистрации пользователя
class Registration(StatesGroup):
    """
    Состояние для регистрации пользователя.

    Это состояние используется для сбора и подтверждения данных нового пользователя.
    """

    data_processing_consent_confirm = State()  # Согласие на обработку данных
    full_name = State()  # Полное имя пользователя
    phone = State()  # Номер телефона пользователя
    confirm = State()  # Подтверждение регистрации


# Обработка сообщений от забаненного пользователя
@user.message(IsUserBanned())
async def process_banned_user(message: Message):
    """
    Обработчик сообщений от забаненного пользователя.

    :param message: Сообщение от пользователя.
    :type message: Message
    """

    await message.answer("🚫 Вы забанены за плохое поведение!")


# Обработка команды /start (регистрация пользователя)
@user.message(CommandStart())
async def process_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start. Если пользователь зарегистрирован, приветствие.
    В противном случае — запрос согласия на обработку данных.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    await message.answer_sticker("CAACAgIAAxkBAAEDJLZlt3nrHgcV-CbOkU3EuAhDVSg4GQACkQ8AAo7aAAFIhPeRyUFm2n40BA")

    if await db.is_user_registered(chat_id=message.from_user.id):

        user_info: User = await db.get_info_about_user(chat_id=message.from_user.id)
        user_full_name: str = user_info.full_name

        await message.answer(f"🤗 Добро пожаловать, {user_full_name}!",
                             reply_markup=await kb.get_start_menu(rights="user"))

    else:
        await message.answer(const.DATA_PROCESSING_CONSENT_MESSAGE,
                             reply_markup=await kb.get_confirm_menu(callback="confirm_data_processing"))

        await state.set_state(Registration.data_processing_consent_confirm)


# Обработчик согласия на обработку данных
@user.callback_query(Registration.data_processing_consent_confirm)
async def confirm_data_processing_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения согласия на обработку данных.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_data_processing":

        await callback.message.answer("\n📝 Для продолжения вам нужно зарегистрироваться!"
                                      "\nВведите своё имя в таком формате: Имя Фамилия")

        await state.set_state(Registration.full_name)

    else:
        await callback.message.answer(const.DISAGREE_DATA_PROCESSING_CONSENT_MESS)
        await state.clear()


# Обработчик ввода полного имени пользователя
@user.message(Registration.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """
    Обработчик ввода полного имени пользователя.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """

    full_name: Optional[str] = message.text

    if full_name and search(compile(const.FULL_NAME_REGEXP), full_name):

        await state.update_data(full_name=full_name)

        await message.answer("Поделитесь своим номером телефона, нажав на кнопку '📞Отправить' ",
                             reply_markup=kb.USER_PHONE_MARKUP)

        await state.set_state(Registration.phone)

    else:
        await message.answer("🤔 Некорректные ф.и!\nПопробуйте ещё раз!")


# Обработчик ввода номера телефона
@user.message(Registration.phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Обработчик ввода номера телефона пользователя.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    phone_request: Optional = message.contact

    if phone_request:

        state_data: dict = await state.get_data()
        full_name: str = state_data.get("full_name")
        user_phone: str = phone_request.phone_number

        await message.answer("Подтвердите регистрацию!"
                             "\n📒Ваши данные : "
                             f"\n👤Ф.И : {full_name}"
                             f"\n📞Номер телефона : {user_phone}",
                             reply_markup=ReplyKeyboardRemove())

        await message.answer("👇 Нажмите кнопку ниже:", reply_markup=await kb.get_confirm_menu(callback="confirm_reg"))
        await state.update_data(phone=user_phone)
        await state.set_state(Registration.confirm)

    else:
        await message.answer("🤔 Некорректный номер телефона!\nПопробуйте ещё раз!")


# Обработчик подтверждения регистрации
@user.callback_query(Registration.confirm)
async def confirm_registration_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения регистрации пользователя.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_reg":

        state_data: dict = await state.get_data()
        user_full_name: str = state_data.get("full_name")
        user_phone: str = state_data.get("phone")
        user_chat_id: int = callback.from_user.id

        await db.add_user(full_name=user_full_name, phone=user_phone, chat_id=user_chat_id)

        await callback.message.answer("🙌 Вы успешно прошли регистрацию!",
                                      reply_markup=await kb.get_start_menu(rights="user"))

        log_user_action(callback.from_user.id, "зарегистрировался")
        await state.clear()

    else:
        await callback.message.answer("❌ Отменяю регистрацию!\nВведите фамилию и имя!")
        await state.set_state(Registration.full_name)


# Обработчик команды айди
@user.message(Command("id"))
async def process_id(message: Message):
    """
    Обработчик команды /id для получения идентификатора пользователя.

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    await message.answer(f"👤 Ваш айди: {message.from_user.id}")


# Обработчик отмены действия
@user.message(F.text == "🚫Отмена")
async def btn_cancel_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "Отмена".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await state.set_state(EventSignUp.event_name)
    await message.answer("❌ Отменяю действие",
                         reply_markup=await kb.get_event_menu(rights="user", event_status="unsigned"))


# Обработчик команды "Наши контакты"
@user.message(F.text == "👤Наши контакты")
async def btn_contacts_click(message: Message):
    """
    Обработчик нажатия кнопки "Наши контакты".

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    await message.answer("📞 Наши контакты:", reply_markup=kb.OUR_CONTACTS)


# Обработчик команды "Тех поддержка"
@user.message(F.text == "💻Тех поддержка")
async def btn_support_click(message: Message):
    """
    Обработчик нажатия кнопки "Тех поддержка".

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    await message.answer("🛠️ Техническая поддержка:", reply_markup=kb.TECH_SUPPORT)


# Обработчик команды "Помощь"
@user.message(F.text == "❓Помощь")
async def btn_support_click(message: Message):
    """
    Обработчик нажатия кнопки "Помощь".

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    await message.answer(const.HELP_TEXT, parse_mode="Markdown")


# Обработчик нажатия кнопки "Мероприятия"
@user.message(F.text == "🎉Мероприятия")
async def btn_events_click(message: Message):
    """
    Обработчик нажатия кнопки "Мероприятия".

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    if not await db.is_events_exist():
        await message.answer("😢 Нет мероприятий на которые можно записаться!")
    else:
        await message.answer("✨ Выберите интересующее вас мероприятие!",
                             reply_markup=await kb.get_events_names_buttons())


# Обработчик кнопки "Назад"
@user.message(F.text == "🔙Назад")
async def btn_exit_from_events_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "Назад".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await state.clear()
    await message.answer("🔄 Перехожу назад", reply_markup=await kb.get_events_names_buttons())


# Обработка сообщений от незарегистрированного пользователя
@user.message(~IsUserRegistered())
async def process_unregistered_user(message: Message):
    """
    Обработчик сообщений от незарегистрированного пользователя.

    :param message: Сообщение от пользователя.
    :type message: Message
    """
    await message.answer("🔒 Вы еще не зарегистрированы в нашей системе. "
                         "Чтобы получить доступ ко всем функциям и мероприятиям, "
                         "пожалуйста, пройдите регистрацию.")


# Обработчик нажатия кнопки "Назад"
@user.message(F.text == "👈Назад")
async def btn_back_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "Назад".

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await state.clear()
    await message.answer("🔙 Открываю меню", reply_markup=await kb.get_start_menu(rights="user"))


# Обработчик нажатий кнопок с названием мероприятий
@user.message(IsEventName())
async def btn_event_name_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки с названием мероприятия.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    event_name = message.text
    chat_id = message.from_user.id

    await state.set_state(EventSignUp.event_name)
    await state.update_data(event_name=event_name)
    await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")

    event_info = await db.get_event_info_by_name(name=event_name)
    event_id = event_info.id
    user_id = await db.get_user_id(chat_id=chat_id)
    is_open = await db.is_event_signup_open(event_name=event_name)
    is_signed = await db.is_user_signed_up_to_event(event_id=event_id, user_id=user_id)
    is_canceled = await db.is_user_signup_canceled(event_id=event_id, user_id=user_id) if is_signed else False
    message_text = await utils.get_event_message(event_name=event_name)

    if not is_signed:
        status = "unsigned" if is_open and event_info.users_limit else ""

    elif not is_canceled:
        status = "signed"
        message_text += "\n🛎Статус : пойду"

    else:
        status = ""
        message_text += "\n🛎Статус : не пойду"

    await message.answer(
        message_text,
        reply_markup=await kb.get_event_menu(rights="user", event_status=status)
    )


# Обработчик нажатия кнопки "❌Я не приду", отмена записи на мероприятие
@user.message(F.text == "❌Я не приду", EventSignUp.event_name)
async def btn_cancel_signup_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "❌Я не приду" для отмены записи на мероприятие.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    state_data: dict = await state.get_data()
    event_name: str = state_data.get("event_name")
    chat_id = message.from_user.id
    event_info = await db.get_event_info_by_name(name=event_name)
    event_id = event_info.id
    user_id = await db.get_user_id(chat_id=chat_id)

    if not await db.is_user_signed_up_to_event(event_id=event_id, user_id=user_id):
        await message.answer("📝 Для начала запишитесь на мероприятие!")

    else:
        if not await db.is_user_signup_canceled(event_id=event_id, user_id=user_id):

            await message.answer("😔 Вы точно не пойдёте на мероприятие?"
                                 "\nПримечание: после подтверждения вы больше не сможете "
                                 "записаться на это мероприятие!",
                                 reply_markup=ReplyKeyboardRemove())

            await message.answer("👇 Нажмите кнопку ниже:",
                                 reply_markup=await kb.get_confirm_menu(callback="confirm_cancel_signup"))

        else:
            await message.answer("🤔 Вы уже отменили запись!")


# Обработчик нажатия кнопки для подтверждения отмены записи на мероприятие
@user.callback_query(EventSignUp.event_name)
async def confirm_cancel_signup_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения отмены записи на мероприятие.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_cancel_signup":

        state_data: dict = await state.get_data()
        event_name: str = state_data.get("event_name")
        chat_id: int = callback.from_user.id
        event_info = await db.get_event_info_by_name(name=event_name)
        event_id = event_info.id
        user_id = await db.get_user_id(chat_id=chat_id)

        await db.set_users_limit(users_limit=event_info.users_limit + 1, event_id=event_id)
        await db.cancel_user_signup(event_id=event_id, user_id=user_id)

        log_user_action(chat_id, f"отменил запись на мероприятие {event_name}")
        await callback.message.answer("✅ Вы успешно отменили запись!",
                                      reply_markup=await kb.get_events_names_buttons())
    else:
        await callback.message.answer("❌ Отменяю действие!",
                                      reply_markup=await kb.get_event_menu(rights="user", event_status="signed"))


# Обработчик нажатия кнопки "📝Записаться" на мероприятие
@user.message(F.text == "📝Записаться", EventSignUp.event_name)
async def btn_signup_click(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "📝Записаться" на мероприятие.

    :param message: Сообщение от пользователя.
    :type message: Message

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    state_data: dict = await state.get_data()
    event_name: str = state_data.get("event_name")

    # Проверка, открыта ли запись на мероприятие
    if await db.is_event_signup_open(event_name=event_name):
        chat_id = message.from_user.id
        event_id = (await db.get_event_info_by_name(name=event_name)).id
        user_id = await db.get_user_id(chat_id=chat_id)

        # Проверка, записан ли пользователь на мероприятие
        if not await db.is_user_signed_up_to_event(event_id=event_id, user_id=user_id):
            await message.answer("🤝 Подтвердите запись на мероприятие!", reply_markup=ReplyKeyboardRemove())

            await message.answer("👇 Нажмите кнопку ниже:",
                                 reply_markup=await kb.get_confirm_menu(callback="confirm_signup"))

            await state.set_state(EventSignUp.confirm)

        else:
            await message.answer("🤔 Вы уже записались на это мероприятие!")

    else:
        await message.answer("🚫 Запись на мероприятие уже закрыта!")


# Обработчик нажатия кнопки для подтверждения/отмены записи на мероприятие
@user.callback_query(EventSignUp.confirm)
async def confirm_signup_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения записи на мероприятие.

    :param callback: Данные от callback-запроса.
    :type callback: CallbackQuery

    :param state: Контекст состояний.
    :type state: FSMContext
    """
    await callback.message.delete()

    if callback.data == "confirm_signup":
        state_data: dict = await state.get_data()
        user_chat_id: int = callback.from_user.id
        event_name: str = state_data.get("event_name")
        event_info = await db.get_event_info_by_name(name=event_name)
        event_id = event_info.id
        user_id = await db.get_user_id(chat_id=user_chat_id)
        event_users_limit = event_info.users_limit

        # Добавляем тематику мероприятия в userInterest
        await utils.process_user_interest(user_id=user_id, event_name=event_name)
        await db.add_signup_user(event_id=event_id, user_id=user_id)

        log_user_action(user_chat_id, f"записался на мероприятие {event_name}")
        await db.set_users_limit(users_limit=event_users_limit - 1, event_id=event_id)

        await callback.message.answer("📅 Вы успешно записались!\nКогда придёте на мероприятие, "
                                      "покажите QR-код администратору.",
                                      reply_markup=await kb.get_events_names_buttons())

        qr_path = await utils.process_qr(user_chat_id, event_name)
        photo = FSInputFile(qr_path)

        await cfg.BOT.send_photo(chat_id=user_chat_id, photo=photo)
        await state.clear()

    else:
        await callback.message.answer("❌ Отменяю запись!",
                                      reply_markup=await kb.get_event_menu(rights="user", event_status="unsigned"))