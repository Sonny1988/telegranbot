# handlers/menu_handler.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

class MenuHandler:
    """Gestionnaire du menu principal du bot"""

    # Dans menu_handler.py, modifier le keyboard :
    @staticmethod
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Affiche le menu principal avec toutes les options disponibles"""
        keyboard = [
            ["📝 Ajouter un client"],
            ["📋 Liste des clients"],
            ["📅 Réservation"],
            ["⚙️ Préférences"],
            ["📧 Export Email"],
            ["🗑️ Supprimer client"],
            ["🔄 Menu principal"]
        ]
        
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        welcome_message = (
            "👋 Bienvenue sur le bot de conciergerie !\n\n"
            "Choisissez une option dans le menu ci-dessous :\n\n"
            "📝 Ajouter un client\n"
            "📋 Liste des clients\n"
            "📅 Réservation\n"
            "⚙️ Préférences\n"
            "📧 Export Email\n"
            "🗑️ Supprimer client\n"
            "🔄 Menu principal\n"
        )
        
        await update.message.reply_text(
            text=welcome_message,
            reply_markup=reply_markup
        )

    @staticmethod
    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Affiche l'aide et les instructions d'utilisation"""
        help_text = (
            "💡 Aide et Instructions\n\n"
            "Commandes disponibles :\n"
            "/start - Afficher le menu principal\n"
            "/help - Afficher ce message d'aide\n\n"
            "Pour utiliser le bot :\n"
            "1. Ajoutez d'abord un client\n"
            "2. Faites des réservations pour ce client\n"
            "3. Gérez les préférences selon les besoins\n\n"
            "Pour annuler une opération en cours,\n"
            "utilisez la commande /cancel"
        )
        await update.message.reply_text(help_text)

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Annule l'opération en cours"""
        await update.message.reply_text(
            "❌ Opération annulée.\n"
            "Retour au menu principal."
        )
        await MenuHandler.show_main_menu(update, context)