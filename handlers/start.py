# handlers/start.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from database import db
from keyboards import get_calc_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    user_data = {
        'user_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    db.save_user(user_data)

    user = db.get_user(user_id)

    welcome_text = f"🎬 *Привет, {message.from_user.first_name}!*\n\n" \
                   "Я — *CinemaBot*, твой помощник для поиска фильмов и сериалов.\n\n"

    if user:
        if user['created_at']:
            welcome_text += f"📅 *Ты с нами с:* {user['created_at'][:10]}\n"
        welcome_text += f"🎞 *Сохранённых фильмов:* {len(user['films'])}\n\n"

    welcome_text += "🔍 Просто введи название фильма или сериала, и я покажу, где его можно посмотреть онлайн!\n" \
                    "💡 Используй кнопки ниже для быстрого доступа к истории или помощи."

    await message.answer(
        welcome_text,
        reply_markup=get_calc_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )