# config.py
import os

from get_token import get_api_token

API_TOKEN = get_api_token()
DB_NAME = 'calculator_bot.db'
ADMIN_IDS = [123456789]
DATABASE_PATH = os.getenv("DATABASE_PATH", DB_NAME)
