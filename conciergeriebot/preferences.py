# preferences.py

from telegram import Update
from telegram.ext import ContextTypes

async def set_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fonctionnalité de préférence du client en cours de développement...")
    # Ajoutez ici le code pour gérer les préférences
