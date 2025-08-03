import datetime
import asyncio
import database.requests as db
import bot.configs.telegram_bot_config as cfg

async def send_notify(event_name: str, message: str) -> None:
    """
    Отправляет уведомление пользователям, зарегистрированным на мероприятие.

    :param event_name: Название мероприятия.
    :param message: Текст уведомления, которое будет отправлено.
    :return: None
    """
    event_id = (await db.get_event_info_by_name(name=event_name)).id
    users = await db.get_signup_people(event_id=event_id)

    for user in users:
        chat_id = await db.get_chat_id_from_user_id(user_id=user.chat_id)
        await cfg.BOT.send_message(chat_id=chat_id, text=message)

async def schedule_notifications(*, event_time, event_name):
    """
    Планирует отправку уведомлений пользователям за 7 дней и за 1 день до события.

    :param event_time: Время начала мероприятия.
    :param event_name: Название мероприятия.
    :return: None
    """
    now = datetime.datetime.now()

    # Время для уведомления за 7 дней до события
    seven_days_before_event = event_time - datetime.timedelta(days=7)

    # Время для уведомления за 1 день до события
    one_day_before_event = event_time - datetime.timedelta(days=1)

    message_seven_days = f"🔔 Уведомление: до начала мероприятия {event_name} осталось 7 дней!\n🗓 Дата начала {event_time}"
    message_one_day = f"🔔 Уведомление: до начала мероприятия {event_name} остался 1 день!\n🗓 Дата начала {event_time}"

    # Запланировать уведомление за 7 дней
    if seven_days_before_event >= now:
        await asyncio.sleep((seven_days_before_event - now).total_seconds())
        await send_notify(event_name, message_seven_days)

    # Запланировать уведомление за 1 день
    if one_day_before_event >= now:
        await asyncio.sleep((one_day_before_event - now).total_seconds())
        await send_notify(event_name, message_one_day)

def start_notifications(event_time, event_name):
    """
    Запускает задачу для планирования уведомлений в основном цикле.

    :param event_time: Время начала мероприятия.
    :param event_name: Название мероприятия.
    :return: None
    """
    asyncio.create_task(schedule_notifications(event_time=event_time, event_name=event_name))
