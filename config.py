import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

MAX_ENERGY = 100
ENERGY_RECHARGE_INTERVAL_SEC = 600
ENERGY_RECHARGE_AMOUNT = 1
XP_PER_LEVEL_BASE = 100
DEFAULT_ENERGY_COST = 8
DEFAULT_BASE_XP = 10
