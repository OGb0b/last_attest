import asyncio
import logging
import os
import sys

# Добавляем родительскую директорию в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import user_handler

TOKEN = "7714704448:AAG-vX5NOkRbr9dGp4LLthTfTojqzb1tCTM"
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(user_handler.router)

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())