import datetime
import threading
import database.requests as db
import bot.config as cfg


async def send_notify(EVENT_NAME: str, MESSAGE: str) -> None:
    
    USERS = db.get_signup_people(EVENT_NAME=EVENT_NAME)
    
    for user in USERS:
        
        await cfg.BOT.send_message(chat_id=user.chat_id, text=MESSAGE)
    
    
# Функция для планирования уведомлений
def schedule_notifications(*, event_time, EVENT_NAME):
    
    NOW = datetime.datetime.now()
    
    # Преобразование строки в объект datetime
    event_time = datetime.datetime.strptime(event_time, '%d.%m.%Y %H:%M')
    
    # Время для уведомления за 7 дней до события
    SEVEN_DAYS_BEFORE_EVENT = event_time - datetime.timedelta(days=7)
    # Время для уведомления за 1 день до события
    ONE_DAY_BEFORE_EVENT = event_time - datetime.timedelta(days=1)

    MESSAGE_SEVEN_DAYS = "Уведомление: до начала мероприятия {EVENT_NAME} осталось 7 дней!\nДата начала {event_time}"
    MESSAGE_ONE_DAY = "Уведомление: до начала мероприятия {EVENT_NAME} остался 1 день!\nДата начала {event_time}"
    
    # Запланировать уведомление за 7 дней
    if SEVEN_DAYS_BEFORE_EVENT >= NOW:
        threading.Timer((SEVEN_DAYS_BEFORE_EVENT - NOW).total_seconds(), send_notify, args=[EVENT_NAME, MESSAGE_SEVEN_DAYS]).start()

    # Запланировать уведомление за 1 день
    if ONE_DAY_BEFORE_EVENT >= NOW:
        threading.Timer((ONE_DAY_BEFORE_EVENT - NOW).total_seconds(), send_notify, args=[EVENT_NAME, MESSAGE_ONE_DAY]).start()
