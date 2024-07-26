from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def likee(like, dislike):
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(
        text=f"👍 {like}", callback_data='action_like'))
    ikm_b.add(InlineKeyboardButton(
        text=f"👎 {dislike}", callback_data='action_dislike'))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


def require_channels():
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(text="Saodat asri", url="https://t.me/SaodatAsrigaQaytib"))
    ikm_b.add(InlineKeyboardButton(text="Tekshirish", callback_data="check_subscriber"))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


def register_data():
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(
        text="First Name", callback_data="register_edit_firstname"))
    ikm_b.add(InlineKeyboardButton(
        text="Last Name", callback_data="register_edit_lastname"))
    ikm_b.add(InlineKeyboardButton(
        text="Phone Number", callback_data="register_edit_phone"))
    ikm_b.add(InlineKeyboardButton(
        text="Gender", callback_data="register_edit_gender"))
    ikm_b.add(InlineKeyboardButton(
        text="Location", callback_data="register_edit_location"))
    ikm_b.add(InlineKeyboardButton(
        text="Profile Pic", callback_data="register_edit_profilepic"))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


def confirmation_keyboard():
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(text="View Cart", callback_data="view_cart"))
    ikm_b.add(InlineKeyboardButton(text="Buy Now", callback_data="buy"))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


def delete_user():
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(text="O'chirish", callback_data="delete_user"))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


def gender():
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(text="Erkak", callback_data="MALE"))
    ikm_b.add(InlineKeyboardButton(text="Ayol", callback_data="FEMALE"))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


def confirm_delete():
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(text="Ha", callback_data="delete_user_confirm"))
    ikm_b.add(InlineKeyboardButton(text="Fikrimdan qaytdim", callback_data="delete_user_canceled"))
    ikm_b.adjust(2)
    ikm = ikm_b.as_markup()
    return ikm


async def create_cart_product_pagination(page, total_page) -> InlineKeyboardMarkup:
    ikm_b = InlineKeyboardBuilder()
    ikm_b.add(InlineKeyboardButton(text="-", callback_data=f"quantity_decrease_{page}"))
    ikm_b.add(InlineKeyboardButton(text="+", callback_data=f"quantity_increase_{page}"))
    ikm_b.add(InlineKeyboardButton(text="Buyurtm berish", callback_data="buy"))

    if total_page > 1:
        ikm_b.add(InlineKeyboardButton(text="Oldingi", callback_data=f"cart_{page - 1}"))
        ikm_b.add(InlineKeyboardButton(text="Keyingi", callback_data=f"cart_{page + 1}"))
        ikm_b.add(InlineKeyboardButton(text=f"Sahifa {page}/{total_page}", callback_data=f"cartcount_{total_page}_{page}"))

    ikm_b.add(InlineKeyboardButton(text="O'chirish", callback_data=f"delete_product_{page}"))
    ikm_b.adjust(3, 3)
    ikm = ikm_b.as_markup()
    return ikm


async def create_order_product_pagination(total_page, page, order_id):
    ikm_b = InlineKeyboardBuilder()

    if total_page > 1:
        ikm_b.add(
            InlineKeyboardButton(text="Oldingi", callback_data=f"item_{order_id}_{page - 1}"),
            InlineKeyboardButton(text="Keyingi", callback_data=f"item_{order_id}_{page + 1}"),
            InlineKeyboardButton(text=f"Sahifa {page}/{total_page}", callback_data=f"itemcount_{total_page}_{page}")
        )

    ikm = ikm_b.as_markup()
    return ikm


async def create_order_pagination(total_page, page, order_id):
    ikm_b = InlineKeyboardBuilder()

    if total_page > 1:
        ikm_b.add(
            InlineKeyboardButton(text="Oldingi", callback_data=f"order_{order_id}_{page - 1}"),
            InlineKeyboardButton(text="Keyingi", callback_data=f"order_{order_id}_{page + 1}"),
            InlineKeyboardButton(text=f"Sahifa {page}/{total_page}", callback_data=f"ordercount_{total_page}_{page}")
        )

    ikm_b.add(InlineKeyboardButton(text="Buyurtmalar", callback_data=f"items_{order_id}_1"))
    ikm_b.add(InlineKeyboardButton(text="Shikoyat qilish", callback_data="contact_support"))
    ikm_b.adjust(3, 2)
    ikm = ikm_b.as_markup()
    return ikm
