from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton,
                           InputMediaPhoto)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_categories, get_category_item

import emoji

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Каталог' + emoji.emojize(":open_book:"))],
        [KeyboardButton(text="Связаться с нами" + emoji.emojize(":telephone_receiver:"))],
        [KeyboardButton(text='Контакты' + emoji.emojize(":globe_with_meridians:")), KeyboardButton(text='О нас' + emoji.emojize(":information:"))]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите, чтобы продолжить'
)

async def contact_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.as_markup()

async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()