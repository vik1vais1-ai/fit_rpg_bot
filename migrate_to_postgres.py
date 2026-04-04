import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# --- 1. ПОДКЛЮЧАЕМСЯ К СТАРОЙ БАЗЕ (SQLite) ---
print("🔍 Подключаюсь к старой SQLite базе...")
sqlite_engine = create_engine('sqlite:///./fit_rpg.db')
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

# --- 2. ПОДКЛЮЧАЕМСЯ К НОВОЙ БАЗЕ (PostgreSQL) ---
if len(sys.argv) != 2:
    print("Пожалуйста, укажите DATABASE_URL PostgreSQL как аргумент командной строки.")
    print("Пример: python migrate_to_postgres.py 'postgresql://...'")
    sys.exit(1)

postgres_url = sys.argv[1].strip()
print("🐘 Подключаюсь к новой PostgreSQL базе...")
postgres_engine = create_engine(postgres_url, pool_pre_ping=True)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_session = PostgresSession()

# --- 3. СОЗДАЁМ СТРУКТУРУ ТАБЛИЦ В POSTGRESQL ---
print("🛠️ Создаю структуру таблиц в PostgreSQL...")
# Импортируем модели, чтобы SQLAlchemy знал, какие таблицы создавать
from models import Base, User, Character, Workout, WorkoutExercise, Exercise, SurveyResult, UserAttribute
Base.metadata.create_all(bind=postgres_engine)

# --- 4. ПОЛУЧАЕМ СПИСОК ТАБЛИЦ ИЗ SQLite ---
sqlite_inspector = inspect(sqlite_engine)
sqlite_tables = sqlite_inspector.get_table_names()

def migrate_table(model_class, table_name):
    """Переносит данные из одной таблицы в другую"""
    if table_name not in sqlite_tables:
        print(f"⚠️ Таблица '{table_name}' не найдена в SQLite, пропускаю.")
        return

    print(f"📦 Переношу данные из таблицы '{table_name}'...")
    old_data = sqlite_session.query(model_class).all()
    if not old_data:
        print(f"   👀 В таблице '{table_name}' нет данных.")
        return

    for item in old_data:
        exists = postgres_session.query(model_class).filter_by(id=item.id).first()
        if not exists:
            postgres_session.add(item)
        else:
            print(f"   ⚠️ Запись с id={item.id} уже есть, пропускаю.")
    postgres_session.commit()
    print(f"   ✅ Перенесено {len(old_data)} записей.")

# --- 5. ЗАПУСКАЕМ ПЕРЕНОС (ПОРЯДОК ВАЖЕН!) ---
print("\n🚀 Начинаю перенос данных...")

migrate_table(Exercise, 'exercises')
migrate_table(User, 'users')
migrate_table(Character, 'characters')
migrate_table(Workout, 'workouts')
migrate_table(WorkoutExercise, 'workout_exercises')
migrate_table(SurveyResult, 'survey_results')
migrate_table(UserAttribute, 'user_attributes')

# --- 6. ПРОВЕРКА ---
print("\n✨ Проверяю количество записей в PostgreSQL...")
for table_name in ['users', 'characters', 'workouts', 'exercises']:
    if table_name in postgres_engine.table_names():
        result = postgres_session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        print(f"   📊 Таблица '{table_name}': {result} записей.")
    else:
        print(f"   ⚠️ Таблица '{table_name}' не создана.")

print("\n🎉 Миграция успешно завершена!")
print("➡️ Теперь обнови переменную DATABASE_URL на Render и перезапусти бота.")

sqlite_session.close()
postgres_session.close()
