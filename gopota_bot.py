import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.markdown import hbold, hitalic
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Text, select, func
from emoji import emojize
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Установка логирования
logging.basicConfig(level=logging.INFO)

# Замените 'YOUR_TELEGRAM_BOT_TOKEN_HERE' на токен вашего бота
API_TOKEN = '7887411283:AAHlXMhdOub5TTeHBCU3XvKY0Rgms2Jk6h0'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Константы для пагинации
CATEGORIES_PER_PAGE = 5
COURSES_PER_PAGE = 5

# Переменная состояния бота
bot_active = {}

# SQLAlchemy модели
Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    url = Column(String(255))
    slug = Column(String(255))
    courses = relationship("Course", back_populates="category")

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    type = Column(String(255))
    durations = Column(String(255))
    format = Column(Text)
    cost = Column(String(255))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="courses")

# Создаем асинхронный движок и сессию
DATABASE_URL = "sqlite+aiosqlite:///courses.db"
engine = create_async_engine(
    DATABASE_URL, echo=False
)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Функция для создания клавиатуры главного меню
def get_main_menu_keyboard(is_active: bool):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="📚 Каталог"))
    keyboard.add(KeyboardButton(text="ℹ️ О боте"))
    if is_active:
        keyboard.add(KeyboardButton(text="🛑 Стоп"))
    else:
        keyboard.add(KeyboardButton(text="▶️ Старт"))
    keyboard.adjust(2, 1)  # Располагаем кнопки в два ряда по две кнопки
    return keyboard.as_markup(resize_keyboard=True)

# Функция для получения категорий с пагинацией
async def get_categories(page: int, per_page: int = CATEGORIES_PER_PAGE):
    offset = (page - 1) * per_page
    async with async_session() as session:
        result = await session.execute(
            select(Category).order_by(Category.id).limit(per_page).offset(offset)
        )
        categories = result.scalars().all()
    return categories

# Функция для получения общего количества категорий
async def get_total_categories():
    async with async_session() as session:
        result = await session.execute(
            select(func.count(Category.id))
        )
        total = result.scalar()
    return total

# Функция для получения курсов с пагинацией
async def get_courses(category_id: int, page: int, per_page: int = COURSES_PER_PAGE):
    offset = (page - 1) * per_page
    async with async_session() as session:
        result = await session.execute(
            select(Course).where(Course.category_id == category_id).order_by(Course.id).limit(per_page).offset(offset)
        )
        courses = result.scalars().all()
    return courses

# Функция для получения общего количества курсов в категории
async def get_total_courses(category_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(func.count(Course.id)).where(Course.category_id == category_id)
        )
        total = result.scalar()
    return total

# Функция для получения деталей курса
async def get_course(course_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
    return course

# Обработчик команды /start и кнопки '▶️ Старт'
@dp.message(F.text == "▶️ Старт")
@dp.message(CommandStart())
async def cmd_start(message: Message):
    bot_active[message.chat.id] = True
    keyboard = get_main_menu_keyboard(is_active=True)
    await message.answer("Привет! Я помогу тебе найти интересующие курсы.", reply_markup=keyboard)

# Обработчик команды /stop и кнопки '🛑 Стоп'
@dp.message(F.text == "🛑 Стоп")
@dp.message(Command(commands=["stop"]))
async def cmd_stop(message: Message):
    bot_active[message.chat.id] = False
    keyboard = get_main_menu_keyboard(is_active=False)
    await message.answer("Бот остановлен. Чтобы начать снова, нажмите '▶️ Старт'.", reply_markup=keyboard)

# Обработчик сообщений с кнопок главного меню
@dp.message(F.text)
async def handle_main_menu(message: Message):
    if not bot_active.get(message.chat.id, True):
        await message.answer("Бот остановлен. Чтобы начать снова, нажмите '▶️ Старт'.", reply_markup=get_main_menu_keyboard(is_active=False))
        return
    if message.text == "📚 Каталог":
        await send_categories(message.chat.id, page=1)
    elif message.text == "ℹ️ О боте":
        await message.answer("Этот бот предназначен для просмотра курсов ДПО Московского политеха. Вы можете просматривать категории и курсы, а также получать информацию о них.", reply_markup=get_main_menu_keyboard(is_active=True))
    elif message.text == "🛑 Стоп":
        await cmd_stop(message)
    elif message.text == "▶️ Старт":
        await cmd_start(message)
    else:
        await message.answer("Пожалуйста, выберите действие с помощью клавиатуры ниже.", reply_markup=get_main_menu_keyboard(is_active=bot_active.get(message.chat.id, True)))

# Функция для отправки списка категорий
async def send_categories(chat_id: int, page: int):
    categories = await get_categories(page)
    total_categories = await get_total_categories()
    total_pages = (total_categories + CATEGORIES_PER_PAGE - 1) // CATEGORIES_PER_PAGE

    builder = InlineKeyboardBuilder()

    for category in categories:
        button_text = f"📚 {category.title}"
        callback_data = f"select_category:{category.id}"
        builder.button(text=button_text, callback_data=callback_data)

    builder.adjust(1)  # По одной кнопке в ряд

    # Навигационные кнопки
    navigation_buttons = []
    if page > 1:
        prev_callback = f"navigate_categories:{page - 1}"
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=prev_callback))
    if page < total_pages:
        next_callback = f"navigate_categories:{page + 1}"
        navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=next_callback))

    if navigation_buttons:
        builder.row(*navigation_buttons)

    keyboard = builder.as_markup()

    await bot.send_message(chat_id, emojize("🏷️ <b>Выберите категорию:</b>"), reply_markup=keyboard, parse_mode='HTML')

# Функция для отправки списка курсов
async def send_courses(chat_id: int, category_id: int, page: int):
    courses = await get_courses(category_id, page)
    total_courses = await get_total_courses(category_id)
    total_pages = (total_courses + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE

    builder = InlineKeyboardBuilder()

    for course in courses:
        button_text = f"🎓 {course.title}"
        callback_data = f"view_course:{category_id}:{course.id}"
        builder.button(text=button_text, callback_data=callback_data)

    builder.adjust(1)  # По одной кнопке в ряд

    # Навигационные кнопки
    navigation_buttons = []
    if page > 1:
        prev_callback = f"navigate_courses:{category_id}:{page - 1}"
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=prev_callback))
    if page < total_pages:
        next_callback = f"navigate_courses:{category_id}:{page + 1}"
        navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=next_callback))

    # Кнопка "Назад к категориям"
    back_callback = "back_to_categories"
    navigation_buttons.append(InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=back_callback))

    if navigation_buttons:
        builder.row(*navigation_buttons)

    keyboard = builder.as_markup()

    await bot.send_message(chat_id, emojize("📋 <b>Выберите курс:</b>"), reply_markup=keyboard, parse_mode='HTML')

# Функция для отправки деталей курса
async def send_course_details(chat_id: int, course_id: int, category_id: int):
    course = await get_course(course_id)
    if course:
        title = course.title
        course_type = course.type
        durations = course.durations
        format = course.format
        cost = course.cost

        message_text = emojize(f"🎓 <b>{title}</b>\n\n")
        message_text += f"📖 Тип: {course_type}\n"
        if durations:
            message_text += f"⏳ Длительность: {durations}\n"
        if format:
            message_text += f"📝 Формат: {format}\n"
        if cost:
            message_text += f"💰 Стоимость: {cost}\n"

        builder = InlineKeyboardBuilder()

        back_to_courses_callback = f"back_to_courses:{category_id}:1"
        back_to_categories_callback = "back_to_categories"

        builder.row(
            InlineKeyboardButton(text="🔙 Назад к курсам", callback_data=back_to_courses_callback),
            InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=back_to_categories_callback)
        )

        keyboard = builder.as_markup()

        await bot.send_message(chat_id, message_text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await bot.send_message(chat_id, "Курс не найден.", reply_markup=get_main_menu_keyboard(is_active=bot_active.get(chat_id, True)))

# Обработчик callback_query
@dp.callback_query()
async def callback_query_handler(callback_query: CallbackQuery):
    data = callback_query.data

    if not bot_active.get(callback_query.message.chat.id, True):
        await callback_query.answer("Бот остановлен. Чтобы начать снова, нажмите '▶️ Старт'.")
        return

    if data.startswith("select_category:"):
        # Пользователь выбрал категорию
        category_id = int(data.split(":")[1])
        await callback_query.message.delete()
        await send_courses(callback_query.message.chat.id, category_id, page=1)
        await callback_query.answer()

    elif data.startswith("navigate_categories:"):
        # Пользователь переключил страницу категорий
        page = int(data.split(":")[1])
        await callback_query.message.delete()
        await send_categories(callback_query.message.chat.id, page)
        await callback_query.answer()

    elif data == "back_to_categories":
        # Пользователь вернулся к категориям
        await callback_query.message.delete()
        await send_categories(callback_query.message.chat.id, page=1)
        await callback_query.answer()

    elif data.startswith("navigate_courses:"):
        # Пользователь переключил страницу курсов
        parts = data.split(":")
        category_id = int(parts[1])
        page = int(parts[2])
        await callback_query.message.delete()
        await send_courses(callback_query.message.chat.id, category_id, page)
        await callback_query.answer()

    elif data.startswith("back_to_courses:"):
        # Пользователь вернулся к курсам из деталей курса
        parts = data.split(":")
        category_id = int(parts[1])
        page = int(parts[2])
        await callback_query.message.delete()
        await send_courses(callback_query.message.chat.id, category_id, page)
        await callback_query.answer()

    elif data.startswith("view_course:"):
        # Пользователь выбрал курс
        parts = data.split(":")
        category_id = int(parts[1])
        course_id = int(parts[2])
        await callback_query.message.delete()
        await send_course_details(callback_query.message.chat.id, course_id, category_id)
        await callback_query.answer()

    else:
        await callback_query.answer("Неизвестная команда")

# Основная функция
async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен!')
