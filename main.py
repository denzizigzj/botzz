import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers import router
from app.database.models import async_main



async def main():
    await async_main()
    load_dotenv()
    bot = Bot('7888361113:AAHQWU7enrY_2ljI63-R2_kuGcw71kiqEIY')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
     

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен!')

