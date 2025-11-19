import logging
from datetime import datetime, timedelta
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from payment import payment_handler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

#токен укажи прямо здесь
TOKEN = "ТУТ"


TRIAL_DAYS = 3
TRIAL_TOKENS = 10


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT,
                tokens INTEGER,
                last_access TEXT
            )
        """)
        self.conn.commit()

    def get_user(self, telegram_id):
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None

    def create_user(self, telegram_id, username, first_name, last_name):
        created_at = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO users (telegram_id, username, first_name, last_name, created_at, tokens, last_access)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (telegram_id, username, first_name, last_name, created_at, TRIAL_TOKENS, created_at))
        self.conn.commit()

        return self.get_user(telegram_id)

    def update_last_access(self, user_id):
        now = datetime.now().isoformat()
        self.cursor.execute("UPDATE users SET last_access = ? WHERE id = ?", (now, user_id))
        self.conn.commit()

    def use_token(self, user_id):
        self.cursor.execute("SELECT tokens FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return False

        tokens = row[0]
        if tokens <= 0:
            return False

        self.cursor.execute("UPDATE users SET tokens = tokens - 1 WHERE id = ?", (user_id,))
        self.conn.commit()
        return True

    def add_tokens(self, user_id, amount):
        self.cursor.execute("UPDATE users SET tokens = tokens + ? WHERE id = ?", (amount, user_id))
        self.conn.commit()

    def get_user_token_status(self, user_id):
        self.cursor.execute("SELECT created_at, tokens FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return None

        created_at_str, tokens = row
        created_at = datetime.fromisoformat(created_at_str)
        days_passed = (datetime.now() - created_at).days
        days_remaining = max(0, TRIAL_DAYS - days_passed)

        return {
            "is_active": days_remaining > 0,
            "has_tokens": tokens > 0,
            "tokens": tokens,
            "days_remaining": days_remaining
        }

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "telegram_id": row[1],
            "username": row[2],
            "first_name": row[3],
            "last_name": row[4],
            "created_at": row[5],
            "tokens": row[6],
            "last_access": row[7]
        }


# Initialize database
db = Database()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    # Create or get user in database
    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    welcome_message = f"""
Привет, {user.first_name}! 👋

Я бот по черной психологии. Используй команду /search для поиска материалов.

У тебя есть {db_user['tokens']} токенов для использования.
После 3 дней использования токены закончатся, и тебе нужно будет пополнить баланс через /profile.

Используй /help для получения списка команд.
    """

    if update.message:
        await update.message.reply_text(welcome_message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
Доступные команды:

/start - Начать работу с ботом
/search - Поиск материалов по черной психологии
/profile - Просмотр профиля и баланса токенов
/help - Показать это сообщение

Каждый поиск расходует 1 токен.
У тебя есть 3 дня и 10 токенов для использования.
После этого нужно пополнить баланс.
    """
    await update.message.reply_text(help_text)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command."""
    user = update.effective_user

    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    token_status = db.get_user_token_status(db_user["id"])

    if not token_status["is_active"]:
        await update.message.reply_text(
            "Твой пробный период закончился. Пополни баланс через команду /profile"
        )
        return

    if not token_status["has_tokens"]:
        await update.message.reply_text(
            "У тебя закончились токены. Пополни баланс через команду /profile"
        )
        return

    if db.use_token(db_user["id"]):
        db.update_last_access(db_user["id"])

        search_results = get_black_psychology_content()

        response = f"""
Результаты поиска по черной психологии:

{search_results}

Осталось токенов: {token_status['tokens'] - 1}
Дней до окончания пробного периода: {token_status['days_remaining']}
        """

        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Не удалось использовать токен. Попробуйте позже.")


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /profile command."""
    user = update.effective_user

    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    token_status = db.get_user_token_status(db_user["id"])

    created_date = datetime.fromisoformat(db_user["created_at"])
    formatted_date = created_date.strftime("%d.%m.%Y")

    profile_text = f"""
👤 Профиль:
Имя: {db_user['first_name'] or 'Не указано'}
Статус: {'Активен' if token_status['is_active'] else 'Не активен'}
Токенов: {db_user['tokens']}
Дата регистрации: {formatted_date}

Дней до окончания пробного периода: {token_status['days_remaining']}

Цена: 1 токен = 10 рублей
    """

    keyboard = [[InlineKeyboardButton("Пополнить баланс", callback_data="recharge")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(profile_text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "recharge":
        payment_text = """
Выберите количество токенов для покупки:

1 токен = 10 рублей

Варианты:
- 10 токенов (100 рублей) - /buy_10
- 25 токенов (250 рублей) - /buy_25
- 50 токенов (500 рублей) - /buy_50
- 100 токенов (1000 рублей) - /buy_100
        """
        await query.edit_message_text(text=payment_text)


async def buy_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int, price: int) -> None:
    """Handle token purchase."""
    user = update.effective_user

    db_user = db.get_user(user.id)
    if not db_user:
        await update.message.reply_text("Ошибка: пользователь не найден.")
        return

    payment_info = payment_handler.generate_payment_info(db_user["id"], amount, price)

    await update.message.reply_text(payment_info)


async def buy_10_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /buy_10 command."""
    await buy_tokens(update, context, 10, 100)


async def buy_25_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /buy_25 command."""
    await buy_tokens(update, context, 25, 250)


async def buy_50_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /buy_50 command."""
    await buy_tokens(update, context, 50, 500)


async def buy_100_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /buy_100 command."""
    await buy_tokens(update, context, 100, 1000)


def get_black_psychology_content() -> str:
    """Simulate fetching black psychology content from different sources."""
    content = """
📚 Материалы по черной психологии:

1. "Темная триада личности" - Психологические черты макиавеллизма, нарциссизма и психопатии.
   Источник: Журнал "Психология и безопасность"

2. "Манипуляции в межличностных отношениях" - Техники психологического влияния.
   Источник: Международный журнал прикладной психологии

3. "Психология обмана и лжи" - Как распознать ложь и манипуляции.
   Источник: Российский журнал психологии

4. "Темные стороны лидерства" - Психология токсичных лидеров.
   Источник: Журнал социальной психологии

5. "Психология насилия" - Психологические аспекты агрессивного поведения.
   Источник: Психологический журнал МГУ

⚠️ Важно: Вся информация предоставлена исключительно в образовательных целях.
    """
    return content


async def recharge_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payment_text = """
Выберите количество токенов для покупки:

1 токен = 10 рублей

Варианты:
- 10 токенов (100 рублей) - /buy_10
- 25 токенов (250 рублей) - /buy_25
- 50 токенов (500 рублей) - /buy_50
- 100 токенов (1000 рублей) - /buy_100
    """
    await update.message.reply_text(payment_text)


def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("buy_10", buy_10_command))
    app.add_handler(CommandHandler("buy_25", buy_25_command))
    app.add_handler(CommandHandler("buy_50", buy_50_command))
    app.add_handler(CommandHandler("buy_100", buy_100_command))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^Пополнить баланс$"), recharge_text_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
