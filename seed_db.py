from database import SessionLocal, engine, Base
from models import Exercise

Base.metadata.create_all(bind=engine)
db = SessionLocal()

exercises = [
    Exercise(name="Отжимания", attribute="strength", base_xp=10, energy_cost=8, min_reps=10),
    Exercise(name="Приседания", attribute="strength", base_xp=8, energy_cost=6, min_reps=15),
    Exercise(name="Прыжки джампинг джек", attribute="endurance", base_xp=8, energy_cost=7, min_reps=20),
    Exercise(name="Планка (сек)", attribute="endurance", base_xp=12, energy_cost=10, min_reps=30),
    Exercise(name="Наклоны вперёд", attribute="flexibility", base_xp=8, energy_cost=5, min_reps=10),
    Exercise(name="Выпады", attribute="flexibility", base_xp=9, energy_cost=7, min_reps=12),
]

for ex in exercises:
    db.add(ex)
db.commit()
db.close()
print("Упражнения добавлены")
