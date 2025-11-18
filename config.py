import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('8429262459:AAEYBZKC8a-sonFPkGxO_cmaSf41eNP9au4')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'users.db')

# Payment Configuration
TOKEN_PRICE = 10  # Price per token in RUB
ADMIN_CONTACT = os.getenv('ADMIN_CONTACT', '@admin')

# Trial period configuration
TRIAL_DAYS = 3
TRIAL_TOKENS = 10
