import logging


# Общая настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# Логгер для общего логирования
logger = logging.getLogger("main_logger")


# Логгер для админских действий
admin_logger = logging.getLogger("admin_logger")
admin_handler = logging.FileHandler("admin_actions.log")
admin_handler.setLevel(logging.INFO)
admin_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
admin_logger.addHandler(admin_handler)


# Логгер для пользовательских действий
user_logger = logging.getLogger("user_logger")
user_handler = logging.FileHandler("user_actions.log")
user_handler.setLevel(logging.INFO)
user_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
user_logger.addHandler(user_handler)


# Логирование Aiogram
logging.getLogger("aiogram").setLevel(logging.INFO)


def log_admin_action(admin_id: int, action: str):
    """
    Записывает действие администратора в лог.

    :param admin_id: Идентификатор администратора.
    :param action: Описание действия администратора.
    :return: None
    """

    admin_logger.info(f"Админ ID: {admin_id} - {action}")

def log_user_action(user_id: int, action: str):
    """
    Записывает действие пользователя в лог.

    :param user_id: Идентификатор пользователя.
    :param action: Описание действия пользователя.
    :return: None
    """
    user_logger.info(f"Пользователь ID: {user_id} - {action}")
