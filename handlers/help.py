# handlers/help.py
from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command

from database import db
from keyboards import get_calc_keyboard, KeyBottons

router = Router()

@router.message(F.text == KeyBottons.KEYB_HELP)
@router.message(Command("help"))
async def show_help(message: types.Message):
    user_data = {
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    db.save_user(user_data)

    help_text = (
        "🎬 *CINEMA BOT — ПОМОЩЬ*\n\n"

        "🔍 *Как искать фильмы:*\n"
        "1. Нажмите *🔍 Найти фильм*\n"
        "2. Введите название фильма или сериала\n"
        "3. Бот подберёт информацию и ссылки для просмотра\n\n"

        "📌 *Что умеет бот:*\n"
        "• 🎞 Показывает описание фильма\n"
        "• ⭐ Отображает рейтинги (Кинопоиск / IMDb)\n"
        "• 🖼 Показывает постер\n"
        "• ▶️ Даёт ссылки для просмотра\n\n"

        "🧭 *Кнопки управления:*\n"
        "• 🔍 *Найти фильм* — поиск по названию\n"
        "• 📋 *История поиска* — все фильмы, которые вы искали\n"
        "• ❌ *Удалить последний фильм из истории* — шаг назад\n"
        "• 🧹 *Очистить всё* — очистить историю поиска\n"
        "• ℹ️ *Помощь* — это сообщение\n\n"

        "🍿 *Приятного просмотра!*"
    )

    await message.answer(
        help_text,
        reply_markup=get_calc_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
