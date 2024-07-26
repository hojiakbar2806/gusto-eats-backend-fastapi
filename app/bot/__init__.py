import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.bot.hanldlers import main
from app.bot.keyboards import create_cart_product_pagination
from app.bot.order import order
from app.bot.register import register
from app.core.config import settings

bot = Bot(settings.BOT_TOKEN)
dispatch = Dispatcher()
set_update = dispatch._process_update

dispatch.include_router(main)
dispatch.include_router(order)
dispatch.include_router(register)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def set_command():
    await bot.delete_my_commands()
    await bot.set_my_commands([
        BotCommand(command="start", description="Bot ni ishga tushirish"),
        BotCommand(command="register", description="Ro'xatdan o'tish"),
        BotCommand(command="my_info", description="Ma'lumotlaringizni ko'rish"),
    ])
