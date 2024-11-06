# client_form.py

from telegram import Update
from telegram.ext import ContextTypes

# Définitions des étapes du formulaire
NOM, PRENOM, TELEPHONE, EMAIL = range(4)

async def start_add_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Entrez le nom du client :")
    return NOM
