from aiogram.fsm.state import State, StatesGroup

class WorkoutState(StatesGroup):
    choosing_exercise = State()
    waiting_reps = State()
    after_exercise = State()
    finishing = State()

class SurveyState(StatesGroup):
    waiting_intensity = State()
    waiting_completed = State()
    waiting_feeling = State()
    waiting_hardest = State()
