import asyncio
import threading
import database.requests as db
import bot.configs.telegram_bot_config as cfg
import bot.utils as utils
import bot.constants.recommender as const

from database.models import User, Event, UserInterest


async def send_recommend_by_groups(*, interest_groups: dict, events: dict, user_signed_events: dict) -> None:
    """
    Генерирует и отправляет рекомендации по мероприятиям пользователям в группах интересов.

    :param interest_groups: Словарь, где ключи - это группы интересов, а значения - пользователи, принадлежащие к этим группам.
    :param events: Словарь, где ключи - это мероприятия, а значения - идентификаторы тем.
    :param user_signed_events: Словарь, в котором для каждого пользователя указаны мероприятия, на которые он записан.
    :return: None
    """
    for interests, users_in_group in interest_groups.items():
        # Отбираем только мероприятия, подходящие по интересам
        recommended_events = {
            event: theme_id for event, theme_id in events.items() if theme_id in interests
        }

        for user in users_in_group:
            # Отсекаем мероприятия, на которые пользователь уже записан
            filtered_events = {
                event: theme_id for event, theme_id in recommended_events.items()
                if event not in user_signed_events.get(user.id, set())
            }

            if not filtered_events:
                continue  # Пропускаем, если нечего рекомендовать

            # Создаём сообщение с подходящими мероприятиями
            mess_with_recommended_events = utils.get_message_with_events(events=filtered_events)
            await cfg.BOT.send_message(
                chat_id=user.chat_id,
                text=utils.get_recommend_message(mess_with_events=mess_with_recommended_events)
            )


async def recommend_events() -> None:
    """
    Основная функция для рекомендации мероприятий пользователям.

    Собирает информацию о пользователях, мероприятиях и интересах, затем генерирует и отправляет рекомендации.

    :return: None
    """

    users: list[User] = await db.get_users()
    events: list[Event] = await db.get_events_with_open_signup()

    if await db.is_open_signup_events_exist() and await db.is_users_exists():

        # Преобразуем events в словарь для многократного использования
        events: dict = utils.events_to_dict(events=events)
        mess_with_all_events: str = utils.get_message_with_events(events=events)

        user_event_signups: dict = {}
        interest_groups: dict = {}

        for user in users:

            user_interests: list[UserInterest] = await db.get_user_interests(user_id=user.chat_id)

            if not user_interests:

                # Формируем словарь с информацией о мероприятиях, на которые уже записались пользователи
                user_event_signups[user.chat_id] = await utils.process_user_event_signups(user_id=user.chat_id)

                await cfg.BOT.send_message(
                    chat_id=user.chat_id,
                    text=utils.get_recommend_message(mess_with_events=mess_with_all_events)

                )

            else:
                # Формируем группы интересов для дальнейшей рекомендации
                utils.process_interest_groups(interest_groups=interest_groups, user=user, user_interests=user_interests)

        await send_recommend_by_groups(
            interest_groups=interest_groups,
            events=events,
            user_signed_events=user_event_signups
        )


async def schedule_weekly_recommendations():
    """
    Планирует еженедельные рекомендации мероприятий для пользователей.

    Вечный цикл, который запускает функцию recommend_events() каждую неделю.

    :return: None
    """

    while True:
        await recommend_events()
        # Планируем запуск через 7 дней
        await asyncio.sleep(const.ONE_WEEK_IN_SECONDS)


def run_schedule_weekly_recommendations():
    """
    Запускает планировщик для еженедельных рекомендаций в основном асинхронном цикле.

    :return: None
    """

    loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
    loop.create_task(schedule_weekly_recommendations())  # Создаём задачу
    loop.run_forever()  # Запускаем цикл до завершения программы


def start_weekly_recommendations():
    """
    Запускает планировщик для еженедельных рекомендаций в основном асинхронном цикле.

    :return: None
    """

    loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
    loop.create_task(schedule_weekly_recommendations())  # Создаём задачу
