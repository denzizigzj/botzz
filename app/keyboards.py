import httpx
import os
import emoji

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_category_item
from dotenv import load_dotenv

load_dotenv()
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Каталог' + emoji.emojize(":open_book:"))],
        [KeyboardButton(text="Связаться с нами" + emoji.emojize(":telephone_receiver:"))],
        [KeyboardButton(text='Контакты' + emoji.emojize(":globe_with_meridians:")),
         KeyboardButton(text='О нас' + emoji.emojize(":information:"))]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите, чтобы продолжить'
)

async def contact_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.as_markup()


async def categories():
    keyboard = InlineKeyboardBuilder()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(os.getenv("URL"))
            if response.status_code == 200:
                all_courses = response.json()
                for course in all_courses:
                    keyboard.add(InlineKeyboardButton(
                        text=course["title"],
                        callback_data=f"category_{course['slug']}"
                    ))
            else:
                print(f"Ошибка при получении курсов: {response.status_code}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def items(category_slug):
    all_items = await get_category_item(category_slug)
    keyboard = InlineKeyboardBuilder()
    if not all_items:
        keyboard.add(InlineKeyboardButton(text="Нет доступных категорий", callback_data="no_items"))
    else:
        for item in all_items:
            keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

