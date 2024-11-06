import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from config import BOT_TOKEN
from handlers.menu_handler import MenuHandler
from handlers.client_handler import ClientHandler
from handlers.reservation_handler import ReservationHandler
from database import init_database
# ... reste du code

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ConciergeBot:
    """Classe principale du bot de conciergerie"""
    
    def __init__(self):
        """Initialise le bot et configure la base de données"""
        self.application = Application.builder().token(BOT_TOKEN).build()
        init_database()  # Initialize database tables
        self.setup_handlers()
        
    def setup_handlers(self):
        """Configure tous les handlers du bot"""
        try:
            # Handler pour la commande start
            self.application.add_handler(
                CommandHandler("start", MenuHandler.show_main_menu)
            )
            
            # Handler pour l'ajout de client
            self.application.add_handler(
                ClientHandler.get_client_conversation_handler()
            )
            
            # Handler pour la liste des clients
            self.application.add_handler(
                MessageHandler(
                    filters.Regex("^📋 Liste des clients$"),
                    ClientHandler.list_clients
                )
            )
            
            # Handler pour les réservations
            self.application.add_handler(
                ReservationHandler.get_reservation_conversation_handler()
            )
            
            # Handler pour les callbacks de réservation
            self.application.add_handler(
                CallbackQueryHandler(
                    ReservationHandler.handle_client_choice,
                    pattern="^client_"
                )
            )
            
            self.application.add_handler(
                CallbackQueryHandler(
                    ReservationHandler.handle_type_choice,
                    pattern="^type_"
                )
            )
            
            # Handler pour les préférences
            self.application.add_handler(
                MessageHandler(
                    filters.Regex("^⚙️ Préférences$"),
                    self.handle_preferences
                )
            )
            
            # Handler pour l'export email
            self.application.add_handler(
                MessageHandler(
                    filters.Regex("^📧 Export Email$"),
                    self.handle_email_export
                )
            )
            
            # Handler pour la suppression de client
            self.application.add_handler(
                MessageHandler(
                    filters.Regex("^🗑️ Supprimer client$"),
                    self.handle_client_deletion
                )
            )

            # Handler pour retour au menu principal
            self.application.add_handler(
                MessageHandler(
                    filters.Regex("^🔄 Menu principal$"),
                    MenuHandler.show_main_menu
                )
            )
            
            # Handler pour les messages non reconnus
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.handle_unknown_message
                )
            )
            
            logger.info("Tous les handlers ont été configurés avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration des handlers: {e}")
            raise

    async def handle_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les préférences utilisateur"""
        await update.message.reply_text(
            "⚙️ La gestion des préférences est en cours de développement..."
        )

    async def handle_email_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère l'export des données par email"""
        await update.message.reply_text(
            "📧 L'export par email est en cours de développement..."
        )

    async def handle_client_deletion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la suppression des clients"""
        await update.message.reply_text(
            "🗑️ La suppression de client est en cours de développement..."
        )

    async def handle_unknown_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les messages non reconnus"""
        await update.message.reply_text(
            "❓ Je ne comprends pas cette commande.\n"
            "Utilisez le menu pour naviguer dans les options disponibles."
        )
        await MenuHandler.show_main_menu(update, context)

    def run(self):
        """Démarre le bot"""
        try:
            print("🤖 Bot démarré... Appuyez sur Ctrl+C pour arrêter.")
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du bot: {e}")
            raise

def main():
    """Point d'entrée principal"""
    try:
        bot = ConciergeBot()
        bot.run()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    main()