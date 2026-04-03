from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка"), KeyboardButton(text="📊 Профиль")],
            [KeyboardButton(text="⚡ Энергия"), KeyboardButton(text="🏆 Топ")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def goal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍖 Набор массы", callback_data="goal_mass")],
        [InlineKeyboardButton(text="🔥 Похудение", callback_data="goal_lose")],
        [InlineKeyboardButton(text="🧘 Гибкость и восстановление", callback_data="goal_flexibility")]
    ])

def workout_choice_keyboard(exercises):
    buttons = []
    for ex in exercises:
        buttons.append([InlineKeyboardButton(text=ex.name, callback_data=f"ex_{ex.id}")])
    buttons.append([InlineKeyboardButton(text="❌ Закончить тренировку", callback_data="finish_workout")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def survey_intensity_keyboard():
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f"intensity_{i}") for i in range(1, 6)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def survey_feeling_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😄 Отлично", callback_data="feeling_great")],
        [InlineKeyboardButton(text="😐 Нормально", callback_data="feeling_normal")],
        [InlineKeyboardButton(text="😩 Устал", callback_data="feeling_tired")],
        [InlineKeyboardButton(text="🤕 Боль", callback_data="feeling_pain")]
    ])

def survey_completed_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="completed_yes")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="completed_no")]
    ])