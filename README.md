# Telegram Bot for Black Psychology

This bot provides access to black psychology content with a token-based system.

## Features

- `/search` - Find black psychology content from different sources
- `/profile` - View user profile, token balance, and purchase more tokens
- Trial period of 3 days with 10 free tokens
- Token-based payment system (1 token = 10 RUB)

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Telegram bot token:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

3. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

- `/start` - Start the bot and create user profile
- `/help` - Show help message
- `/search` - Search for black psychology content (uses 1 token)
- `/profile` - View profile and token balance

## Payment

After the trial period, users can purchase tokens:
- 10 tokens (100 RUB) - `/buy_10`
- 25 tokens (250 RUB) - `/buy_25`
- 50 tokens (500 RUB) - `/buy_50`
- 100 tokens (1000 RUB) - `/buy_100`

Note: Payment information is hidden for security. Users need to contact the administrator after payment.