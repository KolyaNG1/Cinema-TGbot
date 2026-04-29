# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from attr import dataclass


@dataclass
class KeyBottons:
    KEYB_FIND_FILM = "🔍 Найти фильм"
    KEYB_CLEAR_ALL = "🧹 Очистить всё"
    KEYB_SEARCH_HISTORY = "📋 История поиска"
    KEYB_HELP = "ℹ️ Помощь"
    KEYB_DELETE_LAST = "❌ Удалить последний фильм из истории"

    all = [KEYB_FIND_FILM, KEYB_CLEAR_ALL, KEYB_SEARCH_HISTORY, KEYB_HELP, KEYB_DELETE_LAST]


def get_calc_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=KeyBottons.KEYB_FIND_FILM)],
            [KeyboardButton(text=KeyBottons.KEYB_DELETE_LAST), KeyboardButton(text=KeyBottons.KEYB_CLEAR_ALL)],
            [KeyboardButton(text=KeyBottons.KEYB_SEARCH_HISTORY), KeyboardButton(text=KeyBottons.KEYB_HELP)]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def remove_keyboard():
    return ReplyKeyboardRemove()
