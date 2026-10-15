import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "data/it_learning.db")

# Список Telegram ID администраторов
ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден. Проверьте файл .env")