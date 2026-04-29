# handlers/search_film.py
from aiogram import Router, types, F
from aiogram.enums import ParseMode

from database import db
from film_searcher import FilmSearcher
from keyboards import get_calc_keyboard, KeyBottons


router = Router()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from html import escape
from aiogram.exceptions import TelegramBadRequest

def build_sources_keyboard(sources: dict | None) -> InlineKeyboardMarkup | None:
    if not sources:
        return None

    buttons = []
    for name, source in sources.items():
        url = source.get("url")
        title = source.get("title", "")
        if url:
            button_text = f"▶️ {name}"
            if title:
                button_text += f" — {title}"
            buttons.append([InlineKeyboardButton(text=button_text, url=url)])

    if not buttons:
        return None

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == KeyBottons.KEYB_FIND_FILM)
async def process_number(message: types.Message):
    await message.answer(
        "🔍 *Введите название фильма или сериала, который хотите найти*\n\n"
        "💡 Совет: __пишите название полностью и без ошибок__\n"
        "🎬 Я постараюсь найти его для вас онлайн!",
        reply_markup=get_calc_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@router.message(~F.text.in_(KeyBottons.all) & ~F.text.startswith("/"))
async def process_number(message: types.Message):
    user_id = message.from_user.id

    try:
        film_to_find = message.text.strip()

        user = db.get_user(user_id)
        if not user:
            await message.answer(
                "❌ Пользователь не найден. Нажмите /start",
                reply_markup=get_calc_keyboard()
            )
            return

        films = user['films']
        films.append(film_to_find)
        db.update_user_numbers(user_id, films)

        db.save_user({
            'user_id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        })

        FS = FilmSearcher()
        film = await FS.find_movie(film_to_find)

        if not film:
            await message.answer(
                "❌ Мы ничего не нашли 😔 \n Варианты: \n — фильм ещё не сняли \n — название введено с ошибкой \n — это был сон, а не кино 🙂",
                reply_markup=get_calc_keyboard()
            )
            return

        MAX_DESCR = 300

        title = escape(film.get("title", "Без названия"))
        year = film.get("year", "—")
        kp = film.get("rating", {}).get("kp") or "—"
        imdb = film.get("rating", {}).get("imdb") or "—"
        descr = escape((film.get("description") or "Описание отсутствует")[:MAX_DESCR])

        text = (
            f"🎬 <b>{title}</b> ({year})\n\n"
            f"⭐ <b>Рейтинг</b>\n"
            f"— КП: <b>{kp}</b>\n"
            f"— IMDb: <b>{imdb}</b>\n\n"
            f"📝 <b>Описание</b>\n"
            f"{descr}..."
            f"\n\n💡 <em>Если вы искали другой фильм, попробуйте написать более точное название "
            f"и проверьте его на ошибки 📝</em>"
        )

        keyboard = build_sources_keyboard(film.get("sources"))

        if film.get("poster"):
            try:
                await message.answer_photo(
                    photo=film["poster"],
                    caption=text[:1024],
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                return
            except TelegramBadRequest:
                pass

        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        await message.answer(
            "❌ Что-то пошло не так… попробуйте ещё раз ❤️",
            reply_markup=get_calc_keyboard()
        )
