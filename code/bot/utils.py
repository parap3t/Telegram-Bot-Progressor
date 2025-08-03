import os
import urllib.parse
import qrcode
import pandas as pd
import database.requests as db
import bot.constants.utils as const

from re import search, compile
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from database.models import Event, EventSignUp


def process_id(*, id_: str) -> int | None:
    """
    Преобразует строковый идентификатор в целое число, если он является числом.

    :param id_: Идентификатор в виде строки.
    :return: Идентификатор в виде целого числа, если строка является числом, иначе None.
    """

    if id_ and id_.isdigit():

        id_: int = int(id_)

        return id_


def extract_data_components(*, date_and_time: str) -> tuple:
    """
    Извлекает год, месяц и день из строки, содержащей дату и время.

    :param date_and_time: Строка с датой и временем в формате дд.мм.гггг чч:мм.
    :return: Кортеж с годом, месяцем и днем.
    """

    # дд.мм.гггг
    date = date_and_time.split()[0]
    year = int(date[6:])
    month = int(date[3:5])
    day = int(date[:2])

    return year, month, day


def is_leap_year(*, year: int) -> bool:
    """
    Проверяет, является ли год високосным.

    :param year: Год для проверки.
    :return: True, если год високосный, иначе False.
    """

    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def is_valid_date_and_time(*, date_and_time: str) -> bool:
    """
    Проверяет, является ли строка допустимой датой и временем, и соответствует ли она шаблону.

    :param date_and_time: Строка с датой и временем в формате гггг-мм-дд.
    :return: True, если дата и время действительны, иначе False.
    """

    # Проверяем чтобы строка не была пустой и соответствовала шаблону гггг-мм-дд

    if date_and_time and search(compile(const.DATE_REGEXP), date_and_time):

        last_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        year, month, day = extract_data_components(date_and_time=date_and_time)

        if is_leap_year(year=year):
            last_days_in_month[1] = 29  # Февраль в високосный год

        return day <= last_days_in_month[month - 1]

    return False


def get_events_enumerate(*, events) -> str:
    """
    Возвращает строку с перечислением всех мероприятий и их идентификаторов.

    :param events: Список объектов мероприятий.
    :return: Строка с перечислением идентификаторов и названий мероприятий.
    """

    events_enumerate: str = ""

    for event in events:
        events_enumerate += f"{event.id}. {event.name}\n"

    return events_enumerate


def delete_excel_file_with_participants(*, event_name: str) -> None:
    """
    Удаляет Excel файл с участниками мероприятия.

    :param event_name: Название мероприятия для формирования пути к файлу.
    """

    filepath = os.path.join("report_tables", f"{event_name}.xlsx")

    if os.path.exists(filepath):
        os.remove(filepath)


def delete_qr_codes_by_event_id(*, event_id: int) -> None:
    """
    Удаляет все QR-коды для мероприятия с указанным ID.

    :param event_id: ID мероприятия, для которого нужно удалить QR-коды.
    """

    # Путь к папке с QR-кодами
    qr_codes_directory = 'qr_codes'

    # Проходим по всем файлам в указанной директории
    for filename in os.listdir(qr_codes_directory):

        # Извлекаем айди мероприятия из имени файла
        file_event_id = filename.split('-')[0]
        file_event_id = int(file_event_id)

        # Если айди мероприятия совпадает с переданным параметром, удаляем файл
        if file_event_id == event_id:

            file_path = os.path.join(qr_codes_directory, filename)
            os.remove(file_path)


async def create_report_excel_file(*, event_name: str) -> None:
    """
    Создает Excel отчет с участниками для указанного мероприятия.

    :param event_name: Название мероприятия для создания отчета.
    """
    filepath = os.path.join("report_tables", f"{event_name}.xlsx")
    event_id = (await db.get_event_info_by_name(name=event_name)).id
    signup_people = await db.get_all_event_participants(event_id=event_id)
    people = await process_event_participants(signup_people=signup_people)

    # Приводим данные в объект класса DataFrame
    table = pd.DataFrame(people)

    # Создаём excel файл с нашими данными в текущей папке проекта
    table.to_excel(filepath, sheet_name="Записавшиеся", index=False)
    workbook = load_workbook(filepath)
    sheet = workbook.active

    # Подстраиваем ширину столбца под ширину названия и колонки
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        sheet.column_dimensions[column].width = max_length + 2

    # Добавление границ к ячейкам
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                         bottom=Side(style='thin'))

    for row in sheet.iter_rows():
        for cell in row:
            cell.border = thin_border

    workbook.save(filepath)
    workbook.close()


async def get_event_message(*, event_name) -> str:
    """
    Формирует сообщение с информацией о мероприятии.

    :param event_name: Название мероприятия.
    :return: Строка с описанием мероприятия.
    """

    event_info = await db.get_event_info_by_name(name=event_name)
    event_theme = await db.get_theme_name_by_id(theme_id=event_info.theme_id)
    event_message = (f"🎉Название мероприятия: {event_name}"
                     f"\n🎊Описание: {event_info.description}"
                     f"\n🎯Тематика: {event_theme}"
                     f"\n👥Количество мест: {event_info.users_limit}"
                     f"\n📆Дата и время проведения: {event_info.date_and_time}"
                     f"\n✏️Запись: {'открыта' if event_info.is_signup_open else 'закрыта'}")

    return event_message


def get_message_with_events(*, events: dict) -> str:
    """
    Формирует сообщение со списком мероприятий.

    :param events: Словарь мероприятий.
    :return: Строка с перечислением мероприятий.
    """

    mess: str = ""

    for event in events.keys():

        mess += f"- {event}"
        mess += "\n"

    return mess


async def process_event_participants(*, signup_people) -> dict:
    """
    Обрабатывает список участников мероприятия и формирует данные для отчета.

    :param signup_people: Список участников мероприятия.
    :return: Словарь с данными о каждом участнике.
    """

    participants: dict = {
        "Полное имя": [],
        "Телефон": [],
        "Айди чата": [],
        "Отменил запись": [],
        "Пришёл": []
    }

    for person in signup_people:
        user_chat_id = await db.get_chat_id_from_user_id(user_id=person.user_id)
        user_info = await db.get_info_about_user(chat_id=user_chat_id)
        participants["Полное имя"] += [user_info.full_name]
        participants["Телефон"] += [str(user_info.phone)]
        participants["Айди чата"] += [user_chat_id]
        participants["Отменил запись"] += ["Да" if person.is_signup_canceled else "Нет"]
        participants["Пришёл"] += ["Да" if person.is_arrived else "Нет"]

    return participants


def create_qr(data: str, filename: str) -> str:
    """
    Создает QR-код с переданными данными и сохраняет его в файл.

    :param data: Данные для кодирования в QR-код.
    :param filename: Имя файла для сохранения QR-кода.
    :return: Путь к сохраненному QR-коду.
    """

    # Кодируем данные для URL
    encoded_data = urllib.parse.quote(data)

    # Формируем URL
    url = f"{const.BOT_URL}?text={encoded_data}"

    # Генерация QR-кода
    qr = qrcode.QRCode(
        box_size=10,
        border=4
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Путь для сохранения файла
    base_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.abspath(os.path.join(base_path, '..', 'qr_codes'))
    full_path = os.path.join(folder_path, f"{filename}.png")

    # Создаем и сохраняем изображение
    img = qr.make_image(fill="black", back_color="white")
    img.save(full_path)

    return full_path


async def process_qr(chat_id, event_name) -> str:
    """
    Генерирует QR-код для конкретного пользователя и мероприятия.

    :param chat_id: ID чата пользователя.
    :param event_name: Название мероприятия.
    :return: Путь к сохраненному QR-коду.
    """

    # Получаем данные о пользователе и событии
    user_id = (await db.get_info_about_user(chat_id=chat_id)).id
    event_id = (await db.get_event_info_by_name(name=event_name)).id

    # Генерируем QR с уникальными данными
    return create_qr(data=f"{event_id}-{user_id}", filename=f"{event_id}-{user_id}")


async def process_user_interest(*, user_id: int, event_name: str) -> None:
    """
    Обрабатывает интерес пользователя к тематике мероприятия.

    :param user_id: ID пользователя.
    :param event_name: Название мероприятия.
    """

    event_theme_id = (await db.get_event_info_by_name(name=event_name)).theme_id

    if not await db.is_theme_in_user_interests(theme_id=event_theme_id, user_id=user_id):
        await db.add_user_interest(theme_id=event_theme_id, user_id=user_id)


async def process_user_event_signups(*, user_id: int) -> set:
    """
    Получает список мероприятий, на которые записан пользователь.

    :param user_id: ID пользователя.
    :return: Множество названий мероприятий.
    """

    signup_infos: list[EventSignUp] = await db.get_user_event_signups(user_id=user_id)

    if signup_infos:

        event_ids: list[int] = [signup_info.event_id for signup_info in signup_infos]
        event_infos: list[Event] = await db.get_event_names_by_ids(event_ids=event_ids)
        event_names: set[str] = set(event.name for event in event_infos)

        return event_names

    return None


# Преобразуем список событий в словарь
def events_to_dict(*, events: list[Event]) -> dict:
    """
    Преобразует список событий в словарь с названиями мероприятий и их ID тем.

    :param events: Список объектов мероприятий.
    :return: Словарь с названиями мероприятий и их ID тем.
    """

    event_dict: dict = {}

    for event in events:
        event_dict[event.name] = event.theme_id

    return event_dict


def get_recommend_message(*, mess_with_events: str) -> str:
    """
    Формирует сообщение с рекомендациями по мероприятиям.

    :param mess_with_events: Список мероприятий для отображения в сообщении.
    :return: Сообщение с рекомендациями.
    """

    return ("👋 Привет! Я нашёл для тебя интересные мероприятия!"
            f"\n📌 Вот список:\n{mess_with_events}"
            "Если хочешь узнать подробности, нажми на кнопку \n🎉 Мероприятия.")


def process_interest_groups(interest_groups, user, user_interests) -> None:
    """
    Обрабатывает группы интересов пользователей.

    :param interest_groups: Группы интересов.
    :param user: Пользователь.
    :param user_interests: Интересы пользователя.
    """

    # Извлекаем theme_id из объектов UserInterest
    themes = tuple(sorted(set(interest.theme_id for interest in user_interests)))

    if themes not in interest_groups:
        interest_groups[themes] = []

    interest_groups[themes].append(user)


def get_feedback_message_by_event_status(user_signup, google_link, event_name):
    """
    Формирует сообщение для пользователя в зависимости от его статуса на мероприятии.

    :param user_signup: Данные о записи пользователя.
    :param google_link: Ссылка на форму для отзыва.
    :param event_name: Название мероприятия.
    :return: Сообщение для пользователя.
    """

    result = ""

    if user_signup.is_signup_canceled:
        result = (f"Привет! 👋 \nМы заметили, что вы отменили свою запись на мероприятие"
                  f" под названием {event_name}. Нам очень важно узнать, почему это произошло. Пожалуйста,"
                  "перейдите по ссылке ниже и выберите подходящий вариант в форме."
                  f"\n{google_link}"
                  "\nСпасибо за ваш отзыв! 🙏 \nЭто поможет нам улучшить наши мероприятия. 🎯")

    elif user_signup.is_arrived:
        result = (
            f"Привет! 👋 \nСпасибо, что посетили наше мероприятие под названием {event_name}! 🎉"
            "\nМы очень ценим ваше мнение. Пожалуйста, поделитесь своими впечатлениями,"
            " пройдя по ссылке на форму."
            f"\n{google_link}"
            "\nВаш отзыв поможет нам сделать мероприятия ещё лучше. 💡 \nСпасибо! 🙌")

    else:
        result = (
            f"Привет! 👋 \nМы заметили, что вы не пришли на мероприятие под названием {event_name}, на которое записались."
            " Мы понимаем, что могут быть разные причины. Пожалуйста, помогите нам понять,"
            " что произошло, заполнив форму по ссылке ниже."
            f"\n{google_link}"
            "\nСпасибо за ваш ответ! 😊 \nМы постараемся учесть все ваши пожелания в будущем. 💬"
        )

    return result


def calculate_percentage(total, div):
    """
    Вычисляет процентное соотношение между двумя значениями.

    :param total: Общее количество.
    :param div: Частичное количество.
    :return: Процентное соотношение.
    """

    if div:
        return round((total / div) * 100)

    return div


def get_report_message(participants_count, canceled_signup_percent,
                       unarrived_percent, arrived_percent):
    """
    Формирует сообщение с отчетом по мероприятию.

    :param participants_count: Количество участников.
    :param canceled_signup_percent: Процент отменивших запись.
    :param unarrived_percent: Процент не пришедших.
    :param arrived_percent: Процент пришедших.
    :return: Сообщение с отчетом.
    """

    return (f"👥 Общее количество записавшихся = {participants_count}"
            f"\n❌ Процент людей отменивших запись = {canceled_signup_percent}%"
            f"\n🚫 Процент не пришедших на мероприятие = {unarrived_percent}%"
            f"\n✅ Процент пришедших на мероприятие = {arrived_percent}%")


async def process_report_message(*, event_id: int) -> str:
    """
    Генерирует отчет по мероприятию, используя статистику участников.

    :param event_id: ID мероприятия.
    :return: Сообщение с отчетом по мероприятию.
    """
    participants_count = await db.get_event_participants_count(event_id=event_id)
    canceled_signup_count = await db.get_count_canceled_signups_by_person(event_id=event_id)
    unarrived_count = await db.get_count_person_by_arrival_status(event_id=event_id, arrival_status=const.NOT_ARRIVED)
    arrived_count = await db.get_count_person_by_arrival_status(event_id=event_id, arrival_status=const.ARRIVED)

    canceled_signup_percent = calculate_percentage(participants_count, canceled_signup_count)
    unarrived_percent = calculate_percentage(participants_count, unarrived_count)
    arrived_percent = calculate_percentage(participants_count, arrived_count)

    return get_report_message(participants_count, canceled_signup_percent, unarrived_percent, arrived_percent)