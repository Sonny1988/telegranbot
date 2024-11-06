# handlers/restaurant_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import get_all_clients
from datetime import datetime

class RestaurantHandler:
    # États de la conversation pour la réservation restaurant
    RESTAURANT_NAME, LAST_NAME, FIRST_NAME, NUM_PEOPLE, DATE, TIME, EMAIL, PHONE = range(8)

    @staticmethod
    async def start_restaurant_reservation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Démarre le processus de réservation de restaurant."""
        await update.message.reply_text(
            "🍽️ Nouvelle réservation restaurant\n\n"
            "Veuillez entrer le nom du restaurant :"
        )
        return RestaurantHandler.RESTAURANT_NAME

    @staticmethod
    async def get_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['restaurant_name'] = update.message.text
        await update.message.reply_text("Entrez le nom de famille :")
        return RestaurantHandler.LAST_NAME

    @staticmethod
    async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['last_name'] = update.message.text
        await update.message.reply_text("Entrez le prénom :")
        return RestaurantHandler.FIRST_NAME

    @staticmethod
    async def get_num_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['first_name'] = update.message.text
        await update.message.reply_text("Entrez le nombre de personnes :")
        return RestaurantHandler.NUM_PEOPLE

    @staticmethod
    async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            num_people = int(update.message.text)
            context.user_data['num_people'] = num_people
            await update.message.reply_text(
                "Entrez la date souhaitée :\n"
                "Format: JJ/MM/AAAA"
            )
            return RestaurantHandler.DATE
        except ValueError:
            await update.message.reply_text(
                "⚠️ Veuillez entrer un nombre valide de personnes."
            )
            return RestaurantHandler.NUM_PEOPLE

    @staticmethod
    async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            date_text = update.message.text
            # Validation de la date
            datetime.strptime(date_text, "%d/%m/%Y")
            context.user_data['date'] = date_text
            await update.message.reply_text(
                "Entrez l'heure souhaitée :\n"
                "Format: HH:MM"
            )
            return RestaurantHandler.TIME
        except ValueError:
            await update.message.reply_text(
                "⚠️ Format de date invalide. Veuillez utiliser le format JJ/MM/AAAA"
            )
            return RestaurantHandler.DATE

    @staticmethod
    async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            time_text = update.message.text
            # Validation de l'heure
            datetime.strptime(time_text, "%H:%M")
            context.user_data['time'] = time_text
            await update.message.reply_text("Entrez l'adresse email :")
            return RestaurantHandler.EMAIL
        except ValueError:
            await update.message.reply_text(
                "⚠️ Format d'heure invalide. Veuillez utiliser le format HH:MM"
            )
            return RestaurantHandler.TIME

    @staticmethod
    async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['email'] = update.message.text
        await update.message.reply_text(
            "Entrez le numéro de téléphone :\n"
            "Format: +XX XXXXXXXXX"
        )
        return RestaurantHandler.PHONE

    @staticmethod
    async def confirm_reservation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['phone'] = update.message.text
        
        # Création du résumé de la réservation
        summary = (
            "📋 Résumé de la réservation :\n\n"
            f"🍽️ Restaurant : {context.user_data['restaurant_name']}\n"
            f"👤 Nom : {context.user_data['last_name']}\n"
            f"👤 Prénom : {context.user_data['first_name']}\n"
            f"👥 Nombre de personnes : {context.user_data['num_people']}\n"
            f"📅 Date : {context.user_data['date']}\n"
            f"⏰ Heure : {context.user_data['time']}\n"
            f"📧 Email : {context.user_data['email']}\n"
            f"📞 Téléphone : {context.user_data['phone']}\n\n"
            "✅ Réservation confirmée !"
        )
        
        await update.message.reply_text(summary)
        
        # TODO: Ajouter la sauvegarde dans la base de données
        
        return ConversationHandler.END

    @staticmethod
    def get_restaurant_conversation_handler():
        """Retourne le gestionnaire de conversation pour les réservations restaurant."""
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^🍽️ Restaurant$"),
                    RestaurantHandler.start_restaurant_reservation
                )
            ],
            states={
                RestaurantHandler.RESTAURANT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_last_name
                    )
                ],
                RestaurantHandler.LAST_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_first_name
                    )
                ],
                RestaurantHandler.FIRST_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_num_people
                    )
                ],
                RestaurantHandler.NUM_PEOPLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_date
                    )
                ],
                RestaurantHandler.DATE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_time
                    )
                ],
                RestaurantHandler.TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_email
                    )
                ],
                RestaurantHandler.EMAIL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.get_phone
                    )
                ],
                RestaurantHandler.PHONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        RestaurantHandler.confirm_reservation
                    )
                ]
            },
            fallbacks=[
                MessageHandler(
                    filters.COMMAND,
                    lambda u, c: ConversationHandler.END
                )
            ]
        )