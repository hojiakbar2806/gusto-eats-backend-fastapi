from aiogram import types, Bot
from aiogram.filters import Filter

from app.crud import get_user_by_chat_id
from app.database.base import get_session
from app.bot import keyboards as kb


class IsRegistered(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        chat_id = message.chat.id
        text = "Iltimos ro'yxatdan o'ting. Buning uchun /register buyrug'ini kiriting"

        async with get_session() as session:
            user = await get_user_by_chat_id(session, chat_id)
            if not user:
                await message.answer(text, reply_markup=kb.delete())
                return False
            return True
