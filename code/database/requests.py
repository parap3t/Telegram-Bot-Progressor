from database.models import Admin, BannedUser, UserInMailing, Event, EventSingUp
from database.models import async_session
from bot.config import ADMIN_CHAT_ID
from sqlalchemy import select, delete, update, func

async def get_events():
    async with async_session() as session:
        return await session.scalars(select(Event))

async def add_in_mailing(*, chat_id: int):
    async with async_session() as session:
        # Проверяем находиться-ли пользователь в рассылке
        user = await session.scalar(select(UserInMailing).where(UserInMailing.chat_id == chat_id))
        # Если пользователя нет в таблице, то добавляем его
        if not user:
            session.add(UserInMailing(chat_id=chat_id))
            await session.commit()

async def check_is_signup_open(*, event_name: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where((Event.is_signup_open == 1) &
                                                        (Event.name == event_name)))
        
async def close_signup_to_event(*, event_name: str):
    async with async_session() as session:
        await session.execute(update(Event).where(Event.name == event_name).
                                                  values(is_signup_open = 0))
        await session.commit()

async def del_from_mailing(*, chat_id: int):
    async with async_session() as session:
        await session.execute(delete(UserInMailing).where(UserInMailing.chat_id == chat_id))
        await session.commit()

async def add_in_ban(*, chat_id: int):
    async with async_session() as session:
        session.add(BannedUser(chat_id=chat_id))
        await session.commit()

async def del_from_ban(*, chat_id: int):
    async with async_session() as session:
        await session.execute(delete(BannedUser).where(BannedUser.chat_id == chat_id))
        await session.commit()

async def add_in_admin(*, chat_id: int):
    async with async_session() as session:
        session.add(Admin(chat_id=chat_id))
        await session.commit()

async def del_from_admin(*, chat_id: int):
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.chat_id == chat_id))
        await session.commit()

async def get_users_from_mailing():
    async with async_session() as session:
        return await session.scalars(select(UserInMailing))

async def check_ban(*, chat_id: int):
    async with async_session() as session:
        return await session.scalar(select(BannedUser).where(BannedUser.chat_id == chat_id))

async def check_admin(*, chat_id: int):
    async with async_session() as session:
        if str(chat_id) == ADMIN_CHAT_ID: 
            return True
        else:
            return await session.scalar(select(Admin).where(Admin.chat_id == chat_id))

async def add_event_to_table(*, event_name: str, event_description: str, 
                             event_date: str, is_signup_open: int=1):
    async with async_session() as session:
        session.add(Event(name=event_name, description=event_description, 
                          date=event_date, is_signup_open=is_signup_open))
        await session.commit()
    
async def delete_event_from_table(*, event_id: int):
    async with async_session() as session:
        await session.execute(delete(Event).where(Event.id == event_id))
        await session.commit()
        await session.execute((delete(EventSingUp).where(EventSingUp.event_id == event_id)))
        await session.commit()

async def check_event_by_name(*, event_name: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == event_name))

async def check_event_by_id(*, event_id: int):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == event_id))

async def get_event_name_by_id(*, event_id: int):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == event_id))

async def get_event_info_by_name(*, event_name: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == event_name))

async def add_signup_user(*, event_name: str, full_name: str, phone: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        session.add(EventSingUp(chat_id=chat_id, full_name=full_name, 
                                phone=phone, event_id=id_of_event, event_status=1))
        await session.commit()

async def check_signup(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(EventSingUp).where((EventSingUp.event_id == id_of_event) &
                                                              (EventSingUp.chat_id == chat_id)))

async def check_go_to_event(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(EventSingUp).where((EventSingUp.event_status == 1) &
                                                               (EventSingUp.event_id == id_of_event) &
                                                               (EventSingUp.chat_id == chat_id)))

async def get_full_info_about_singup_user(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(EventSingUp).where((EventSingUp.event_id == id_of_event) &
                                                              (EventSingUp.chat_id == chat_id)))

async def change_signup_status(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        await session.execute(update(EventSingUp).where((EventSingUp.event_id == id_of_event) &
                                                        (EventSingUp.chat_id == chat_id)).
                                                        values(event_status = 0))
        await session.commit()

async def get_count_of_signup(*, event_name: str):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(func.count(EventSingUp.id)).filter((EventSingUp.event_status == 1) &
                                                                              (EventSingUp.event_id == id_of_event)))

async def get_count_of_events():
    async with async_session() as session:
        return await session.scalar(select(func.count(Event.id)))

async def get_signup_people(*, event_name: str):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        people: dict = {
            "Полное имя": [],
            "Телефон": [],
            "Айди чата": []
        }
        signup_people = await session.scalars(select(EventSingUp).where((EventSingUp.event_status == 1) & 
                                                                        (EventSingUp.event_id == id_of_event)))
        for user in signup_people:
            people["Полное имя"] += [user.full_name]
            people["Телефон"] += [user.phone]
            people["Айди чата"] += [user.chat_id]
        return people
