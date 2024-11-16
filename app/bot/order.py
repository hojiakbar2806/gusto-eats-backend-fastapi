import json

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.future import select

import app.bot.keyboards as kb
from app.bot.helper import send_current_product, create_order, send_order, send_order_item
from app.database.base import get_session
from app.database.models import Product, User

order = Router()


@order.message(F.content_type == ContentType.WEB_APP_DATA)
async def web_app_data_handler(message: Message, state: FSMContext):
    chat_id = str(message.from_user.id)
    cart_data = json.loads(message.web_app_data.data)
    user_data = (await state.get_data()) or {}
    user_data[chat_id] = {'cart': cart_data["cartItems"]}
    await state.set_data(user_data)
    await message.answer("Mahsulotlar sacatingizga qo'shildi", reply_markup=kb.confirmation_keyboard())


@order.callback_query(lambda c: c.data in ['view_cart', 'buy'])
async def handle_confirmation_callback(query: CallbackQuery, state: FSMContext):
    chat_id = query.from_user.id
    await query.message.delete()

    if query.data == 'view_cart':
        await send_current_product(state=state, chat_id=str(chat_id), query=query)

    elif query.data == 'buy':
        user_data = await state.get_data()
        async with get_session() as session:
            result = await session.execute(select(User).filter(User.chat_id == chat_id))
            user = result.scalars().first()

        if not user:
            await query.message.answer(
                text="Ro'yxatdan o'tmagansiz. Ro'yxatdan o'tib qayta urunib ko'ring. /register",
                reply_markup=kb.main()
            )
            return

        cart = user_data.get(str(chat_id), {}).get('cart', [])

        if not cart:
            await query.message.answer(
                text="Savatingiz bo'sh. Iltimos, savatga mahsulot qo'shing.",
                reply_markup=kb.main()
            )
            return

        new_order = await create_order(user, cart)

        await query.message.answer(
            text=f"Buyurtmangiz muvaffaqiyatli yaratildi. Buyurtma ID: {new_order.id}",
            reply_markup=kb.main()
        )
        await query.bot.send_message(chat_id, text=f"\nBuyurtma ID: {new_order.id}", reply_markup=kb.main())


@order.message(F.text == "🧺 My cart")
async def my_cart(message: Message, state: FSMContext, bot: Bot):
    chat_id = str(message.from_user.id)
    user_data = await state.get_data()
    cart = user_data.get(chat_id, {}).get('cart', [])
    if not cart:
        await message.reply("Savatingiz bo'sh")
        return
    await send_current_product(message=message, state=state, chat_id=chat_id, bot=bot)


@order.message(F.text == "📦 My orders")
async def my_orders(message: Message):
    chat_id = message.from_user.id
    await send_order(msg=message, current=1, chat_id=str(chat_id))


@order.callback_query(lambda query: query.data.startswith('item_') or query.data.startswith('itemcount_'))
async def send_order_items(query: CallbackQuery):
    if query.data.startswith('item_'):
        wh, order_id, page = query.data.split('_')
        await send_order_item(query=query, order_id=order_id, current=int(page), msg_id=query.message.message_id)

    elif query.data.startswith('itemcount_'):
        wh, total_page, current_page = query.data.split('_')
        response_message = f"Jami {total_page} ta sahifa, hozir {current_page}-sahifadasiz"
        await query.answer(response_message)


@order.callback_query(lambda query: query.data.startswith('items_'))
async def send_order_items(query: CallbackQuery):
    await query.message.delete()
    if query.data.startswith('items_'):
        wh, order_id, page = query.data.split('_')
        await send_order_item(query=query, order_id=order_id, current=int(page))


@order.callback_query(lambda query: query.data.startswith('cart_') or query.data.startswith('cartcount_'))
async def process_pagination_callback(query: CallbackQuery, state: FSMContext):
    chat_id = str(query.from_user.id)
    message_id = str(query.message.message_id)
    user_data = await state.get_data()

    if chat_id not in user_data:
        await query.answer("Ma'lumotlar topilmadi")
        return

    if query.data.startswith('cart_'):
        _, page = query.data.split('_')
        user_data[chat_id]['current_page'] = int(page)
        await state.set_data(user_data)
        await send_current_product(query=query, state=state, chat_id=chat_id, msg_id=message_id)

    elif query.data.startswith('cartcount_'):
        _, total_page, current_page = query.data.split('_')
        total_page = int(total_page)
        response_message = f"Jami {total_page} ta sahifa, hozir {current_page}-sahifadasiz"
        await query.answer(response_message)


@order.callback_query(lambda query: query.data.startswith('order_') or query.data.startswith('ordercount_'))
async def process_pagination_callback(query: CallbackQuery):
    chat_id = str(query.from_user.id)
    msg_id = int(query.message.message_id)

    if query.data.startswith('order_'):
        _, order_id, page = query.data.split('_')
        await send_order(query=query, current=int(page), chat_id=chat_id, msg_id=msg_id)

    elif query.data.startswith('ordercount_'):
        wh, total_page, current_page = query.data.split('_')
        response_message = f"Jami {total_page} ta sahifa, hozir {current_page}-sahifadasiz"
        await query.answer(response_message)


@order.callback_query(lambda query: query.data.startswith('quantity_'))
async def process_quantity_callback(query: CallbackQuery, state: FSMContext):
    chat_id = str(query.from_user.id)
    message_id = str(query.message.message_id)
    user_data = await state.get_data()
    index = int(query.data.split('_').pop()) - 1
    cart = user_data.get(chat_id, {}).get('cart', [])

    if not (chat_id in user_data and 0 <= index < len(cart)):
        await query.answer("Ma'lumotlar topilmadi" if chat_id not in user_data else "Savatingiz bo'sh")
        return

    current_product = cart[index]
    product_id = current_product.get('id')

    async with get_session() as session:
        result = await session.execute(select(Product).filter(Product.id == int(product_id)))
        product = result.scalars().first()

        if not product:
            await query.answer("Mahsulot topilmadi")
            return

    if query.data.startswith("quantity_increase"):
        if current_product['quantity'] < product.count_in_stock:
            cart[index]['quantity'] += 1
        else:
            await query.answer("Omborda mahsulot yetarli emas")
            return
    elif query.data.startswith("quantity_decrease"):
        if current_product['quantity'] > 1:
            cart[index]['quantity'] -= 1
        else:
            return

    user_data[chat_id]['cart'][index] = current_product
    await state.set_data(user_data)
    await send_current_product(query=query, state=state, chat_id=chat_id, msg_id=message_id)


@order.callback_query(lambda query: query.data.startswith('delete_product_'))
async def delete_product_from_cart(query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    chat_id = str(query.from_user.id)
    cart = user_data.get(chat_id, {}).get('cart', [])

    if not cart:
        await query.message.delete()
        await query.answer("Ma'lumotlar topilmadi")
        return

    index = int(query.data.split('_').pop()) - 1

    if 0 <= index < len(cart):
        del cart[index]
        user_data[chat_id]['cart'] = cart
        user_data[chat_id]['current_page'] = 1
        await state.set_data(user_data)
        await query.message.delete()
        await query.answer("Mahsulot savatdan o'chirildi")
        await send_current_product(query=query, state=state, chat_id=chat_id)
    else:
        await query.message.delete()
        await query.answer("Mahsulot topilmadi")
