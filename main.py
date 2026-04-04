import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import Base, engine
from handlers import start, profile, workout, energy, top, survey

Base.metadata.create_all(bind=engine)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(workout.router)
    dp.include_router(energy.router)
    dp.include_router(top.router)
    dp.include_router(survey.router)
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
