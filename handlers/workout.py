
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import SessionLocal
from models import User, Character, Exercise, Workout, WorkoutExercise
from utils import recharge_energy, spend_energy, calc_xp_for_exercise, add_xp_to_character
from keyboards import workout_choice_keyboard, main_keyboard
from states import WorkoutState, SurveyState
from handlers.survey import start_survey

router = Router()

@router.message(F.text == "🏋️ Тренировка")
async def start_workout(message: Message, state: FSMContext):
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    if not user:
        await message.answer("Сначала /start")
        db.close()
        return
    recharge_energy(user, db)
    if user.energy < 5:
        await message.answer(f"Не хватает энергии ({user.energy}/100). Подожди или купи энергию (/energy).", reply_markup=main_keyboard())
        db.close()
        return
    workout = Workout(user_id=user.id)
    db.add(workout)
    db.commit()
    await state.update_data(workout_id=workout.id)
    exercises = db.query(Exercise).all()
    if not exercises:
        await message.answer("Нет упражнений в базе. Добавьте через админ-команду.")
        db.close()
        return
    await message.answer("Выбери упражнение:", reply_markup=workout_choice_keyboard(exercises))
    await state.set_state(WorkoutState.choosing_exercise)
    db.close()

@router.callback_query(WorkoutState.choosing_exercise, F.data.startswith("ex_"))
async def select_exercise(callback: CallbackQuery, state: FSMContext):
    ex_id = int(callback.data.split("_")[1])
    db = SessionLocal()
    exercise = db.query(Exercise).filter_by(id=ex_id).first()
    if not exercise:
        await callback.answer("Упражнение не найдено")
        db.close()
        return
    await state.update_data(current_exercise_id=ex_id, current_exercise_name=exercise.name, min_reps=exercise.min_reps)
    await callback.message.edit_text(f"🏋️ {exercise.name}\nМинимальное количество для полных XP: {exercise.min_reps}\nСколько раз сделал(а)? (введи число)")
    await state.set_state(WorkoutState.waiting_reps)
    await callback.answer()
    db.close()

@router.message(WorkoutState.waiting_reps)
async def process_reps(message: Message, state: FSMContext):
    try:
        reps = int(message.text)
        if reps <= 0:
            raise ValueError
    except:
        await message.answer("Введи положительное число повторений.")
        return
    data = await state.get_data()
    ex_id = data['current_exercise_id']
    workout_id = data['workout_id']
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    exercise = db.query(Exercise).filter_by(id=ex_id).first()
    character = db.query(Character).filter_by(user_id=user.id).first()
    success, msg = spend_energy(user, exercise.energy_cost, db)
    if not success:
        await message.answer(msg, reply_markup=main_keyboard())
        await state.clear()
        db.close()
        return
    xp = calc_xp_for_exercise(exercise, reps, user.goal)
    new_level, leveled = add_xp_to_character(character, exercise.attribute, xp, db)
    workout_ex = WorkoutExercise(workout_id=workout_id, exercise_id=ex_id, reps_done=reps, xp_earned=xp)
    db.add(workout_ex)
    workout = db.query(Workout).filter_by(id=workout_id).first()
    workout.total_xp += xp
    workout.energy_spent += exercise.energy_cost
    db.commit()
    await message.answer(f"✅ {exercise.name}: {reps} раз → +{xp} XP\n{msg}")
    if leveled:
        await message.answer(f"🎉 Поздравляю! Твой уровень '{exercise.attribute}' повышен до {new_level}!")
    exercises = db.query(Exercise).all()
    await message.answer("Что дальше?", reply_markup=workout_choice_keyboard(exercises))
    await state.update_state(WorkoutState.choosing_exercise)
    db.close()

@router.callback_query(WorkoutState.choosing_exercise, F.data == "finish_workout")
async def finish_workout(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    workout_id = data['workout_id']
    db = SessionLocal()
    workout = db.query(Workout).filter_by(id=workout_id).first()
    if workout:
        workout.completed = 1
        db.commit()
        total_xp = workout.total_xp
        await callback.message.edit_text(f"🏁 Тренировка завершена! Получено всего XP: {total_xp}.\nТеперь ответь на пару вопросов.")
    else:
        await callback.message.edit_text("Тренировка завершена.")
    await callback.answer()
    await start_survey(callback.message, workout_id, state)
    db.close()
