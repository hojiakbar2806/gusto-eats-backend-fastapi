from aiogram.filters import Filter
from aiogram import Bot
from aiogram.types import Message

from app.core.config import settings
from app.bot import keyboards as kb


class IsSubscriber(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, bot: Bot) -> bool:
        member = await bot.get_chat_member(chat_id=settings.CHANNEL_ID, user_id=message.from_user.id)
        text = "Siz kanallarga obuna bo'lmadingiz. Iltimos, obuna bo'ling va qayta urinib ko'ring."
        if member.status in ["owner", "member", "creator"]:
            return True
        else:
            await message.answer(text, reply_markup=kb.require_channels())
