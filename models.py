from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, index=True)
    name = Column(String)
    goal = Column(String)
    energy = Column(Integer, default=100)
    max_energy = Column(Integer, default=100)
    last_energy_recharge = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    strength_lvl = Column(Integer, default=1)
    strength_xp = Column(Integer, default=0)
    endurance_lvl = Column(Integer, default=1)
    endurance_xp = Column(Integer, default=0)
    flexibility_lvl = Column(Integer, default=1)
    flexibility_xp = Column(Integer, default=0)
    mentality_lvl = Column(Integer, default=1)
    mentality_xp = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    attribute = Column(String)
    base_xp = Column(Integer, default=10)
    energy_cost = Column(Integer, default=8)
    min_reps = Column(Integer, default=5)

class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    total_xp = Column(Integer, default=0)
    energy_spent = Column(Integer, default=0)
    completed = Column(Integer, default=0)

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    reps_done = Column(Integer)
    xp_earned = Column(Integer)

class SurveyAnswer(Base):
    __tablename__ = "survey_answers"
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    q_intensity = Column(Integer)
    q_completed = Column(Integer)
    q_feeling = Column(String)
    q_hardest_exercise = Column(String)
