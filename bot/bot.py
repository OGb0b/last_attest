import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage


TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher(storage=MemoryStorage())

async def main():
    bot = Bot(token=TOKEN)
    from handlers import user_handler
    dp.include_router(user_handler.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())