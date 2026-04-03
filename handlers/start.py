from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from database import SessionLocal
from models import User, Character
from keyboards import main_keyboard, goal_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    if user:
        await message.answer(f"С возвращением, {user.name}! Выбери действие.", reply_markup=main_keyboard())
    else:
        await message.answer(
            "🌟 Добро пожаловать в Фитнес RPG!\n\nТвой персонаж ждёт. Сначала выбери главную цель:",
            reply_markup=goal_keyboard()
        )
    db.close()

@router.callback_query(F.data.startswith("goal_"))
async def set_goal(callback: CallbackQuery):
    goal_map = {"goal_mass": "mass", "goal_lose": "lose", "goal_flexibility": "flexibility"}
    goal = goal_map.get(callback.data)
    if not goal:
        return
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=str(callback.from_user.id)).first()
    if not user:
        user = User(telegram_id=str(callback.from_user.id), name=callback.from_user.first_name, goal=goal)
        db.add(user)
        db.flush()
        character = Character(user_id=user.id)
        db.add(character)
        db.commit()
        await callback.message.edit_text(
            f"🎉 Отлично! Твой персонаж создан. Цель: {goal}. Теперь ты можешь тренироваться.",
            reply_markup=main_keyboard()
        )
    else:
        user.goal = goal
        db.commit()
        await callback.message.edit_text(f"Цель изменена на {goal}.")
    await callback.answer()
    db.close()