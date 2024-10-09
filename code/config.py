import os
from pathlib import Path
from dotenv import dotenv_values

PROJECT_PATH = Path(__file__).parent.parent
ENV_PATH = PROJECT_PATH / ".env"
config_env = dotenv_values(ENV_PATH)

BOT_API = os.environ.get(
    "BOT_API", default=config_env.get("BOT_API"))
ADMIN_CHAT_ID = os.environ.get(
    "ADMIN_CHAT_ID", default=config_env.get("ADMIN_CHAT_ID"))

# ADMIN_CHAT_ID = config_env.get("ADMIN_CHAT_ID")
ADMIN_CHAT_ID = '..ADMIN_CHAT_ID'
