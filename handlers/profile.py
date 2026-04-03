from aiogram import Router, F
from aiogram.types import Message
from database import SessionLocal
from models import User, Character
from utils import get_attribute_levels, get_next_level_xp
from keyboards import main_keyboard

router = Router()

@router.message(F.text == "📊 Профиль")
async def show_profile(message: Message):
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    if not user:
        await message.answer("Сначала /start")
        db.close()
        return
    character = db.query(Character).filter_by(user_id=user.id).first()
    attrs = get_attribute_levels(character)
    text = (
        f"👤 {user.name} | Цель: {user.goal}\n"
        f"⚡ Энергия: {user.energy}/{user.max_energy}\n"
        f"📊 Атрибуты:\n"
        f"💪 Сила: {attrs['strength']} (до след. уровня: {get_next_level_xp(character,'strength')} XP)\n"
        f"🏃 Выносливость: {attrs['endurance']} ({get_next_level_xp(character,'endurance')} XP)\n"
        f"🧘 Гибкость: {attrs['flexibility']} ({get_next_level_xp(character,'flexibility')} XP)\n"
        f"🧠 Ментальность: {attrs['mentality']} ({get_next_level_xp(character,'mentality')} XP)\n"
        f"✨ Всего XP: {character.total_xp}"
    )
    await message.answer(text, reply_markup=main_keyboard())
    db.close()