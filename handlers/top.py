from aiogram import Router, F
from aiogram.types import Message
from database import SessionLocal
from models import Character, User
from keyboards import main_keyboard

router = Router()

@router.message(F.text == "🏆 Топ")
async def show_top(message: Message):
    db = SessionLocal()
    top_chars = db.query(Character).order_by(Character.total_xp.desc()).limit(10).all()
    if not top_chars:
        await message.answer("Пока нет ни одной тренировки. Будь первым!", reply_markup=main_keyboard())
        db.close()
        return
    text = "🏆 Топ игроков по суммарному XP:\n"
    for idx, char in enumerate(top_chars, 1):
        user = db.query(User).filter_by(id=char.user_id).first()
        name = user.name if user else "Неизвестный"
        text += f"{idx}. {name} — {char.total_xp} XP\n"
    await message.answer(text, reply_markup=main_keyboard())
    db.close()