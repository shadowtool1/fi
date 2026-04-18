import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TOKEN, API_ID, API_HASH
from handlers import (
    start_handler, contact_handler, reg_handler
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

dp.register_message_handler(start_handler, commands=["start"])
dp.register_message_handler(reg_handler, commands=["reg"])
dp.register_message_handler(contact_handler, content_types=types.ContentType.CONTACT)

async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Бот запущен!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
