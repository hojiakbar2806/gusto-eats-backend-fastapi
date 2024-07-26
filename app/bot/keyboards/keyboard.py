from aiogram.types import KeyboardButton, ReplyKeyboardRemove
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.core.config import settings


def confirm():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Ha"))
    rkm_b.add(KeyboardButton(text="Yo'q"))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def main():
    web_app_info = WebAppInfo(text="Order", url=settings.WEBHOOK_URL)
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="🍔 Foods", web_app=web_app_info))
    rkm_b.add(KeyboardButton(text="🧺 My cart"))
    rkm_b.add(KeyboardButton(text="📦 My orders"))
    rkm_b.adjust(2)
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def delete():
    return ReplyKeyboardRemove()


def my_info():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Mening ma'lumotlarim"))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def share_contact():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Telefon raqamni ulashish", request_contact=True))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def share_location():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Manzilni ulashish", request_location=True))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def location_ignore():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Manzilni ulashish", request_location=True))
    rkm_b.add(KeyboardButton(text="Tashlab ketish"))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def location():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Manzilni ulashish", request_location=True))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def ignore():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Tashlab ketish"))
    rkm = rkm_b.as_markup(resize_keyboard=True)
    return rkm


def confirm_save_to_database():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Ha saqlansin"))
    rkm_b.add(KeyboardButton(text="Bekor qilish"))
    rkm_b.add(KeyboardButton(text="Tahrirlash"))
    rkm = rkm_b.adjust(2, True).as_markup(resize_keyboard=True)
    return rkm


def start_counter():
    rkm_b = ReplyKeyboardBuilder()
    rkm_b.add(KeyboardButton(text="Boshlash"))
    rkm = rkm_b.adjust(2, True).as_markup(resize_keyboard=True)
    return rkm
