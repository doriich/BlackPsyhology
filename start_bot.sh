#!/bin/bash

# Telegram Bot Startup Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing dependencies..."
    venv/bin/pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Please create a .env file with your TELEGRAM_BOT_TOKEN"
    echo "Copy .env.example to .env and add your token:"
    echo "cp .env.example .env"
    echo "Then edit .env to add your TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo "TELEGRAM_BOT_TOKEN is not set in .env file"
        echo "Please add your bot token to the .env file"
        exit 1
    fi
fi

echo "Starting Telegram Bot..."
venv/bin/python bot.py