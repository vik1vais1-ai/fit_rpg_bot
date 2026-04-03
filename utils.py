from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Character, Exercise
from config import ENERGY_RECHARGE_INTERVAL_SEC, ENERGY_RECHARGE_AMOUNT, XP_PER_LEVEL_BASE

def recharge_energy(user: User, db: Session):
    now = datetime.utcnow()
    last = user.last_energy_recharge
    seconds_passed = (now - last).total_seconds()
    recharge_amount = int(seconds_passed // ENERGY_RECHARGE_INTERVAL_SEC) * ENERGY_RECHARGE_AMOUNT
    if recharge_amount > 0:
        user.energy = min(user.energy + recharge_amount, user.max_energy)
        user.last_energy_recharge = now
        db.commit()
    return user.energy

def spend_energy(user: User, cost: int, db: Session):
    if user.energy < cost:
        return False, f"❌ Не хватает энергии! Нужно {cost}, у тебя {user.energy}. Подожди восстановления или купи энергию (/energy)."
    user.energy -= cost
    db.commit()
    return True, f"⚡ −{cost} энергии. Осталось {user.energy}."

def calc_xp_for_exercise(exercise: Exercise, reps_done: int, user_goal: str) -> int:
    ratio = min(reps_done / max(exercise.min_reps, 1), 2.0)
    base_xp = exercise.base_xp
    xp = int(base_xp * ratio)
    goal_mod = {
        'mass': {'strength': 1.2, 'endurance': 0.9, 'flexibility': 0.9},
        'lose': {'strength': 0.9, 'endurance': 1.2, 'flexibility': 0.9},
        'flexibility': {'strength': 0.9, 'endurance': 0.9, 'flexibility': 1.2},
    }.get(user_goal, {}).get(exercise.attribute, 1.0)
    return int(xp * goal_mod)

def add_xp_to_character(character: Character, attr: str, xp: int, db: Session):
    level_attr = f"{attr}_lvl"
    xp_attr = f"{attr}_xp"
    current_lvl = getattr(character, level_attr)
    current_xp = getattr(character, xp_attr)
    new_xp = current_xp + xp
    leveled_up = False
    while new_xp >= current_lvl * XP_PER_LEVEL_BASE:
        new_xp -= current_lvl * XP_PER_LEVEL_BASE
        current_lvl += 1
        leveled_up = True
    setattr(character, level_attr, current_lvl)
    setattr(character, xp_attr, new_xp)
    character.total_xp += xp
    db.commit()
    return current_lvl, leveled_up

def get_attribute_levels(character: Character) -> dict:
    return {
        "strength": character.strength_lvl,
        "endurance": character.endurance_lvl,
        "flexibility": character.flexibility_lvl,
        "mentality": character.mentality_lvl,
    }

def get_next_level_xp(character: Character, attr: str) -> int:
    current_lvl = getattr(character, f"{attr}_lvl")
    current_xp = getattr(character, f"{attr}_xp")
    return current_lvl * XP_PER_LEVEL_BASE - current_xp