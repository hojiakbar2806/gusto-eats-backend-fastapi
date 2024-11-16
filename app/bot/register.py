import re

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from psycopg2._psycopg import IntegrityError
from sqlalchemy.future import select

from app.bot import helper
from app.bot import keyboards as kb
from app.bot.state import DeleteUserState, RegisterState
from app.core.hashing import get_password_hash, verify_password
from app.database.base import get_session
from app.database.models import User, Gender

register = Router()

# Regular expression for password validation
password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$')


# State handlers
@register.message(StateFilter(None), Command("register"))
async def register_handler(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    async with get_session() as session:
        stmt = select(User).filter(User.chat_id == chat_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            await message.answer("Siz allaqachon ro'yxatdan o'tgansiz")
            return
        await message.answer("Ismingizni kiriting", reply_markup=kb.delete())
        await state.update_data(chat_id=message.from_user.id)
        await state.set_state(RegisterState.first_name)


@register.message(RegisterState.first_name, F.text)
async def register_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familyangizni kiriting", reply_markup=kb.delete())
    await state.set_state(RegisterState.last_name)


@register.message(RegisterState.last_name, F.text)
async def register_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer(text="Jinsingizni tanlang", reply_markup=kb.gender())
    await state.set_state(RegisterState.gender)


@register.callback_query(RegisterState.gender)
async def register_gender(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    text = (
        "Parol kiriting. Eng kamida 6 belgi ishlatilsin, katta va kichik harflar va raqam ishtirok etishi zarur, "
        "va parolingiz bilan siz bizning saytimizga kirishingiz mumkin bo'ladi"
    )
    await state.update_data(gender=query.data)
    await query.message.answer(text, reply_markup=kb.delete())
    await state.set_state(RegisterState.password)


@register.message(RegisterState.password, lambda message: re.match(password_regex, message.text))
async def register_password(message: types.Message, state: FSMContext):
    await message.delete()
    text = "Telefon raqamingizni kiriting"
    await state.update_data(password=message.text)
    await message.answer(text, reply_markup=kb.share_contact())
    await state.set_state(RegisterState.phone_number)


@register.message(RegisterState.password, lambda message: not re.match(password_regex, message.text))
async def invalid_password_format(message: types.Message):
    text = "Parolda katta harf, kichik harf, va raqam bo'lishi kerak. Eng kami 6 belgi. Iltimos, qaytadan kiriting."
    await message.delete()
    await message.answer(text, reply_markup=kb.delete())


@register.message(RegisterState.phone_number, F.text, lambda message: re.match(r"^998\d{9}$", message.text))
async def register_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Malumotlaringiz saqlansinmi ?", reply_markup=kb.confirm_save_to_database())
    await state.set_state(RegisterState.confirmation)


@register.message(RegisterState.phone_number, F.text, lambda message: not re.match(r"^998\d{9}$", message.text))
async def invalid_phone_number(message: types.Message):
    await message.answer("Telefon raqami noto'g'ri formatda. Iltimos, qaytadan kiriting. Masalan, '998993250628'")


@register.message(RegisterState.phone_number, F.contact)
async def register_phone_number_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    await message.answer("Malumotlaringiz saqlansinmi ?", reply_markup=kb.confirm_save_to_database())
    await state.set_state(RegisterState.confirmation)


@register.message(RegisterState.confirmation, F.text.contains("Bekor qilish"))
async def cancel_register(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    path = user_data.get('profile_pic', None)
    await helper.delete_image(path)
    await state.clear()
    await message.answer("Ro'yxatdan o'tish bekor qilindi", reply_markup=kb.delete())


@register.message(RegisterState.confirmation, F.text.contains("Tahrirlash"))
async def edit(message: types.Message, state: FSMContext):
    await message.answer("Ismingizni kiriting", reply_markup=kb.delete())
    await state.set_state(RegisterState.first_name)


@register.message(RegisterState.confirmation, F.text.contains("Ha"))
async def save_to_database(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        new_user = User(
            chat_id=user_data.get('chat_id'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            gender=Gender[user_data.get("gender")],
            phone_number=int(user_data.get('phone_number')),
            hashed_password=get_password_hash(user_data.get('password'))
        )
        async with get_session() as session:
            session.add(new_user)
            await session.commit()
    except IntegrityError as e:
        await state.clear()
        await message.answer(f"Database error: {e}", reply_markup=kb.main())
    except Exception as e:
        await state.clear()
        await message.answer(f"Unexpected error: {e}", reply_markup=kb.main())
    else:
        await message.answer("Muvafaqiyatli ro'yxatdan o'tdingiz", reply_markup=kb.main())


@register.callback_query(lambda query: query.data == "delete_user", StateFilter(None))
async def delete_user_start(query: types.CallbackQuery, state: FSMContext):
    chat_id = query.from_user.id
    text = "Ma'lumotlaringizni rostan o'chirmoqchimisz?\nEslatib o'taman sizning barcha buyurtma tarixingiz o'chiriladi bu ma'lumotlar menga kerak emas"

    async with get_session() as session:
        stmt = select(User).filter(User.chat_id == chat_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user:
            await query.answer("Foydalanuvchi topilmadi", show_alert=True)
            await state.clear()
            return

    await query.message.delete()
    await state.update_data(user=user)
    await state.set_state(DeleteUserState.confirmation)
    await query.message.answer(text, reply_markup=kb.confirm_delete())


@register.callback_query(StateFilter(DeleteUserState.confirmation))
async def delete_user_confirm(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    if query.data == "delete_user_confirm":
        await query.message.answer("Parolingizni kiriting")
        await state.set_state(DeleteUserState.delete_user)
        return
    await query.message.answer("Gap yo'q endi bemalol foydalanavering qanaqadur g'oyangiz bo'lsa /contact buyrug'ini kiriting", reply_markup=kb.main())


@register.message(StateFilter(DeleteUserState.delete_user), F.text)
async def delete_user_get_password(message: types.Message, state: FSMContext):
    await message.delete()
    user_data = await state.get_data()
    user = user_data.get("user")

    if not verify_password(message.text, user.hashed_password):
        await message.answer("Parol noto'g'ri")
    else:
        async with get_session() as session:
            try:
                await session.delete(user)
                await session.commit()
            except IntegrityError as e:
                await message.answer(f"Database error: {e}", reply_markup=kb.main())
            except Exception as e:
                await message.answer(f"Unexpected error: {e}", reply_markup=kb.main())
            else:
                await message.answer("Ma'lumotlaringiz o'chirildi", reply_markup=kb.main())
            finally:
                await session.close()

    await state.clear()
