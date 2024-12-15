import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Text

Base = declarative_base()

# Define the Category model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    url = Column(String(255))
    slug = Column(String(255))
    courses = relationship("Course", back_populates="category")

# Define the Course model
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

async def fetch_json(session, url, params=None):
    async with session.get(url, params=params) as response:
        response.raise_for_status()
        return await response.json()

async def main():
    # Define the database URL (SQLite database)
    DATABASE_URL = "sqlite+aiosqlite:///courses.db"

    # Create the async engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Define the base URL of the microservice
    BASE_URL = "http://localhost:8001/api/v1/courses"  # Adjust the host and port as needed

    async with aiohttp.ClientSession() as session, async_session() as db_session:
        # Fetch all categories
        categories_url = f"{BASE_URL}/categories"
        categories_data = await fetch_json(session, categories_url)

        # Iterate over categories
        for cat_data in categories_data:
            # Create Category instance
            category = Category(
                title=cat_data.get('title'),
                url=cat_data.get('url'),
                slug=cat_data.get('slug')
            )
            db_session.add(category)
            await db_session.flush()  # Flush to get the category.id

            # Fetch courses for the category
            courses_url = f"{BASE_URL}/course"
            params = {'slug': category.slug}
            courses_data = await fetch_json(session, courses_url, params=params)

            # Iterate over courses
            for course_data in courses_data:
                # Create Course instance
                course = Course(
                    title=course_data.get('title'),
                    type=course_data.get('type'),
                    durations=course_data.get('durations'),
                    format=course_data.get('format'),
                    cost=course_data.get('cost'),
                    category_id=category.id
                )
                db_session.add(course)

        # Commit the session
        await db_session.commit()

    # Close the engine
    await engine.dispose()

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
