# handlers/manage_numbers.py
from aiogram import Router, types, F
from aiogram.enums import ParseMode
from database import db
from keyboards import get_calc_keyboard, KeyBottons

router = Router()

@router.message(F.text == KeyBottons.KEYB_DELETE_LAST)
async def cancel_last(message: types.Message):
    user_id = message.from_user.id

    user_data = {
        'user_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    db.save_user(user_data)

    user = db.get_user(user_id)
    if not user or not user['films']:
        await message.answer(
            "📭 История поиска и так пуста!",
            reply_markup=get_calc_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    films = user['films']
    removed = films.pop()
    db.update_user_numbers(user_id, films)

    if films:
        await message.answer(
            f"🗑️ *Удалено из истории:* `{removed}`\n"
            f"📋 *История:* {', '.join(str(n) for n in films)}",
            reply_markup=get_calc_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.answer(
            "🗑️ *Все фильмы удалены из истории!*\n"
            "Начните заново.",
            reply_markup=get_calc_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )


@router.message(F.text == KeyBottons.KEYB_CLEAR_ALL)
async def clear_all(message: types.Message):
    print('clear all')
    user_id = message.from_user.id
    user_data = {
        'user_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    db.save_user(user_data)

    db.update_user_numbers(user_id, [])

    await message.answer(
        "✨ *Все фильмы удалены из истории!*\n"
        "Можете начать искать новый фильм на вечер.",
        reply_markup=get_calc_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(F.text == KeyBottons.KEYB_SEARCH_HISTORY)
async def show_my_numbers(message: types.Message):
    user_id = message.from_user.id

    user_data = {
        'user_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    db.save_user(user_data)

    user = db.get_user(user_id)

    if user and user['films']:
        films = user['films']

        numbers_text = "\n".join([f"{i + 1}. `{num}`" for i, num in enumerate(films)])

        await message.answer(
            f"📋 *Ваша история поиска:*\n\n"
            f"{numbers_text}\n\n",
            reply_markup=get_calc_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.answer(
            "📭 *В БД пока нет сохраненных фильмов!*",
            reply_markup=get_calc_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
