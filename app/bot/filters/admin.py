from aiogram import types, Bot
from aiogram.filters import Filter

from app.bot import keyboards as kb
from data.base import get_session
from data.config import settings
from data.crud import get_admins_chat_id


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        username = message.from_user.username
        firstname = message.from_user.first_name
        chat_id = message.chat.id
        text = "Sizda bu operatsiya uchun ruxsat yo'q"
        text2 = (f"{chat_id} {username} {firstname}\n"
                 f"Ushbu foydalanuvchi ruxsat berilmagan operatsiya bajarmoqchi")

        async with get_session() as session:
            admins_chat_id = await get_admins_chat_id(session)
        if chat_id != settings.OWNER_ID and chat_id not in admins_chat_id:
            await message.answer(text, reply_markup=kb.delete())
            await bot.send_message(text=text2, chat_id=settings.OWNER_ID, reply_markup=kb.request_permission(chat_id))
            return False
        else:
            return True
