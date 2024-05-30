# Импортируем необходимые модули
from sqlalchemy import String,Integer
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs,async_sessionmaker,create_async_engine 

# Создём бд и подключаемся к ней
engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)

# Создаём родительский класс для построения моделей
class Base(AsyncAttrs,DeclarativeBase):
    pass

# Таблица с забаненными пользователями
class BannedUser(Base):
    __tablename__ = "banned_users"

    id : Mapped[int] = mapped_column(primary_key=True)
    chat_id : Mapped[int] = mapped_column(Integer)

# Таблица с пользователями,которые находятся в рассылке
class UserInMailing(Base):
    __tablename__ = "users_in_mailing"

    id : Mapped[int] = mapped_column(primary_key=True)
    chat_id : Mapped[int] = mapped_column(Integer)

# Таблица с айди чата администраторов
class Admin(Base):
    __tablename__ = "Admins"

    id : Mapped[int] = mapped_column(primary_key=True)
    chat_id : Mapped[int] = mapped_column(Integer)

# Таблица для мероприятий
class Event(Base):
    __tablename__ = "Events"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(60))
    description : Mapped[str] = mapped_column(String(150))
    foreign_key : Mapped[str] = mapped_column(String(5))

# При запуске главного файла создаём таблицы
async def async_main() -> None:
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)