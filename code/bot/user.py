# Импортируем клавиатуру
import bot.keyboards as kb

# Импортируем недостающие модули и функции
from aiogram import Router,F
from aiogram.types import Message,CallbackQuery
from aiogram.filters import Command,CommandStart,Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup
from database.requests import (addUserInMailing,checkBan,checkEventByName,getDescEventByName,
                               insertSignUpUser,checkSignUp,checkWontCome,getLastFirstNames,
                               updateWontCome)
from re import compile,search

# Чтобы не писать dispatcher 2-й раз заменим его на роутер
user = Router()

# Создаём класс для проверки забанен-ли пользователь
class BannedProtect(Filter):
    async def __call__(self,message : Message):
        return await checkBan(message.from_user.id)

# Создаём класс для проверки мероприятий
class EventCheck(Filter):
    async def __call__(self,message : Message):
        return await checkEventByName(message.text)

# Создаём класс для записи на мероприятие
class EventSign(StatesGroup):
    event = State()
    firstLastNames = State()
    id = State()
    phone = State()
    email = State()
    confirm = State()

# Обработка сообщения от забаненного пользователя
@user.message(BannedProtect())
async def showBannedMessage(message : Message):
    await message.answer("Вы забанены за плохое поведение!")

# Обработаем команду старт 
@user.message(CommandStart())
async def showStartMenu(message : Message):
    # Запускаем функцию для проверки нахождения пользователя в рассылке
    await addUserInMailing(message.from_user.id)
    await message.answer_sticker("CAACAgIAAxkBAAEDJLZlt3nrHgcV-CbOkU3EuAhDVSg4GQACkQ8AAo7aAAFIhPeRyUFm2n40BA")
    await message.answer(f"Добро пожаловать,{message.from_user.first_name}!",reply_markup=kb.userMenu)

# Обработаем кнопку отмены действия
@user.message(F.text == "🚫Отмена")
async def btnCancelClick(message : Message,state : FSMContext):
    await state.set_state(EventSign.event)
    await message.answer("Отменяю действие",reply_markup=kb.eventUnSignUp)

# Обработаем команду айди
@user.message(Command("id"))
async def showUserId(message : Message):
    await message.answer(f"Ваш айди: {message.from_user.id}")

# Обработка кнопки наши контакты
@user.message(F.text == "👤Наши контакты")
async def btnContactsClick(message : Message):
    await message.answer("Наши контакты:",reply_markup=kb.ourContacts)

# Обработка кнопки тех.поддержка
@user.message(F.text == "💻Тех.поддержка")
async def btnSupportClick(message : Message):
    await message.answer("Техническая поддержка:",reply_markup=kb.techSupport)

# Обработка кнопку мероприятия
@user.message(F.text == "🎉Мероприятия")
async def btnEventsClick(message : Message):
    # Проверяем клавиатуру на наличие кнопок
    if await kb.getEventsButtons() is False:
        await message.answer("Нет мероприятий на которые можно записаться!")
    else:
        await message.answer("Запишитесь на интересующие вас мероприятия!",reply_markup=await kb.getEventsButtons())

# Обработка кнопки назад
@user.message(F.text == "👈Назад")
async def showUserMenu(message : Message,state : FSMContext):
    await state.clear()
    await message.answer("Открываю меню",reply_markup=kb.userMenu)

# Обрабокта кнопок с мероприятиями
@user.message(EventCheck())
async def showEventInfo(message : Message, state: FSMContext):
    # проверка записался-ли уже пользователь на мероприятие
    await state.set_state(EventSign.event)
    await state.update_data(event = message.text)
    if await checkSignUp(message.text,message.from_user.id) is None:
        await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")
        await message.answer(f"🎉Название мероприятия : {message.text}\n🎊Описание мероприятия : {(await getDescEventByName(message.text)).description}",reply_markup=kb.eventUnSignUp) 
    else:
        if await checkWontCome(message.text,message.from_user.id) != None:
            await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")
            await message.answer(f"🎉Название мероприятия : {message.text}\n🎊Описание мероприятия : {(await getDescEventByName(message.text)).description}\n📁Ваши данные : {list(await getLastFirstNames(message.text,message.from_user.id))[0]} \n🛎Статус : пойду",reply_markup=kb.eventSignUp)
        else:
            await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")
            await message.answer(f"🎉Название мероприятия : {message.text}\n🎊Описание мероприятия : {(await getDescEventByName(message.text)).description}\n📁Ваши данные : {list(await getLastFirstNames(message.text,message.from_user.id))[0]}\n🛎Статус : не пойду",reply_markup=kb.eventBack)

# Обработаем кнопку отмены записи        
@user.message(F.text == "❌Я не приду",EventSign.event)
async def btnDidntComeClick(message : Message,state : FSMContext):
    data = await state.get_data()
    event = data.get("event")
    if await checkSignUp(event,message.from_user.id) is None:
        await message.answer("Для начала запишитесь на мероприятие!")
    else:
        if await checkWontCome(event,message.from_user.id) is not None:
            await message.answer("Вы точно не пойдёте на мероприятие?",reply_markup=kb.confirmWontCome)
            await state.update_data(User_id = message.from_user.id)
        else:
            await message.answer("Вы уже отменили запись!")

# Обрабоаем нажатие кнопок для отмены записи
@user.callback_query(EventSign.event)
async def confirmaSignUpCallback(callback : CallbackQuery, state : FSMContext):
    if callback.data == "confirmWontCome": 
        data = await state.get_data()
        event = data.get("event")
        id = data.get("User_id")
        await callback.message.delete()
        await updateWontCome(event,id)
        await callback.message.answer("Вы успешно отменили запись!",reply_markup=await kb.getEventsButtons())
        await state.clear()
    else:
        await callback.message.delete()
        await callback.message.answer("Отменяю действие!",reply_markup=kb.eventSignUp)

# Обработаем кнопку выхода из мероприятия
@user.message(F.text == "🔙Назад")
async def showAllEvents(message : Message, state:FSMContext):
    await state.clear()
    await message.answer("Перехожу назад",reply_markup=await kb.getEventsButtons())

# Обработаем кнопку записаться
@user.message(F.text == "📝Записаться",EventSign.event)
async def getUserData(message : Message,state : FSMContext):
    # Провервыч на записался ли уже
    data = await state.get_data()
    event = data.get("event")
    if await checkSignUp(event,message.from_user.id) is None:
        await message.answer("Введите фамилию и имя!\nПример : Иванов Иван",reply_markup=kb.userCancelMarkup)
        await state.set_state(EventSign.firstLastNames)
    else:
        await message.answer("Вы уже записались на это мерпориятие!")

# Ожидаем ввод ф.и от пользователя
@user.message(EventSign.firstLastNames)
async def waitFirstLastNames(message: Message,state:FSMContext):   
    if message.text != None and search(compile("^[а-яёА-ЯЁ]{3,25} [а-яёА-ЯЁ]{3,25}$"),message.text):
        await state.update_data(firstLastNames = message.text)  
        await state.update_data(id = message.from_user.id)
        await message.answer("Введите свой номер телефона!\nПример : +78005553535",reply_markup=kb.userCancelMarkup)
        await state.set_state(EventSign.phone)
    else:
        await message.answer("Некорректные ф.и!\nПопробуйте ещё раз!")

# Ожидаем ввод телефона от пользователя
@user.message(EventSign.phone)
async def waitPhone(message : Message,state : FSMContext):
    if message.text != None and search(compile("^[+]7[0-9]{10}?$"),message.text):
        await state.update_data(phone = message.text)  
        await message.answer("Введите свою почту!\nПример DanilovSemen@gmail.com",reply_markup=kb.userCancelMarkup)
        await state.set_state(EventSign.email)
    else:
        await message.answer("Некорректный номер телефона!\nПопробуйте ещё раз!",reply_markup=kb.userCancelMarkup)

# Ожидаем ввод почты от пользователя
@user.message(EventSign.email)
async def waiiEmail(message : Message,state : FSMContext):
    if message.text != None and search(compile("^[a-zA-Z0-9.]{1,60}@[a-zA-Z]{1,10}.[a-zA-Z]{2,3}$"),message.text):
      await state.update_data(email = message.text)
      data = await state.get_data()
      event = data.get("event")
      FirstLastNames = data.get("firstLastNames")
      phone = data.get("phone")
      email = data.get("email")
      await message.answer(f"Подтвердите запись на мероприятие!\nНазвание мероприятия : {event}\nФамилия и имя : {FirstLastNames}\nНомер телефона : {phone}\nПочта : {email}",reply_markup=kb.confirmSignUp)
      await state.set_state(EventSign.confirm)
    else:
      await message.answer("Некорректная почта!\nПопробуйте ещё раз!")

# Обработаем кнопку для подтверждения/отмены удаления мероприятия
@user.callback_query(EventSign.confirm)
async def confirmaSignUpCallback(callback : CallbackQuery, state : FSMContext):
    if callback.data == "confirmSignUp": # удаляем
        data = await state.get_data()
        event = data.get("event")
        firstLast = data.get("firstLastNames")
        phone = data.get("phone")
        email = data.get("email")
        id = data.get("id")
        await callback.message.delete()
        await insertSignUpUser(event,firstLast,phone,email,id)
        await callback.message.answer("Вы успешно записались!",reply_markup=await kb.getEventsButtons())
        await state.clear()
    else:
        await callback.message.delete()
        await callback.message.answer("Отменяю запись!\nВведите фамилию и имя!",reply_markup=kb.userCancelMarkup)
        await state.set_state(EventSign.firstLastNames)
