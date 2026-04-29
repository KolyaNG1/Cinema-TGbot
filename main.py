# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import API_TOKEN
from database import db
from keyboards import get_calc_keyboard
from handlers import (
    start_router,
    search_film_router,
    manage_numbers_router,
    help_router,
)


async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(search_film_router)
    dp.include_router(manage_numbers_router)

    #
    # @dp.message()
    # async def handle_unknown(message):
    #     await message.answer(
    #         "🤔 Неизвестная команда! \n Напишите /help",
    #         reply_markup=get_calc_keyboard()
    #     )

    print(f"🧮 Синема-бот с БД запущен...")
    print(f"📁 База данных: {db.db_name}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
