from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


# Создаём бд и подключаемся к ней
engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)


# Создаём родительский класс для построения моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass


class BannedUser(Base):
    __tablename__ = "banned_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)


class MailingUser(Base):
    __tablename__ = "users_in_mailing"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    date: Mapped[str] = mapped_column(String(14))
    description: Mapped[str] = mapped_column(String(150))
    is_signup_open: Mapped[int] = mapped_column(Integer)


class EventSingUp(Base):
    __tablename__ = "event_singup"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[int] = mapped_column(Integer)
    chat_id: Mapped[int] = mapped_column(Integer)
    event_status: Mapped[int] = mapped_column(Integer)
    event_id: Mapped[int] = mapped_column(ForeignKey(Event.id))


# При запуске главного файла создаём таблицы
async def async_main():
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)