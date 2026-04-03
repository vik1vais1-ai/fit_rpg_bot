import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import Base, engine, SessionLocal
from handlers import start, profile, workout, energy, top, survey
from models import Exercise

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Добавляем упражнения, если их нет
def init_exercises():
    db = SessionLocal()
    try:
        if db.query(Exercise).count() == 0:
            exercises = [
                Exercise(name="Отжимания", attribute="strength", base_xp=10, energy_cost=8, min_reps=10),
                Exercise(name="Приседания", attribute="strength", base_xp=8, energy_cost=6, min_reps=15),
                Exercise(name="Прыжки джампинг джек", attribute="endurance", base_xp=8, energy_cost=7, min_reps=20),
                Exercise(name="Планка (сек)", attribute="endurance", base_xp=12, energy_cost=10, min_reps=30),
                Exercise(name="Наклоны вперёд", attribute="flexibility", base_xp=8, energy_cost=5, min_reps=10),
                Exercise(name="Выпады", attribute="flexibility", base_xp=9, energy_cost=7, min_reps=12),
            ]
            for ex in exercises:
                db.add(ex)
            db.commit()
            print("✅ Добавлены начальные упражнения")
        else:
            print("✅ Упражнения уже есть")
    except Exception as e:
        print(f"Ошибка при добавлении упражнений: {e}")
    finally:
        db.close()

init_exercises()

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
