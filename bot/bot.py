import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
#from ..config import BOT_TOKEN


from handlers import user_handler

TOKEN = "7714704448:AAG-vX5NOkRbr9dGp4LLthTfTojqzb1tCTM"
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(user_handler.router)

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())