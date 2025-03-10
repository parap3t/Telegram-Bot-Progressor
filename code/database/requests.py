import bot.config as cfg

from database.models import Admin, BannedUser, MailingUser, Event, EventSingUp
from database.models import async_session
from sqlalchemy import select, delete, update, func


SIGNUP_PERSON = 1
CANCELED_SIGNUP = 0


async def get_events():
    async with async_session() as session:
        return await session.scalars(select(Event))


async def add_in_mailing(*, CHAT_ID: int):
    async with async_session() as session:
        
        # Проверяем находиться-ли пользователь в рассылке
        USER = await session.scalar(select(MailingUser).where(MailingUser.chat_id == CHAT_ID))
        
        # Если пользователя нет в таблице, то добавляем его
        if not USER:
            
            session.add(MailingUser(chat_id=CHAT_ID))
            
            await session.commit()


async def check_is_signup_open(*, EVENT_NAME: str):
    async with async_session() as session:
        
        OPEN_SIGNUP = 1
        
        return await session.scalar(select(Event).where(
                                                        (Event.is_signup_open == OPEN_SIGNUP) &
                                                        (Event.name == EVENT_NAME)
                                                        ))
        

async def close_event_signup(*, NAME: str):
    async with async_session() as session:
        
        CLOSE_SIGNUP = 0
        
        await session.execute(update(Event).where(Event.name == NAME).
                                                  values(is_signup_open = CLOSE_SIGNUP))
        
        await session.commit()


async def del_from_mailing(*, CHAT_ID: int):
    async with async_session() as session:
        await session.execute(delete(MailingUser).where(MailingUser.chat_id == CHAT_ID))
        await session.commit()


async def add_in_ban(*, CHAT_ID: int):
    async with async_session() as session:
        
        session.add(BannedUser(chat_id=CHAT_ID))
        
        await session.commit()


async def del_from_ban(*, CHAT_ID: int):
    async with async_session() as session:
        await session.execute(delete(BannedUser).where(BannedUser.chat_id == CHAT_ID))
        await session.commit()


async def add_in_admin(*, CHAT_ID: int):
    async with async_session() as session:
        
        session.add(Admin(chat_id=CHAT_ID))
        
        await session.commit()


async def del_from_admin(*, CHAT_ID: int):
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.chat_id == CHAT_ID))
        await session.commit()


async def get_mailing_users():
    async with async_session() as session:
        return await session.scalars(select(MailingUser))


async def check_ban(*, CHAT_ID: int):
    async with async_session() as session:
        return await session.scalar(select(BannedUser).where(BannedUser.chat_id == CHAT_ID))


async def check_admin(*, chat_id: int):
    async with async_session() as session:
        
        if str(chat_id) == cfg.ADMIN_CHAT_ID: 
            return True
        
        else:
            return await session.scalar(select(Admin).where(Admin.chat_id == chat_id))


async def add_event(*, NAME: str, DESCRIPTION: str, 
                       DATE_AND_TIME: str, is_signup_open: int=1):
    
    async with async_session() as session:
        
        session.add(Event(name=NAME, description=DESCRIPTION, 
                          date_and_time=DATE_AND_TIME, is_signup_open=is_signup_open))
        
        await session.commit()
    
    
async def delete_event(*, ID: int):
    async with async_session() as session:
        
        await session.execute(delete(Event).where(Event.id == ID))
        await session.commit()
        
        await session.execute((delete(EventSingUp).where(EventSingUp.event_id == ID)))
        await session.commit()


async def check_event_by_name(*, NAME: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == NAME))


async def check_event_by_id(*, ID: int):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == ID))


async def get_event_name_by_id(*, ID: int):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == ID))


async def get_event_info_by_name(*, NAME: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == NAME))


async def add_signup_user(*, EVENT_NAME: str, FULL_NAME: str, PHONE: str, CHAT_ID: int):
    async with async_session() as session:
           
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        session.add(EventSingUp(chat_id=CHAT_ID, 
                                full_name=FULL_NAME, 
                                phone=PHONE, 
                                event_id=EVENT_ID, 
                                event_status=SIGNUP_PERSON))
        
        await session.commit()


async def check_signup(*, EVENT_NAME: str, CHAT_ID: int):
    async with async_session() as session:
        
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        return await session.scalar(select(EventSingUp).where(
                                                              (EventSingUp.event_id == EVENT_ID) &
                                                              (EventSingUp.chat_id == CHAT_ID)
                                                              ))


async def check_go_to_event(*, EVENT_NAME: str, CHAT_ID: int):
    async with async_session() as session:
        
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        return await session.scalar(select(EventSingUp).where(
                                                               (EventSingUp.event_status == SIGNUP_PERSON) &
                                                               (EventSingUp.event_id == EVENT_ID) &
                                                               (EventSingUp.chat_id == CHAT_ID)
                                                              ))


async def get_signup_user_full_info(*, EVENT_NAME: str, CHAT_ID: int):
    async with async_session() as session:
        
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        return await session.scalar(select(EventSingUp).where(
                                                              (EventSingUp.event_id == EVENT_ID) &
                                                              (EventSingUp.chat_id == CHAT_ID)
                                                              ))


async def change_signup_status(*, EVENT_NAME: str, CHAT_ID: int):
    async with async_session() as session:
        
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        await session.execute(update(EventSingUp).where(
                                                        (EventSingUp.event_id == EVENT_ID) &
                                                        (EventSingUp.chat_id == CHAT_ID)).
                                                        values(event_status = CANCELED_SIGNUP))
        
        await session.commit()


async def get_signup_count(*, EVENT_NAME: str):
    async with async_session() as session:
        
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        return await session.scalar(select(func.count(EventSingUp.id)).filter(
                                                                              (EventSingUp.event_status == SIGNUP_PERSON) &
                                                                              (EventSingUp.event_id == EVENT_ID)
                                                                              ))


async def get_events_count():
    async with async_session() as session:
        return await session.scalar(select(func.count(Event.id)))


async def get_signup_people(*, EVENT_NAME: str):
    async with async_session() as session:
        
        EVENT_ID = (await session.scalar(select(Event).where(Event.name == EVENT_NAME))).id
        
        people: dict = {
            "Полное имя": [],
            "Телефон": [],
            "Айди чата": []
        }
        
        signup_people = await session.scalars(select(EventSingUp).where(
                                                                        (EventSingUp.event_status == SIGNUP_PERSON) & 
                                                                        (EventSingUp.event_id == EVENT_ID)
                                                                        ))
        
        for user in signup_people:
            
            people["Полное имя"] += [user.full_name]
            people["Телефон"] += [user.phone]
            people["Айди чата"] += [user.chat_id]
            
        return people
