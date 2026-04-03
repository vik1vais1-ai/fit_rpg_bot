from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime
from database import SessionLocal
from models import User
from utils import recharge_energy
from config import ENERGY_RECHARGE_INTERVAL_SEC
from keyboards import main_keyboard

router = Router()

@router.message(F.text == "⚡ Энергия")
async def show_energy(message: Message):
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    if not user:
        await message.answer("Сначала /start")
        db.close()
        return
    recharge_energy(user, db)
    now = datetime.utcnow()
    last = user.last_energy_recharge
    seconds_since_last = (now - last).total_seconds()
    next_recharge_seconds = ENERGY_RECHARGE_INTERVAL_SEC - (seconds_since_last % ENERGY_RECHARGE_INTERVAL_SEC)
    minutes = int(next_recharge_seconds // 60)
    seconds = int(next_recharge_seconds % 60)
    text = (
        f"⚡ Твоя энергия: {user.energy}/{user.max_energy}\n"
        f"⏳ Следующее восстановление через {minutes} мин {seconds} сек.\n"
        f"💡 Совет: энергия восстанавливается каждые 10 минут."
    )
    await message.answer(text, reply_markup=main_keyboard())
    db.close()