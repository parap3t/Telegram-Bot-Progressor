# Импортируем клавиатуру
import bot.keyboards as kb

# Импортируем недостающие модули и функции
from aiogram import Router,F,Bot
from aiogram .types import Message,CallbackQuery
from database.requests import (checkAdmin,checkBan,addBannedUser,delBannedUser,addAdm,delAdm,getUsers,
                               createTable,deleteTable,addToEvent,getEvents,checkEventByName,checkEventById,
                               getDescEventByName,getEventNameById,getCountOfSignUp,getComeUsers,getWontComeUsers)

from aiogram.filters import CommandStart,Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup

from random import choice
from string import ascii_lowercase

# Чтобы не писать dispatcher 2-й раз заменим его на роутер
admin = Router()

# Создаём переменную с ботом,чтобы в дальнейшем можно было отправить рассылку
bot = Bot(token="token")

# Создаём фильтр для проверки админа
class AdminProtect(Filter):
    async def __call__(self,message : Message):
        return await checkAdmin(message.from_user.id)

# Создаём класс для проверки мероприятий
class EventCheck(Filter):
    async def __call__(self,message : Message):
        return await checkEventByName(message.text)

# Создаём состояние для рассылки
class Mailing(StatesGroup):
    message = State()
    confirm = State()

# Создаём состояние для бана пользователя
class BanUser(StatesGroup):
    id = State()

# Создаём состояние для разбана пользователя
class UnBanUser(StatesGroup):
    id = State()

# Создаём состояние для добавления админа
class AddAdmin(StatesGroup):
    id = State()

# Создаём состояние для удаления админа
class DelAdmin(StatesGroup):
    id = State()

# Создаём состояние для удаления админа
class AddEvent(StatesGroup):
    name = State()
    description = State()
    confirm = State()

# Создаём состояние для удаления мероприятия
class DelEvent(StatesGroup):
    id = State()
    confirm = State()

# Создаём состояние для выбора мероприятия
class EventPick(StatesGroup):
    event = State()

# Обработаем команду старт
@admin.message(AdminProtect(),CommandStart())
async def showAdminMenu(message : Message):
    await message.answer_sticker("CAACAgIAAxkBAAEFm5ZmTgIqpv3A8pzMD_lR3EsFPA0u8gACXAwAAj0zCEiRSKTz6TfmmDUE")
    await message.answer(f"Добро пожаловать,{message.from_user.first_name}!",reply_markup=kb.adminMenu)

# Обработаем нажатие на кнопку админ.панель
@admin.message(AdminProtect(),F.text == "⚙️Админ.панель")
async def showAdminPanel(message : Message):
    await message.answer("Открываю админ.панель",reply_markup=kb.adminPanel)

# Обработаем нажатие на кнопку назад
@admin.message(AdminProtect(),F.text == "🤖Назад")
async def btnBackClick(message : Message):
    await message.answer("Открываю меню",reply_markup=kb.adminMenu)

# Обработаем нажатие на кнопку забанить пользователя
@admin.message(AdminProtect(),F.text == "🚫Забанить пользователя")
async def btnBanClick(message : Message,state : FSMContext):
    # Устанавливаем состояние и ожидаем от пользователя сообщение
    await state.set_state(BanUser.id)
    await message.answer("Отправьте айди пользователя...",reply_markup=kb.adminCancelMarkup)

# Обработаем кнопку отмена
@admin.message(F.text == "❌Отмена")
async def btnCancelClick(message : Message,state : FSMContext):
    # Выходим из состояния и отправляем сообщение
    await message.answer("Отменяю действие",reply_markup=kb.adminPanel)
    await state.clear()

# Принимаем сообщение для бана пользователя
@admin.message(BanUser.id)
async def waitBanMessage(message : Message,state : FSMContext):
    # Проверяем сообщение на корректность
    if message.text != None and message.text.isdigit():
        # Проверяем забанен-ли уже пользователь
        if await checkBan(message.text):
            await message.answer("Пользователь уже находиться в бане!",reply_markup=kb.adminPanel)
            await state.clear()
        # Проверяем явялется-ли админом пользователь
        elif await checkAdmin(message.text):
            await message.answer("Нельзя забанить администратора!",reply_markup=kb.adminPanel)
            await state.clear()
        else:
            # Вносим пользователя в таблицу 
            await message.answer("Пользователь забанен!",reply_markup=kb.adminPanel)
            await addBannedUser(message.text)
            await state.clear()
    else:
        await message.answer("Некорректное айди пользователя...\nПопробуйте ещё раз!")

# Обработаем нажатие на кнопку забанить пользователя
@admin.message(AdminProtect(),F.text == "✅Разбанить пользователя")
async def btnUnBanClick(message : Message,state : FSMContext):
    await state.set_state(UnBanUser.id)
    await message.answer("Отправьте айди пользователя...",reply_markup=kb.adminCancelMarkup)

# Принимаем сообщение для разбана пользователя
@admin.message(UnBanUser.id)
async def waitUnBanMessage(message : Message,state : FSMContext):
    if message.text != None and message.text.isdigit():
        if await checkBan(message.text):
            await message.answer("Пользователь разбанен!",reply_markup=kb.adminPanel)
            await delBannedUser(message.text)
            await state.clear()
        else:
            await message.answer("Пользователь никогда не был забанен!",reply_markup=kb.adminPanel)
            await addBannedUser(message.text)
            await state.clear()
    else:
        await message.answer("Некорректное айди пользователя...\nПопробуйте ещё раз!")

# Обработаем нажатие на кнопку добавить админа
@admin.message(AdminProtect(),F.text == "➕Добавить админа")
async def btnaddAdmClick(message : Message,state : FSMContext):
    await state.set_state(AddAdmin.id)
    await message.answer("Отправьте айди пользователя...",reply_markup=kb.adminCancelMarkup)

# Принимаем сообщение для добавления админа
@admin.message(AddAdmin.id)
async def waitAddAdminMessage(message : Message,state : FSMContext):
    # Проверяем сообщение на корректность
    if message.text != None and message.text.isdigit():
        # Проверяем явялется-ли админом пользователь
        if await checkAdmin(message.text):
            await message.answer("Пользователь уже является админом!",reply_markup=kb.adminPanel)
            await state.clear()
        else:
            await message.answer("Администратор добавлен!",reply_markup=kb.adminPanel)
            await addAdm(message.text)
            await state.clear()
    else:
        await message.answer("Некорректное айди пользователя...\nПопробуйте ещё раз!")

# Обработаем нажатие на кнопку удалить админа
@admin.message(AdminProtect(),F.text == "➖Удалить админа")
async def btnDelAdmClick(message : Message,state : FSMContext):
   await state.set_state(DelAdmin.id)
   await message.answer("Отправьте айди пользователя...",reply_markup=kb.adminCancelMarkup)
  
# Принимаем сообщение для удаления админа
@admin.message(DelAdmin.id)
async def waitDelAdminMessage(message : Message,state : FSMContext):
    if message.text != None and message.text.isdigit():
        if await checkAdmin(message.text):
            await message.answer("Администратор удалён!",reply_markup=kb.adminPanel)
            await delAdm(message.text)
            await state.clear()
        else:
            await message.answer("Нет такого администратора!",reply_markup=kb.adminPanel)
            await state.clear()
    else:
        await message.answer("Некорректное айди пользователя...\nПопробуйте ещё раз!")

# Обработаем нажатие на кнопку сделать рассылку
@admin.message(AdminProtect(),F.text == "🗣️Сделать рассылку")
async def btnMailingClick(message : Message,state : FSMContext):
    await state.set_state(Mailing.message)
    await message.answer("Отправьте сообщение для рассылки...",reply_markup=kb.adminCancelMarkup)

# Обработаем сообщение для рассылки
@admin.message(Mailing.message)
async def waitMailingMessage(message : Message,state : FSMContext):
    # Проверяем сообщение на корректность
    if message.text != None:
        # Сохраяем сообщение и просим пользователя подтвердить рассылку
        await state.update_data(message = message.text)
        await message.answer(f"Подтвердите отправку рассылки!\nТекст рассылки : {message.text}",reply_markup=kb.mailingConfirm)
        await state.set_state(Mailing.confirm)
    else:
        await message.answer("Некорректное сообщение для рассылки!\nПопробуйте ещё раз!")

# Обработаем кнопку для подтверждения/отмены рассылки
@admin.callback_query(Mailing.confirm)
async def confirmMailingCallback(callback : CallbackQuery, state : FSMContext):
   if callback.data == "confirm_mailing":
        # Получаем список пользователей
        users = await getUsers()
        # Получаем сообщение админа
        data = await state.get_data()
        mess = data.get("message")
        # Отправляем рассылку
        for user in users:
            try:
                await bot.send_message(chat_id = user.chat_id,text = mess)
            except:
                pass
        await callback.message.delete()
        await callback.message.answer("Рассылка завершена!",reply_markup=kb.adminPanel)
        await state.clear()
   else:
        await callback.message.delete()
        await callback.message.answer("Отменяю рассылку!\nВведите новое сообщение!",reply_markup=kb.adminCancelMarkup)
        await state.set_state(Mailing.message)


# Обработаем нажатие на кнопку создать мероприятие
@admin.message(AdminProtect(),F.text == "🎇Создать мероприятие")
async def btnCreateEventClick(message : Message,state : FSMContext):
    await state.set_state(AddEvent.name)
    await message.answer("Отправьте название!",reply_markup=kb.adminCancelMarkup)

# Обработаем сообщение с именем мероприятия
@admin.message(AddEvent.name)
async def waitingCreateEventName(message : Message,state : FSMContext):
    if message.text != None:
        if not(await checkEventByName(message.text)):
            await state.update_data(name = message.text)
            await message.answer("Введите описание мероприятия!",reply_markup=kb.adminCancelMarkup)
            await state.set_state(AddEvent.description)
        else:
            await message.answer("Мероприятие с таким названием уже существует!",reply_markup=kb.adminPanel)
            await state.clear()
    else:
        await message.answer("Некорректное название!\nПопробуйте ещё раз!",reply_markup=kb.adminCancelMarkup)

# Обработаем сообщение с именем мероприятия
@admin.message(AddEvent.description)
async def waitingCreateEventDisc(message : Message,state : FSMContext):
    if message.text != None:
        data = await state.get_data()
        name = data.get("name")
        await state.update_data(description = message.text)
        await message.answer(f"Подтвердите создание мероприятия!\nНазвание : {name}\nОписание : {message.text}",reply_markup=kb.addEventConfirm)
        await state.set_state(AddEvent.confirm)
    else:
        await message.answer("Некорректное описание!\nПопробуйте ещё раз!",reply_markup=kb.adminCancelMarkup)

# Обработаем кнопку для подтверждения/отмены создания мероприятия
@admin.callback_query(AddEvent.confirm)
async def confirmAddEventCallback(callback : CallbackQuery, state : FSMContext):
    if callback.data == "confirmAddEvent":
        # Получаем сообщение админа
        data = await state.get_data()
        name = data.get("name")
        description = data.get("description")
        for_key = "".join([choice(ascii_lowercase) for _ in range(5)])
        await createTable(for_key)
        await addToEvent(name,description,for_key)
        await callback.message.delete()
        await callback.message.answer("Мероприятие добавлено!",reply_markup=kb.adminPanel)
        await state.clear()
    else:
        await callback.message.delete()
        await callback.message.answer("Отменяю создание!\nВведите название мероприятия!",reply_markup=kb.adminCancelMarkup)
        await state.set_state(AddEvent.name)

# Обработаем нажатие на кнопку удалить мероприятие
@admin.message(AdminProtect(),F.text == "🎆Удалить мероприятие")
async def btnDeleteEventClick(message : Message,state : FSMContext):
    mess : str = ""
    for event in await getEvents():
        mess += f"{event.id}. {event.name}\n"
    if mess:
        await message.answer(f"Отправьте номер мероприятия!\n{mess}",reply_markup=kb.adminCancelMarkup)
        await state.set_state(DelEvent.id)
    else:
        await message.answer("Нет мероприятий,которые можно удалить!",reply_markup=kb.adminPanel)
        await state.clear()


# Обработаем сообщение для удаления мероприятия
@admin.message(DelEvent.id)
async def waitingDeleteEventMessage(message : Message,state : FSMContext):
    if message.text is not None and message.text.isdigit():
        if await checkEventById(message.text):
            await state.update_data(id = message.text)
            await message.answer(f"Подтвердите удаление мероприятия!\n{message.text}. {(await getEventNameById(message.text)).name}",reply_markup=kb.delEventConfirm)
            await state.set_state(DelEvent.confirm)
        else:
            await message.answer("Мероприятия с таким номером не существует!",reply_markup=kb.adminPanel)
            await state.clear()
    else:
        await message.answer("Некорректный номер!\nПопробуйте ещё раз!",reply_markup=kb.adminCancelMarkup)

# Обработаем кнопку для подтверждения/отмены удаления мероприятия
@admin.callback_query(DelEvent.confirm)
async def confirmDelEventCallback(callback : CallbackQuery, state : FSMContext):
    if callback.data == "confirmDelEvent": # удаляем
        data = await state.get_data()
        id = data.get("id")
        await deleteTable(id)
        await callback.message.delete()
        await callback.message.answer("Мероприятие удалено!",reply_markup=kb.adminPanel)
        await state.clear()
    else:
        await callback.message.delete()
        await callback.message.answer("Отменяю удаление!\nВведите другой порядковый номер!",reply_markup=kb.adminCancelMarkup)
        await state.set_state(DelEvent.id)

# Обработка кнопки назад
@admin.message(AdminProtect(),F.text == "👈Назад")
async def showAdminMenu(message : Message,state : FSMContext):
    await state.clear()
    await message.answer("Открываю меню",reply_markup=kb.adminMenu)

# Обработаем нажатие по одному из мероприятий
@admin.message(AdminProtect(),EventCheck())
async def showEventInfo(message : Message,state : FSMContext):
    await state.set_state(EventPick.event)
    await state.update_data(event = message.text)
    await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE",reply_markup=None)
    await message.answer(f"🎉Название мероприятия : {message.text}\n🎊Описание мероприятия : {(await getDescEventByName(message.text)).description}",reply_markup=kb.adminEventPanel) 

# Обрабоатем нажатие по кнопке записавшиеся
@admin.message(AdminProtect(),F.text == "👥Записавшиеся")
async def showSignUpUsers(message : Message,state : FSMContext):
    data = await state.get_data()
    event = data.get("event") # если никто не записался то так и выводим # в запросах,если количество идущих равно 0 то список не нужен
    if list(await getCountOfSignUp(event))[0] == 0:
        await message.answer("На мероприятие никто не записался!")
    else:
        await message.answer(f"Количество записавшихся : {list(await getCountOfSignUp(event))[0]}\n\n{await getComeUsers(event)}\n\n{await getWontComeUsers(event)}")

