import os

def get_api_token():
    return os.getenv("BOT_TOKEN")

def get_poiskkino_token():
    return os.getenv('KINOPOISK_TOKEN')
