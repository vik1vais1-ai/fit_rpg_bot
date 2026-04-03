from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import SessionLocal
from models import SurveyAnswer, Character, Workout
from utils import add_xp_to_character
from keyboards import survey_intensity_keyboard, survey_completed_keyboard, survey_feeling_keyboard, main_keyboard
from states import SurveyState

router = Router()

async def start_survey(message: Message, workout_id: int, state: FSMContext):
    await state.update_data(workout_id=workout_id)
    await message.answer("Вопрос 1/4: Насколько тяжелой была тренировка? (1 – легко, 5 – очень тяжело)", reply_markup=survey_intensity_keyboard())
    await state.set_state(SurveyState.waiting_intensity)

@router.callback_query(SurveyState.waiting_intensity, F.data.startswith("intensity_"))
async def survey_intensity(callback: CallbackQuery, state: FSMContext):
    intensity = int(callback.data.split("_")[1])
    await state.update_data(intensity=intensity)
    await callback.message.edit_text("Вопрос 2/4: Ты выполнил все запланированные повторения?", reply_markup=survey_completed_keyboard())
    await state.set_state(SurveyState.waiting_completed)
    await callback.answer()

@router.callback_query(SurveyState.waiting_completed, F.data.startswith("completed_"))
async def survey_completed(callback: CallbackQuery, state: FSMContext):
    completed = 1 if callback.data == "completed_yes" else 0
    await state.update_data(completed=completed)
    await callback.message.edit_text("Вопрос 3/4: Как твоё самочувствие?", reply_markup=survey_feeling_keyboard())
    await state.set_state(SurveyState.waiting_feeling)
    await callback.answer()

@router.callback_query(SurveyState.waiting_feeling, F.data.startswith("feeling_"))
async def survey_feeling(callback: CallbackQuery, state: FSMContext):
    feeling = callback.data.split("_")[1]
    await state.update_data(feeling=feeling)
    await callback.message.edit_text("Вопрос 4/4: Какое упражнение было самым сложным? (напиши текстом)")
    await state.set_state(SurveyState.waiting_hardest)
    await callback.answer()

@router.message(SurveyState.waiting_hardest)
async def survey_hardest(message: Message, state: FSMContext):
    hardest = message.text
    data = await state.get_data()
    workout_id = data['workout_id']
    intensity = data['intensity']
    completed = data['completed']
    feeling = data['feeling']
    db = SessionLocal()
    answer = SurveyAnswer(
        workout_id=workout_id,
        q_intensity=intensity,
        q_completed=completed,
        q_feeling=feeling,
        q_hardest_exercise=hardest
    )
    db.add(answer)
    user_workout = db.query(Workout).filter_by(id=workout_id).first()
    if user_workout:
        user_id = user_workout.user_id
        character = db.query(Character).filter_by(user_id=user_id).first()
        add_xp_to_character(character, "mentality", 5, db)
    db.commit()
    db.close()
    await message.answer("🙏 Спасибо за ответы! Твоя ментальность +5 XP.\nВозвращайся завтра для новых тренировок.", reply_markup=main_keyboard())
    await state.clear()
