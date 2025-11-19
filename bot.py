import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from database import Database
from payment import payment_handler
import os
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Bot token (you need to set this as an environment variable)
BOT_TOKEN = os.environ.get('8429262459:AAEYBZKC8a-sonFPkGxO_cmaSf41eNP9au4')

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Create or get user in database
    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
    
    welcome_message = f"""
Привет, {user.first_name}! 👋

Я бот по черной психологии. Используй команду /search для поиска материалов.

У тебя есть {db_user['tokens']} токенов для использования.
После 3 дней использования токены закончатся, и тебе нужно будет пополнить баланс через /profile.

Используй /help для получения списка команд.
    """
    
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
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
    
    update.message.reply_text(help_text)

def search_command(update: Update, context: CallbackContext) -> None:
    """Handle the /search command."""
    user = update.effective_user
    
    # Get or create user
    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
    
    # Check token status
    token_status = db.get_user_token_status(db_user['id'])
    
    if not token_status['is_active']:
        update.message.reply_text(
            "Твой пробный период закончился. Пополни баланс через команду /profile"
        )
        return
    
    if not token_status['has_tokens']:
        update.message.reply_text(
            "У тебя закончились токены. Пополни баланс через команду /profile"
        )
        return
    
    # Use one token
    if db.use_token(db_user['id']):
        db.update_last_access(db_user['id'])
        
        # Simulate search results for black psychology content
        search_results = get_black_psychology_content()
        
        response = f"""
Результаты поиска по черной психологии:

{search_results}

Осталось токенов: {token_status['tokens'] - 1}
Дней до окончания пробного периода: {token_status['days_remaining']}
        """
        
        update.message.reply_text(response)
    else:
        update.message.reply_text(
            "Не удалось использовать токен. Попробуйте позже."
        )

def profile_command(update: Update, context: CallbackContext) -> None:
    """Handle the /profile command."""
    user = update.effective_user
    
    # Get or create user
    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
    
    # Get token status
    token_status = db.get_user_token_status(db_user['id'])
    
    # Format registration date
    created_date = datetime.fromisoformat(db_user['created_at'])
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
    
    # Create payment button
    keyboard = [[InlineKeyboardButton("Пополнить баланс", callback_data="recharge")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(profile_text, reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle button presses."""
    query = update.callback_query
    query.answer()
    
    if query.data == "recharge":
        # Show payment options
        payment_text = """
Выберите количество токенов для покупки:

1 токен = 10 рублей

Варианты:
- 10 токенов (100 рублей) - /buy_10
- 25 токенов (250 рублей) - /buy_25
- 50 токенов (500 рублей) - /buy_50
- 100 токенов (1000 рублей) - /buy_100
        """
        
        query.edit_message_text(text=payment_text)

def buy_tokens(update: Update, context: CallbackContext, amount: int, price: int) -> None:
    """Handle token purchase."""
    user = update.effective_user
    
    # Get user
    db_user = db.get_user(user.id)
    if not db_user:
        update.message.reply_text("Ошибка: пользователь не найден.")
        return
    
    # Generate payment information
    payment_info = payment_handler.generate_payment_info(db_user['id'], amount, price)
    
    update.message.reply_text(payment_info)

def buy_10_command(update: Update, context: CallbackContext) -> None:
    """Handle /buy_10 command."""
    buy_tokens(update, context, 10, 100)

def buy_25_command(update: Update, context: CallbackContext) -> None:
    """Handle /buy_25 command."""
    buy_tokens(update, context, 25, 250)

def buy_50_command(update: Update, context: CallbackContext) -> None:
    """Handle /buy_50 command."""
    buy_tokens(update, context, 50, 500)

def buy_100_command(update: Update, context: CallbackContext) -> None:
    """Handle /buy_100 command."""
    buy_tokens(update, context, 100, 1000)

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

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return
    
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("search", search_command))
    dispatcher.add_handler(CommandHandler("profile", profile_command))
    dispatcher.add_handler(CommandHandler("buy_10", buy_10_command))
    dispatcher.add_handler(CommandHandler("buy_25", buy_25_command))
    dispatcher.add_handler(CommandHandler("buy_50", buy_50_command))
    dispatcher.add_handler(CommandHandler("buy_100", buy_100_command))
    
    # Register button handler
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex('Пополнить баланс'), button_handler))
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
