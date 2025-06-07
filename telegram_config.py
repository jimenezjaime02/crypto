"""Configuration for Telegram bot integration."""
import os

# Telegram Bot credentials (fallback to hard-coded legacy values)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7784674914:AAFKrVJKBWXP2QTP1FiRPLINuspmr9FfpmU')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002312270722')
BOT_NAME = os.getenv('BOT_NAME', 'Price_change_24hr_bot')

__all__ = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'BOT_NAME']
