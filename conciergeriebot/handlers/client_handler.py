# handlers/client_handler.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import add_client, get_all_clients

class ClientHandler:
    # États de la conversation
    NOM, PRENOM, TELEPHONE, EMAIL = range(4)

    @staticmethod
    async def start_add_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Démarre le processus d'ajout d'un client."""
        await update.message.reply_text(
            "📝 Ajout d'un nouveau client\n\n"
            "Veuillez entrer le nom du client :"
        )
        return ClientHandler.NOM

    @staticmethod
    async def ask_prenom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Demande le prénom après avoir reçu le nom."""
        context.user_data['nom'] = update.message.text
        await update.message.reply_text("Entrez le prénom du client :")
        return ClientHandler.PRENOM

    @staticmethod
    async def ask_telephone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Demande le téléphone après avoir reçu le prénom."""
        context.user_data['prenom'] = update.message.text
        await update.message.reply_text(
            "Entrez le numéro de téléphone du client :\n"
            "Format: +XX XXXXXXXXX"
        )
        return ClientHandler.TELEPHONE

    @staticmethod
    async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Demande l'email après avoir reçu le téléphone."""
        context.user_data['telephone'] = update.message.text
        await update.message.reply_text(
            "Entrez l'adresse email du client :\n"
            "Format: exemple@email.com"
        )
        return ClientHandler.EMAIL

    @staticmethod
    async def save_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Sauvegarde les informations du client dans la base de données."""
        context.user_data['email'] = update.message.text
        
        try:
            add_client(
                context.user_data['nom'],
                context.user_data['prenom'],
                context.user_data['telephone'],
                context.user_data['email']
            )
            await update.message.reply_text(
                "✅ Client ajouté avec succès !\n\n"
                f"Nom: {context.user_data['nom']}\n"
                f"Prénom: {context.user_data['prenom']}\n"
                f"Téléphone: {context.user_data['telephone']}\n"
                f"Email: {context.user_data['email']}"
            )
        except Exception as e:
            await update.message.reply_text(
                "❌ Erreur lors de l'ajout du client.\n"
                "Veuillez réessayer."
            )
            print(f"Erreur lors de l'ajout du client: {e}")
            
        return ConversationHandler.END

    @staticmethod
    async def list_clients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Affiche la liste de tous les clients."""
        clients = get_all_clients()
        if not clients:
            await update.message.reply_text(
                "Aucun client n'est enregistré pour le moment."
            )
            return

        message = "📋 Liste des clients :\n\n"
        for client in clients:
            message += (
                f"👤 {client[0]} {client[1]}\n"
                f"📞 {client[2]}\n"
                f"📧 {client[3]}\n"
                "───────────────\n"
            )
        
        await update.message.reply_text(message)

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Annule l'opération en cours."""
        await update.message.reply_text(
            "❌ Opération annulée.\n"
            "Retour au menu principal."
        )
        return ConversationHandler.END

    @staticmethod
    def get_client_conversation_handler():
        """Retourne le gestionnaire de conversation pour l'ajout de client."""
        from telegram.ext import MessageHandler, CommandHandler, filters
        
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📝 Ajouter un client$"),
                    ClientHandler.start_add_client
                )
            ],
            states={
                ClientHandler.NOM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ClientHandler.ask_prenom
                    )
                ],
                ClientHandler.PRENOM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ClientHandler.ask_telephone
                    )
                ],
                ClientHandler.TELEPHONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ClientHandler.ask_email
                    )
                ],
                ClientHandler.EMAIL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ClientHandler.save_client
                    )
                ]
            },
            fallbacks=[
                CommandHandler("cancel", ClientHandler.cancel)
            ]
        )