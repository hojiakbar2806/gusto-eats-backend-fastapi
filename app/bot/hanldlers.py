from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.future import select

from app.bot import keyboards as kb
from app.db.base import get_session
from app.models import User

main = Router()


@main.message(Command('start'))
async def start_handler(message: Message):
    await message.answer("Assalomu aleykum gusto-eats ga xush kelibsiz", reply_markup=kb.main())


@main.message(Command('my_info'))
async def get_user_info(message: Message):
    chat_id = message.chat.id
    text = "Iltimos ro'yxatdan o'ting. Buning uchun /register buyrug'ini kiriting"

    async with get_session() as session:
        stmt = select(User).filter(User.chat_id == chat_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

    if not user:
        return await message.answer(text, reply_markup=kb.main())

    info_message = (
        f"Your Info: \n"
        f"Ism: {user.first_name}\n"
        f"Familya: {user.last_name}\n"
        f"Telefon no'mer: {user.phone_number}\n"
        f"Jins: {user.gender.value}\n"
    )

    await message.answer(info_message, reply_markup=kb.delete_user())
