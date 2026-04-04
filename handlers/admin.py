from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from database import SessionLocal as SQLiteSession
from models import User, Character, Workout, WorkoutExercise, Exercise, Base
# SurveyResult и UserAttribute временно убраны, если их нет в models — добавь позже

router = Router()

# ЗАМЕНИ НА СВОЙ TELEGRAM ID
ADMIN_ID = 1065961610
@router.message(Command("migrate_db"))
async def migrate_to_postgres(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав.")
        return

    await message.answer("🔄 Начинаю миграцию из SQLite в PostgreSQL...")

    # SQLite
    sqlite_engine = create_engine('sqlite:///./fit_rpg.db')
    SQLiteSessionLocal = sessionmaker(bind=sqlite_engine)
    sqlite_db = SQLiteSessionLocal()

    # PostgreSQL
    postgres_url = os.environ.get("DATABASE_URL")
    if not postgres_url:
        await message.answer("❌ Переменная DATABASE_URL не установлена.")
        sqlite_db.close()
        return

    postgres_engine = create_engine(postgres_url, pool_pre_ping=True)
    PostgresSessionLocal = sessionmaker(bind=postgres_engine)
    postgres_db = PostgresSessionLocal()

    # Создаём таблицы в PostgreSQL (только те, что есть в models)
    Base.metadata.create_all(bind=postgres_engine)

    # Список моделей (без SurveyResult и UserAttribute)
    models_list = [
        (Exercise, 'exercises'),
        (User, 'users'),
        (Character, 'characters'),
        (Workout, 'workouts'),
        (WorkoutExercise, 'workout_exercises'),
    ]

    for model_class, table_name in models_list:
        old_data = sqlite_db.query(model_class).all()
        if not old_data:
            await message.answer(f"⚠️ Таблица {table_name}: нет данных.")
            continue
        count = 0
        for item in old_data:
            exists = postgres_db.query(model_class).filter_by(id=item.id).first()
            if not exists:
                postgres_db.add(item)
                count += 1
        postgres_db.commit()
        await message.answer(f"✅ Таблица {table_name}: перенесено {count} записей.")

    sqlite_db.close()
    postgres_db.close()
    await message.answer("🎉 Миграция завершена! Теперь бот использует PostgreSQL.")
