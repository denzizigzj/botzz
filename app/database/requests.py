import httpx
import os

from app.database.models import async_session
from app.database.models import User, Category, Item
from sqlalchemy import select


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_slug: str):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.slug == category_slug))
        if category:
            return await session.scalars(select(Item).where(Item.category == category.id))
        return None

async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))

async def get_course_by_slug(course_slug: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(os.getenv("URL"))
        if response.status_code == 200:
            all_courses = response.json()
            course = next((c for c in all_courses if c["slug"] == course_slug), None)
            if course:
                return course
            else:
                print("Курс не найден.")
                return None
        else:
            print(f"Ошибка при получении курсов: статус {response.status_code}")
            return None