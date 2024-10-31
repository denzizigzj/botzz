from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold, hitalic

from config import ADMIN_CHAT_ID

import emoji
import app.keyboards as kb
import app.database.requests as rq

router = Router()

async def send_welcome(message: Message):
    photo = FSInputFile("photo/mospy.jpg") 
    caption = "Привет, это бот ДПО Московского Политеха"
    await message.answer_photo(photo=photo, caption=caption)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await send_welcome(message)
    await message.answer("Чем могу помочь?",
                          reply_markup=kb.main)

@router.message(F.text == 'Каталог' + emoji.emojize(":open_book:"))
async def catalog(message: Message):
    await message.answer('Выберите категорию товара',
                          reply_markup=await kb.categories())

@router.message(F.text == 'Связаться с нами' + emoji.emojize(":telephone_receiver:"))
async def contact_us(message: Message):
    await message.answer(
        "Напишите ваш вопрос, и администратор ответит вам как можно скорее.\n\nВаш вопрос:",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("Вы можете вернуться на главную, нажав кнопку ниже:",
                          reply_markup=await kb.contact_keyboard())

@router.message(F.text == 'О нас' + emoji.emojize(":information:"))
async def about_us(message: Message):
    await message.answer('Мы предоставляем образовательные услуги и курсы повышения квалификации.\nУзнайте больше по следующей ссылке: https://study.mospolytech.ru/dpo')


@router.message(F.text == 'Контакты' + emoji.emojize(":globe_with_meridians:"))
async def contacts(message: Message):
    await message.answer("Узнайте больше по следующей ссылке: https://study.mospolytech.ru/dpo")

@router.message(F.text)
async def handle_user_message(message: Message):
    if message.chat.type == "private" and message.text not in ['Контакты' + emoji.emojize(":globe_with_meridians:"), 'Связаться с нами' + emoji.emojize(":telephone_receiver:")]:
        user_text = f"{hbold('Сообщение от пользователя')} {message.from_user.username} ({message.from_user.id}):\n\n{hitalic(message.text)}"

        try:
            await message.bot.send_message(ADMIN_CHAT_ID, user_text, parse_mode='HTML')
            await message.answer("Ваше сообщение отправлено администратору.", reply_markup=kb.main)
        except Exception as e:
            print(f"Не удалось отправить сообщение администратору: {e}")
            await message.answer("Не удалось отправить ваше сообщение администратору.")

@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите товар по категории',
                                   reply_markup=await kb.items(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('item_'))
async def handle_name(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали товар')
    await callback.message.answer(f'Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price}₽')

@router.callback_query(F.data == 'to_main')
async def handle_to_main(callback: CallbackQuery):   
    await callback.answer()
    await callback.message.delete() 
    await send_welcome(callback.message)
    await callback.message.answer("Выберите действие:",
                                   reply_markup=kb.main)
