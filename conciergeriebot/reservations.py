# reservations.py

from telegram import Update
from telegram.ext import ContextTypes

async def add_reservation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Fonctionnalité de réservation en cours de développement...")
    # Ajoutez ici le code pour gérer les réservations
