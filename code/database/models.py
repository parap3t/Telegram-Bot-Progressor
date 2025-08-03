from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# Создаём бд и подключаемся к ней
engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для моделей, который используется для создания всех таблиц в базе данных.
    Наследуется от `AsyncAttrs` и `DeclarativeBase`,
    обеспечивая асинхронную работу с SQLAlchemy и поддержку декларативного стиля.

    """
    pass


class User(Base):
    """
    Модель пользователя, представляющая таблицу 'users' в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        full_name (str): Полное имя пользователя.
        phone (int): Номер телефона пользователя.
        chat_id (int): Идентификатор чата пользователя.
        is_banned (bool): Статус блокировки пользователя.
        is_admin (bool): Статус администратора пользователя.
        interests (relationship): Связь с таблицей интересов пользователя.
        signups (relationship): Связь с таблицей регистраций на мероприятия.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(40), unique=True)
    phone: Mapped[int] = mapped_column(Integer, unique=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    signups = relationship("EventSignUp", back_populates="user", cascade="all, delete-orphan")


class Theme(Base):
    """
    Модель темы мероприятия, представляющая таблицу 'themes' в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор темы.
        name (str): Название темы.
        events (relationship): Связь с таблицей мероприятий, относящихся к теме.
        user_interests (relationship): Связь с таблицей интересов пользователей, связанных с темой.
    """

    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, index=True)

    events = relationship("Event", back_populates="theme")
    user_interests = relationship("UserInterest", back_populates="theme", cascade="all, delete-orphan")


class UserInterest(Base):
    """
    Модель интереса пользователя, представляющая таблицу 'user_interests' в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор интереса.
        theme_id (int): Внешний ключ на таблицу тем.
        user_id (int): Внешний ключ на таблицу пользователей.
        theme (relationship): Связь с таблицей темы.
        user (relationship): Связь с таблицей пользователя.
    """

    __tablename__ = "user_interests"

    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    theme = relationship("Theme", back_populates="user_interests")
    user = relationship("User", back_populates="interests")

    __table_args__ = (UniqueConstraint("theme_id", "user_id"),)


class Event(Base):
    """
    Модель мероприятия, представляющая таблицу 'events' в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор мероприятия.
        name (str): Название мероприятия.
        description (str): Описание мероприятия.
        theme_id (int): Внешний ключ на таблицу тем.
        date_and_time (datetime): Дата и время мероприятия.
        users_limit (int): Лимит участников мероприятия.
        is_signup_open (bool): Открыта ли регистрация на мероприятие.
        is_feedback_collected (bool): Собраны ли отзывы.
        theme (relationship): Связь с таблицей темы мероприятия.
        signups (relationship): Связь с таблицей регистраций на мероприятие.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(150))
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    date_and_time: Mapped[datetime] = mapped_column(DateTime)
    users_limit: Mapped[int] = mapped_column(Integer)
    is_signup_open: Mapped[bool] = mapped_column(Boolean, default=True)
    is_feedback_collected: Mapped[bool] = mapped_column(Boolean, default=False)

    theme = relationship("Theme", back_populates="events")
    signups = relationship("EventSignUp", back_populates="event", cascade="all, delete-orphan")


class EventSignUp(Base):
    """
    Модель регистрации пользователя на мероприятие, представляющая таблицу 'event_signup' в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор регистрации.
        user_id (int): Внешний ключ на таблицу пользователей.
        event_id (int): Внешний ключ на таблицу мероприятий.
        is_signup_canceled (bool): Статус отмены регистрации.
        is_arrived (bool): Статус прибытия на мероприятие.
        user (relationship): Связь с таблицей пользователя.
        event (relationship): Связь с таблицей мероприятия.
    """

    __tablename__ = "event_signup"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    is_signup_canceled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_arrived: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="signups")
    event = relationship("Event", back_populates="signups")

    __table_args__ = (UniqueConstraint("user_id", "event_id"),)


async def async_main():
    """
    Функция для создания таблиц в базе данных.

    Эта функция запускает асинхронную задачу для выполнения SQL-команд:
    1. Создаёт таблицы, если они ещё не существуют.
    2. Включает поддержку внешних ключей в базе данных SQLite.
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        await conn.execute(text("PRAGMA foreign_keys = ON;"))