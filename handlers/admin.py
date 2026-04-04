from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import SessionLocal as SQLiteSession
from models import User, Character, Workout, WorkoutExercise, Exercise, SurveyResult, UserAttribute
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

router = Router()

# ID твоего Telegram (замени на свой)
ADMIN_ID = 1065961610  # 👈 ВСТАВЬ СВОЙ ID (можно узнать у @userinfobot)

@router.message(Command("migrate_db"))
async def migrate_to_postgres(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав.")
        return

    await message.answer("🔄 Начинаю миграцию из SQLite в PostgreSQL...")

    # 1. Подключаемся к SQLite (текущая база)
    sqlite_engine = create_engine('sqlite:///./fit_rpg.db')
    SQLiteSessionLocal = sessionmaker(bind=sqlite_engine)
    sqlite_db = SQLiteSessionLocal()

    # 2. Подключаемся к PostgreSQL (из переменной окружения)
    postgres_url = os.environ.get("DATABASE_URL")
    if not postgres_url:
        await message.answer("❌ Переменная DATABASE_URL не установлена.")
        sqlite_db.close()
        return

    postgres_engine = create_engine(postgres_url, pool_pre_ping=True)
    PostgresSessionLocal = sessionmaker(bind=postgres_engine)
    postgres_db = PostgresSessionLocal()

    # 3. Создаём таблицы в PostgreSQL (если ещё нет)
    from models import Base
    Base.metadata.create_all(bind=postgres_engine)

    # 4. Переносим данные
    models_list = [
        (Exercise, 'exercises'),
        (User, 'users'),
        (Character, 'characters'),
        (Workout, 'workouts'),
        (WorkoutExercise, 'workout_exercises'),
        (SurveyResult, 'survey_results'),
        (UserAttribute, 'user_attributes'),
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
    await message.answer("🎉 Миграция завершена! Теперь бот использует PostgreSQL. Можно перезапустить сервис вручную.")

