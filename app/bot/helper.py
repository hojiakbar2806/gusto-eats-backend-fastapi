import logging
import os

from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import InputMediaPhoto
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.bot import keyboards as kb
from app.core.config import settings
from app.db.base import get_session
from app.models import Product, Order, OrderStatus, OrderItem, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_state_data(state: FSMContext, chat_id: str, new_data: dict):
    user_data = await state.get_data() or {}
    user_data[chat_id] = {**user_data.get(chat_id, {}), **new_data}
    await state.set_data(user_data)


async def download_image(message, bot):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    os.makedirs('images', exist_ok=True)
    local_file_path = os.path.join(
        'images', f'{message.chat.id}_profile_pic.jpg')
    await bot.download_file(file_path, local_file_path)
    return local_file_path


# Function for deleting images
async def delete_image(path):
    if path:
        if os.path.exists(path):
            os.remove(path)


def clean_string(value):
    if isinstance(value, str):
        return value.strip()
    return value


async def send_current_product(state, chat_id, msg_id=None, message=None, query=None, bot=None):
    user_data = await state.get_data()
    cart = user_data.get(chat_id, {}).get('cart', [])
    current_page = int(user_data.get(chat_id, {}).get('current_page', 1)) - 1

    if not (0 <= current_page < len(cart)):
        if query:
            await query.answer("Mahsulot topilmadi")
        elif message:
            await message.answer("Mahsulot topilmadi")
        return

    current_product = cart[current_page]
    total_pages = len(cart)
    user_data[chat_id]['current_page'] = current_page + 1
    await state.set_data(user_data)

    total_price = await calculate_total(cart)

    caption = f"{current_product['name']} - {current_product['price']} so'm\n{current_product['quantity']} dona\nJami: {total_price}"
    reply_markup = await kb.create_cart_product_pagination(current_page + 1, total_pages, )
    file_id = await check_and_update_file_id(current_product, bot, query)
    await send_product(reply_markup, file_id, query, message, msg_id, chat_id, caption)


async def calculate_total(cart):
    total_price = 0.0

    for item in cart:
        price = item.get('price', 0.0)
        quantity = item.get('quantity', 0.0)
        total_price += price * quantity

    return total_price


async def check_and_update_file_id(product, bot, query=None):
    bot = query.bot if query else bot
    file_id = product.get('file_id')

    if file_id:
        try:
            await bot.get_file(file_id)
            return file_id
        except Exception as e:
            logger.error(f"Error fetching file with ID {file_id}: {e}")
            return await update_file_id_and_product(product['id'], bot)
    else:
        return await update_file_id_and_product(product['id'], bot)


async def update_file_id_and_product(product_id: int, bot):
    async with get_session() as session:
        result = await session.execute(select(Product).filter(Product.id == product_id))
        product = result.scalars().first()

        if not product:
            raise ValueError("Product not found")

        photo = FSInputFile(path=product.image)

        try:
            message = await bot.send_photo(chat_id=settings.OWNER_ID, photo=photo, caption="File id yangilandi !!!")
            new_file_id = message.photo[-1].file_id

            product.telegram_file_id = new_file_id
            session.add(product)
            await session.commit()

            return new_file_id
        except Exception:
            logger.error(f"Error updating file ID")
            raise


async def send_product(ikm, file_id, query=None, msg=None, msg_id=None, chat_id=None, caption=None):
    media = InputMediaPhoto(media=file_id)

    if msg:
        if msg_id:
            await msg.bot.edit_message_media(chat_id=chat_id, msg_id=msg_id, media=media, reply_markup=ikm)
            await msg.bot.edit_message_caption(chat_id=chat_id, msg_id=msg_id, caption=caption, reply_markup=ikm)
        else:
            await msg.answer_photo(photo=file_id, caption=caption, reply_markup=ikm)
    elif query:
        if msg_id:
            await query.message.edit_media(media=media, inline_message_id=msg_id, reply_markup=ikm)
            await query.message.edit_caption(inline_message_id=msg_id, caption=caption, reply_markup=ikm)
        else:
            await query.message.answer_photo(photo=file_id, caption=caption, reply_markup=ikm)


async def send_order(current, chat_id, msg_id=None, msg=None, query=None):
    async with get_session() as session:
        result = await session.execute(select(User).filter(User.chat_id == int(chat_id)))
        user = result.scalars().first()

        if not user:
            await msg.reply("Ro'yxatdan o'tmagansiz. Ro'yxatdan o'tib qayta urunib ko'ring. /register",
                            reply_markup=kb.main())
            return

        result = await session.execute(select(Order).filter(Order.user_id == int(user.id)))
        orders = result.scalars().all()

        if not orders:
            await msg.reply("Sizda hech qanday buyurtma mavjud emas.")
            return

    if 0 <= current - 1 < len(orders):
        item = orders[current - 1]
    else:
        await query.answer("Noto'g'ri sahifa indeksi")
        return

    created_at_formatted = item.created_at.strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"📦 Buyurtma ID: {item.id}\n"
        f"🔄 Status: {item.status.value}\n"
        f"💰 Jami narx: {item.total_price} so'm\n"
        f"📅 Sana: {created_at_formatted}\n"
    )
    ikm = await kb.create_order_pagination(total_page=len(orders), page=current, order_id=item.id)
    if msg:
        if msg_id:
            await msg.bot.edit_message_text(chat_id=chat_id, text=text, message_id=msg_id, reply_markup=ikm)
        else:
            await msg.answer(text=text, reply_markup=ikm)
    elif query:
        if msg_id:
            await query.message.edit_text(text=text, inline_message_id=str(msg_id), reply_markup=ikm)
        else:
            await query.message.answer(text=text, reply_markup=ikm)


async def send_order_item(query, order_id, current, msg_id=None):
    async with get_session() as session:
        result = await session.execute(
            select(OrderItem).options(selectinload(OrderItem.product)).filter(OrderItem.order_id == int(order_id))
        )
        order_items = result.scalars().all()

        if current == 0:
            await query.answer("Siz birinchi sahifadasiz")
            return
        elif len(order_items) == 0:
            await query.answer("Mahsulot topilmadi")
            return

        elif len(order_items) == current - 1:
            await query.answer("Siz oxirgi sahifadasiz")
            return

        item = order_items[current - 1]

        caption = (
            f"{item.product.name} - {item.price} so'm\n"
            f"{item.quantity} dona\n"
            f"Jami: {item.price * item.quantity} so'm"
        )

        file_id = item.product.telegram_file_id
        ikm = await kb.create_order_product_pagination(len(order_items), int(current), int(order_id))
        media = InputMediaPhoto(media=file_id, caption=caption)

        if msg_id:
            await query.message.edit_media(media=media, inline_message_id=str(msg_id))
            await query.message.edit_caption(inline_message_id=str(msg_id), caption=caption, reply_markup=ikm)

        else:
            await query.message.answer_photo(photo=file_id, caption=caption, reply_markup=ikm)


async def create_order(user, cart):
    total_price = await calculate_total(cart)

    new_order = Order(user_id=user.id, total_price=total_price, status=OrderStatus.PENDING)

    async with get_session() as session:
        session.add(new_order)
        await session.commit()

        # Add order items
        for item in cart:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )
            session.add(order_item)

        await session.commit()

    return new_order
