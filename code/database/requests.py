import os
import bot.constants.db_requests as const

from datetime import datetime
from typing import Optional
from sqlalchemy import select, delete, update, func
from dotenv import load_dotenv
from database.models import User, Event, EventSignUp, Theme, UserInterest
from database.models import async_session


load_dotenv()


async def get_events() -> list[Event]:
    """
    Получить все события из базы данных.

    :return: Список всех событий.
    :rtype: list[Event]
    """

    async with async_session() as session:

        result = await session.scalars(
            select(Event)
        )

        return result.all()


async def get_events_with_open_signup() -> list[Event]:
    """
    Получить события с открытой регистрацией.

    :return: Список событий с открытой регистрацией.
    :rtype: list[Event]
    """

    async with async_session() as session:

        result = await session.scalars(
            select(Event).
            where(
                (Event.is_signup_open == const.OPEN_SIGNUP)
            )
        )

        return result.all()


async def get_user_id(*, chat_id: int) -> Optional[int]:
    """
    Получить ID пользователя по его chat_id.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :return: ID пользователя, если найден, иначе None.
    :rtype: Optional[int]
    """

    async with async_session() as session:

        result = await session.scalar(
            select(User).
            where(
                (User.chat_id == chat_id)
            )
        )

        if result is not None:
            return result.id

        return result


async def is_event_signup_open(*, event_name: str) -> bool:
    """
    Проверить, открыта ли регистрация на событие.

    :param event_name: Название события.
    :type event_name: str

    :return: True, если регистрация открыта, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(Event)
            .where(
                (Event.is_signup_open == const.OPEN_SIGNUP) &
                (Event.name == event_name)
            )
        )

        return result is not None


async def close_event_signup(*, name: str) -> None:
    """
    Закрыть регистрацию на событие.

    :param name: Название события.
    :type name: str
    """

    async with async_session() as session:

        await session.execute(
            update(Event).
            where(
                (Event.name == name)).
            values(is_signup_open = const.CLOSE_SIGNUP)
        )

        await session.commit()


async def add_user(*, full_name: str, phone: str, chat_id: int) -> None:
    """
    Добавить нового пользователя в базу данных.

    :param full_name: Полное имя пользователя.
    :type full_name: str

    :param phone: Телефон пользователя.
    :type phone: str

    :param chat_id: chat_id пользователя.
    :type chat_id: int
    """

    async with async_session() as session:

        session.add(User(chat_id=chat_id, full_name=full_name, phone=phone))

        await session.commit()


async def del_user(*, chat_id: int) -> None:
    """
    Удалить пользователя по его chat_id.

    :param chat_id: chat_id пользователя.
    :type chat_id: int
    """

    async with async_session() as session:

        await session.execute(
            delete(User).
            where(User.chat_id == chat_id)
        )

        await session.commit()


async def get_info_about_user(*, chat_id: int) -> Optional[User]:
    """
    Получить информацию о пользователе по chat_id.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :return: Пользователь, если найден, иначе None.
    :rtype: Optional[User]
    """

    async with async_session() as session:

        return await session.scalar(
            select(User)
            .where(
                User.chat_id == chat_id
            )
        )


async def get_chat_id_from_user_id(*, user_id: int) -> Optional[int]:
    """
    Получить chat_id по ID пользователя.

    :param user_id: ID пользователя.
    :type user_id: int

    :return: chat_id пользователя, если найден, иначе None.
    :rtype: Optional[int]
    """

    async with async_session() as session:

        result = await session.scalar(
            select(User)
            .where(
                User.id == user_id
            )
        )

        if result is not None:
            return result.chat_id

        return result


async def set_ban_status(*, chat_id: int, ban_status: bool) -> None:
    """
    Установить статус бана для пользователя.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :param ban_status: Статус бана (True - забанен, False - не забанен).
    :type ban_status: bool
    """

    async with async_session() as session:

        await session.execute(
            update(User).
            where(
                (User.chat_id == chat_id)).
            values(is_banned=ban_status)
        )

        await session.commit()


async def set_admin_status(*, chat_id: int, admin_status: bool) -> None:
    """
    Установить статус администратора для пользователя.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :param admin_status: Статус администратора (True - администратор, False - не администратор).
    :type admin_status: bool
    """

    async with async_session() as session:

        await session.execute(
            update(User).
            where(
                (User.chat_id == chat_id)).
            values(is_admin=admin_status)
        )

        await session.commit()


async def is_user_arrived(*, user_id: int, event_id: int) -> bool:
    """
    Проверить, прибыл ли пользователь на событие.

    :param user_id: ID пользователя.
    :type user_id: int

    :param event_id: ID события.
    :type event_id: int

    :return: True, если пользователь прибыл, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(EventSignUp)
            .where(
                (EventSignUp.user_id == user_id) &
                (EventSignUp.event_id == event_id) &
                (EventSignUp.is_arrived == const.ARRIVED)
            )
        )

        return result


async def is_user_registered(*, chat_id: int) -> bool:
    """
    Проверить, зарегистрирован ли пользователь по chat_id.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :return: True, если пользователь зарегистрирован, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(User)
            .where(
                User.chat_id == chat_id
            )
        )

        return result is not None


async def get_users() -> list[User]:
    """
    Получить всех пользователей из базы данных.

    :return: Список всех пользователей.
    :rtype: list[User]
    """

    async with async_session() as session:

        result = await session.scalars(
            select(User)
        )

        return result.all()


async def is_user_banned(*, chat_id: int) -> bool:
    """
    Проверить, забанен ли пользователь по chat_id.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :return: True, если пользователь забанен, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(User)
            .where(
                (User.chat_id == chat_id) &
                (User.is_banned == const.USER_IS_BANNED))
        )

        return result is not None


async def is_user_admin(*, chat_id: int) -> bool:
    """
    Проверить, является ли пользователь администратором.

    :param chat_id: chat_id пользователя.
    :type chat_id: int

    :return: True, если пользователь является администратором, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(User)
            .where(
                (User.chat_id == chat_id) &
                (User.is_admin == const.USER_IS_ADMIN))
        )

        return result is not None



async def add_event(*, name: str, desc: str, date_n_time: datetime, theme_id: int, users_limit: int) -> None:
    """
    Добавить новое событие.

    :param name: Название события.
    :type name: str

    :param desc: Описание события.
    :type desc: str

    :param date_n_time: Дата и время события.
    :type date_n_time: datetime

    :param theme_id: ID темы события.
    :type theme_id: int

    :param users_limit: Лимит пользователей на событие.
    :type users_limit: int
    """

    async with async_session() as session:

        session.add(Event(name=name, description=desc, date_and_time=date_n_time, theme_id=theme_id, users_limit=users_limit))

        await session.commit()


async def set_users_limit(*, users_limit: int, event_id: int) -> None:
    """
    Установить лимит пользователей для события.

    :param users_limit: Новый лимит пользователей.
    :type users_limit: int

    :param event_id: ID события.
    :type event_id: int
    """

    async with async_session() as session:

        await session.execute(
            update(Event)
            .where(
                EventSignUp.event_id == event_id
            )
            .values(users_limit=users_limit)
        )

        await session.commit()


async def delete_event(*, event_id: int) -> None:
    """
    Удалить событие по ID.

    :param event_id: ID события.
    :type event_id: int
    """

    async with async_session() as session:

        await session.execute(
            delete(Event)
            .where(
                Event.id == event_id
            )
        )

        await session.commit()


async def get_theme_name_by_id(*, theme_id: str) -> str:
    """
    Получить название темы по ID.

    :param theme_id: ID темы.
    :type theme_id: str

    :return: Название темы.
    :rtype: str
    """

    async with async_session() as session:

        result = await session.scalar(
            select(Theme)
            .where(
                Theme.id == theme_id
            )
        )

        return result.name


async def is_theme_exists(*, theme_name: str) -> bool:
    """
    Проверить, существует ли тема по названию.

    :param theme_name: Название темы.
    :type theme_name: str

    :return: True, если тема существует, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(Theme).where(func.lower(Theme.name) == func.lower(theme_name))
        )

        return result is not None


async def add_theme(theme_name: str) -> None:
    """
    Добавить новую тему.

    :param theme_name: Название новой темы.
    :type theme_name: str
    """

    async with async_session() as session:

        session.add(Theme(name=theme_name))

        await session.commit()


async def get_theme_id_by_name(*, theme_name: str) -> int:
    """
    Получить ID темы по названию.

    :param theme_name: Название темы.
    :type theme_name: str

    :return: ID темы.
    :rtype: int
    """

    async with async_session() as session:

        result = await session.scalar(
            select(Theme)
            .where(
                func.lower(Theme.name) == func.lower(theme_name)
            )
        )

        return result.id


async def get_event_info_by_id(*, event_id: int) -> Optional[Event]:
    """
    Получить информацию о событии по ID.

    :param event_id: ID события.
    :type event_id: int

    :return: Информация о событии, если найдено, иначе None.
    :rtype: Optional[Event]
    """

    async with async_session() as session:

        return await session.scalar(
            select(Event)
            .where(
                Event.id == event_id
            )
        )


async def get_event_info_by_name(*, name: str) -> Optional[Event]:
    """
    Получить информацию о событии по названию.

    :param name: Название события.
    :type name: str

    :return: Информация о событии, если найдено, иначе None.
    :rtype: Optional[Event]
    """

    async with async_session() as session:

        return await session.scalar(
            select(Event)
            .where(
                Event.name == name
            )
        )


async def is_theme_in_user_interests(*, theme_id: int, user_id: int) -> bool:
    """
    Проверить, есть ли тема в интересах пользователя.

    :param theme_id: ID темы.
    :type theme_id: int

    :param user_id: ID пользователя.
    :type user_id: int

    :return: True, если тема есть в интересах пользователя, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(UserInterest)
            .where(
                   (UserInterest.user_id == user_id) &
                   (UserInterest.theme_id == theme_id)
            )
        )

        return result is not None


async def add_user_interest(*, theme_id: int, user_id: int) -> None:
    """
    Добавить интерес пользователя к теме.

    :param theme_id: ID темы.
    :type theme_id: int

    :param user_id: ID пользователя.
    :type user_id: int
    """

    async with async_session() as session:

        session.add(UserInterest(theme_id=theme_id, user_id=user_id))

        await session.commit()


async def get_user_event_signups(*, user_id) -> list[EventSignUp]:
    """
    Получить список регистраций пользователя на события.

    :param user_id: ID пользователя.
    :type user_id: int

    :return: Список регистраций пользователя.
    :rtype: list[EventSignUp]
    """

    async with async_session() as session:

        result = await session.scalars(
            select(EventSignUp)
            .where(
                  (EventSignUp.user_id == user_id)
            )
        )

        return result.all()


async def get_event_names_by_ids(*, event_ids: list):
    """
    Получить названия событий по их ID.

    :param event_ids: Список ID событий.
    :type event_ids: list

    :return: Список событий.
    :rtype: list[Event]
    """

    async with async_session() as session:

         await session.scalars(
            select(Event).where(
                (Event.id.in_(event_ids))
            )
        )


async def get_user_interests(*, user_id: int) -> list[UserInterest]:
    """
    Получить список интересов пользователя.

    :param user_id: ID пользователя.
    :type user_id: int

    :return: Список интересов пользователя.
    :rtype: list[UserInterest]
    """

    async with async_session() as session:

        result = await session.scalars(
            select(UserInterest)
            .where(
                UserInterest.user_id == user_id
            )
        )

        return result.all()


async def add_signup_user(*, event_id: str, user_id: int) -> None:
    """
    Добавить пользователя на регистрацию к событию.

    :param event_id: ID события.
    :type event_id: str

    :param user_id: ID пользователя.
    :type user_id: int
    """

    async with async_session() as session:

        session.add(EventSignUp(user_id=user_id, is_signup_canceled=const.SIGNUP_NOT_CANCELED, event_id=event_id, is_arrived=const.NOT_ARRIVED))

        await session.commit()


async def is_qr_text_valid(user_id: str, event_id: str) -> bool:
    """
    Проверить, действителен ли текст QR-кода для пользователя и события.

    :param user_id: ID пользователя.
    :type user_id: str

    :param event_id: ID события.
    :type event_id: str

    :return: True, если QR-код действителен, иначе False.
    :rtype: bool
    """
    async with async_session() as session:

        result = await session.scalar(
            select(EventSignUp)
            .where(
                   (EventSignUp.user_id == user_id) &
                   (EventSignUp.event_id == event_id) &
                   (EventSignUp.is_signup_canceled == const.SIGNUP_NOT_CANCELED)
            )
        )

        return result is not None


async def is_user_signup_canceled(*, event_id: str, user_id: int) -> bool:
    """
    Проверить, отменил ли пользователь регистрацию на событие.

    :param event_id: ID события.
    :type event_id: str

    :param user_id: ID пользователя.
    :type user_id: int

    :return: True, если регистрация отменена, иначе False.
    :rtype: bool
    """
    async with async_session() as session:

        result = await session.scalar(
            select(EventSignUp)
            .where(
                   (EventSignUp.user_id == user_id) &
                   (EventSignUp.event_id == event_id) &
                   (EventSignUp.is_signup_canceled == const.SIGNUP_CANCELED)
            )
        )

        return result is not None


async def is_user_signed_up_to_event(*, event_id: str, user_id: int) -> Optional[EventSignUp]:
    """
    Проверить, зарегистрирован ли пользователь на событие.

    :param event_id: ID события.
    :type event_id: str

    :param user_id: ID пользователя.
    :type user_id: int

    :return: Регистрация пользователя на событие, если существует, иначе None.
    :rtype: Optional[EventSignUp]
    """
    async with async_session() as session:

        result = await session.scalar(
            select(EventSignUp)
            .where(
                (EventSignUp.event_id == event_id) &
                (EventSignUp.user_id == user_id)
            )
        )

        return result is not None


async def change_arrival_status(*, event_id: int, user_id: int) -> None:
    """
    Изменить статус прибытия пользователя на событие.

    :param event_id: ID события.
    :type event_id: int

    :param user_id: ID пользователя.
    :type user_id: int
    """
    async with async_session() as session:

        await session.execute(
            update(EventSignUp)
            .where(
                    (EventSignUp.event_id == event_id) &
                    (EventSignUp.user_id == user_id)
            )
            .values(is_arrived=const.ARRIVED)
        )

        await session.commit()


async def cancel_user_signup(*, event_id: str, user_id: int) -> None:
    """
    Отменить регистрацию пользователя на событие.

    :param event_id: ID события.
    :type event_id: str

    :param user_id: ID пользователя.
    :type user_id: int
    """
    async with async_session() as session:

        await session.execute(
            update(EventSignUp)
            .where(
                    (EventSignUp.event_id == event_id) &
                    (EventSignUp.user_id == user_id)
            )
            .values(is_signup_canceled = const.SIGNUP_CANCELED)
        )

        await session.commit()


async def get_signup_people_count(*, event_id: str) -> int:
    """
    Получить количество людей, зарегистрированных на событие.

    :param event_id: ID события.
    :type event_id: str

    :return: Количество зарегистрированных пользователей.
    :rtype: int
    """
    async with async_session() as session:

        return await session.scalar(
            select(func.count(EventSignUp.id))
            .filter(
                    (EventSignUp.is_signup_canceled == const.SIGNUP_NOT_CANCELED) &
                    (EventSignUp.event_id == event_id)
            )
        )


async def get_event_participants_count(*, event_id: int) -> int:
    """
    Получить количество участников события.

    :param event_id: ID события.
    :type event_id: int

    :return: Количество участников.
    :rtype: int
    """

    async with async_session() as session:

        return await session.scalar(
            select(func.count(EventSignUp.id))
            .filter(
                    (EventSignUp.event_id == event_id)
            )
        )


async def add_root_admin() -> None:
    """
    Добавить администратора с правами root.

    :return: None
    """

    async with async_session() as session:

        if not await is_user_registered(chat_id=int(os.getenv("ADMIN_CHAT_ID"))):

            session.add(User(chat_id=os.getenv("ADMIN_CHAT_ID"),
                             full_name=os.getenv("ADMIN_FULL_NAME"),
                             phone=os.getenv("ADMIN_PHONE"),
                             is_admin=const.USER_IS_ADMIN))

            await session.commit()

async def get_count_canceled_signups_by_person(*, event_id: int) -> int:
    """
    Получить количество отмененных регистраций для события.

    :param event_id: ID события.
    :type event_id: int

    :return: Количество отмененных регистраций.
    :rtype: int
    """
    async with async_session() as session:

        return await session.scalar(
            select(func.count(EventSignUp.id))
            .filter(
                    (EventSignUp.event_id == event_id) &
                    (EventSignUp.is_signup_canceled == const.SIGNUP_CANCELED)
            )
        )


async def get_count_person_by_arrival_status(*, event_id: int, arrival_status: int) -> int:
    """
    Получить количество людей по статусу прибытия.

    :param event_id: ID события.
    :type event_id: int

    :param arrival_status: Статус прибытия (например, 1 - прибыл, 0 - не прибыл).
    :type arrival_status: int

    :return: Количество людей с заданным статусом прибытия.
    :rtype: int
    """

    async with async_session() as session:

        return await session.scalar(
            select(func.count(EventSignUp.id))
            .filter(
                    (EventSignUp.event_id == event_id) &
                    (EventSignUp.is_signup_canceled == const.SIGNUP_NOT_CANCELED) &
                    (EventSignUp.is_arrived == arrival_status)
            )
        )


async def is_events_exist() -> bool:
    """
    Проверить, существуют ли события в базе данных.

    :return: True, если существуют события, иначе False.
    :rtype: bool
    """
    async with async_session() as session:

        result = await session.scalar(
            select(func.count(Event.id))
        )

        return bool(result)


async def is_open_signup_events_exist() -> bool:
    """
    Проверить, существуют ли события с открытой регистрацией.

    :return: True, если существуют события с открытой регистрацией, иначе False.
    :rtype: bool
    """
    async with async_session() as session:

        result = await session.scalar(
            select(func.count(Event.id))
            .where(
                (Event.is_signup_open == const.OPEN_SIGNUP)
            )
        )

        return bool(result)


async def is_users_exists() -> bool:
    """
    Проверить, существуют ли пользователи в базе данных.

    :return: True, если существуют пользователи, иначе False.
    :rtype: bool
    """

    async with async_session() as session:

        result = await session.scalar(
            select(
                func.count(User.id)
            )
        )

        return bool(result)


async def set_feedback_collected(*, event_name: str) -> None:
    """
    Установить флаг о том, что сбор отзывов завершен для события.

    :param event_name: Название события.
    :type event_name: str
    """

    async with async_session() as session:

        await session.execute(
            update(Event)
            .where(
                (Event.name == event_name)
            )
            .values(is_feedback_collected = const.FEEDBACK_COLLECTED)
        )

        await session.commit()


async def get_signup_people(*, event_id: str) -> list[EventSignUp]:
    """
    Получить список людей, зарегистрированных на событие.

    :param event_id: ID события.
    :type event_id: str

    :return: Список людей, зарегистрированных на событие.
    :rtype: list[EventSignUp]
    """

    async with async_session() as session:

        result = await session.scalars(
            select(EventSignUp)
            .where(
                    (EventSignUp.is_signup_canceled == const.SIGNUP_NOT_CANCELED) &
                    (EventSignUp.event_id == event_id)
            )
        )

        return result.all()


async def get_all_event_participants(*, event_id: str) -> list[EventSignUp]:
    """
    Получить всех участников события.

    :param event_id: ID события.
    :type event_id: str

    :return: Список всех участников события.
    :rtype: list[EventSignUp]
    """

    async with async_session() as session:

       result = await session.scalars(
           select(EventSignUp)
           .where(
               (EventSignUp.event_id == event_id)
           )
       )

       return result.all()