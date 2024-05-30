# Импортируем недостающие модули
from database.models import Admin,BannedUser,UserInMailing,Event
from database.models import async_session,engine
from sqlalchemy import text

# Импортируем sql запросы
from sqlalchemy import select,delete

# Получаем список мероприятий
async def getEvents() -> list:
    async with async_session() as session:
        return await session.scalars(select(Event))

# Проверяем есть-ли пользователь в рассылке
async def addUserInMailing(chat_id : int) -> None:
    async with async_session() as session:
        # Проверяем находиться-ли пользователь в рассылке
        user = await session.scalar(select(UserInMailing).where(UserInMailing.chat_id == chat_id))
        # Если пользователя нет в таблица,то добавляем его
        if not user:
            session.add(UserInMailing(chat_id = chat_id))
            await session.commit()

# Добавляем пользователя в таблицу с баном
async def addBannedUser(chat_id : int) -> None:
    async with async_session() as session:
        session.add(BannedUser(chat_id = chat_id))
        await session.commit()

# Удаляем забаненного пользователя из таблицы
async def delBannedUser(chat_id : int) -> None:
    async with async_session() as session:
        await session.execute(delete(BannedUser).where(BannedUser.chat_id == chat_id))
        await session.commit()

# Добавляем админа в таблицу
async def addAdm(chat_id : int) -> None:
    async with async_session() as session:
        session.add(Admin(chat_id = chat_id))
        await session.commit()

# Удаляем админа из таблицы
async def delAdm(chat_id : int) -> None:
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.chat_id == chat_id))
        await session.commit()

# Получаем всех пользователей из рассылки
async def getUsers() -> list:
    async with async_session() as session:
        return await session.scalars(select(UserInMailing))

# Проверяем забанен-ли пользователь
async def checkBan(chat_id : int) -> list:
    async with async_session() as session:
        return await session.scalar(select(BannedUser).where(BannedUser.chat_id == chat_id))

# Проверяем является-ли пользователь админом
async def checkAdmin(chat_id : int) -> list:
    if str(chat_id) == "chat_id": 
        return True
    else:
        async with async_session() as session:
            return await session.scalar(select(Admin).where(Admin.chat_id == chat_id))

# Создаём таблицу для записи пользователей на мероприятие 
async def createTable(foreign_key : str) -> None: 
    async with async_session() as session:
        await session.execute(statement=text(f"CREATE TABLE {foreign_key}(id INTEGER PRIMARY KEY AUTOINCREMENT,first_last_name TEXT(50),phone TEXT(20),didnt_come INTEGER,email TEXT(70),chat_id INTEGER)"))
        await session.commit()

# Вносим данные в таблицу
async def addToEvent(name : str,description : str,foreign_key : str) -> None:
    async with async_session() as session:
        session.add(Event(name = name,description = description,foreign_key = foreign_key))
        await session.commit()
    
# Удаляем строку из главной таблицы и таблицу с записями
async def deleteTable(id : int) -> None:
    async with async_session() as session:
        for_key = (await session.scalar(select(Event).where(Event.id == id))).foreign_key
        await session.execute(statement=text(f"DROP TABLE {for_key}"))
        await session.commit()
        await session.execute(delete(Event).where(Event.id == id))
        await session.commit()

# Проверяем существует-ли такое мероприятие
async def checkEventByName(name: str) -> list:
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == name))

# Проверяем существует-ли такое мероприятие
async def checkEventById(id : int) -> list:
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == id))

# Получаем название мероприятия с помощью айди
async def getEventNameById(id : int) -> str:
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == id))

# Получаем описание мероприятия по названию
async def getDescEventByName(name : str) -> list:
    async with async_session() as session:
      return await session.scalar(select(Event).where(Event.name == name))

# Вставляем данные пользователя в таблицу с записавшимися    
async def insertSignUpUser(eventName : str,firstLastNames : str,phone: str,email : str,chatId : int) -> None:
    async with async_session() as session:
      forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
      await session.execute(statement=text(f"INSERT INTO {forKey}(first_last_name,phone,email,chat_id,didnt_come) VALUES('{firstLastNames}','{phone}','{email}','{chatId}',1)"))
      await session.commit()

# Проверяем записан-ли пользователь на мероприятие
async def checkSignUp(eventName : str,chatId : int) -> tuple:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        return (await session.execute(statement=text(f"SELECT chat_id FROM {forKey} WHERE chat_id = {chatId} "))).fetchone()

# Проверяем статус пользователя
async def checkWontCome(eventName : str,chatId : int) -> tuple:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        return (await session.execute(statement=text(f"SELECT didnt_come FROM {forKey} WHERE chat_id = {chatId} and didnt_come = 1"))).fetchone()

# Получаем ф.и пользователя    
async def getLastFirstNames(eventName : str,chatId : int) -> tuple:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        return (await session.execute(statement=text(f"SELECT first_last_name FROM {forKey} WHERE chat_id = {chatId}"))).fetchone()

# Обновляем статус пользователя     
async def updateWontCome(eventName : str,chatId : int) -> None:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        await session.execute(statement=text(f"UPDATE {forKey} SET didnt_come = 0 WHERE chat_id = {chatId}"))
        await session.commit()

# Получаем количество записавшихся пользователей 
async def getCountOfSignUp(eventName : str) -> tuple:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        return (await session.execute(statement=text(f"SELECT COUNT(didnt_come) FROM {forKey}"))).fetchone()
    
# Получаем количество и список всех идущих на мероприятие пользователей    
async def getComeUsers(eventName: str) -> str:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        count = list((await session.execute(statement=text(f"SELECT count(chat_id) FROM {forKey} WHERE didnt_come = 1"))).fetchone())[0]
        if not(count):
            return "Количество идущих людей : 0"
        else:
            people = ""
            signUpPeople = (await session.execute(statement=text(f"SELECT first_last_name,phone,email,chat_id FROM {forKey} WHERE didnt_come = 1"))).fetchall()
            for user in signUpPeople:
                people += f"\n{user}"
            return f"Количество идущих людей : {list(count)[0]}\nCписки идущих : {people}"
  
# Получаем количество и список всех не идущих на мероприятие пользователей 
async def getWontComeUsers(eventName : str) -> str:
    async with async_session() as session:
        forKey = (await session.scalar(select(Event).where(Event.name == eventName))).foreign_key
        count = list((await session.execute(statement=text(f"SELECT count(chat_id) FROM {forKey} WHERE didnt_come = 0"))).fetchone())[0]
        if not(count):
            return "Количество не идущих людей : 0"
        else:
            people = ""
            signUpPeople = (await session.execute(statement=text(f"SELECT first_last_name,phone,email,chat_id FROM {forKey} WHERE didnt_come = 0"))).fetchall()
            for user in signUpPeople:
                people += f"\n{user}"
            return f"Количество не идущих людей : {count}\nCписки не идущих : {people}"