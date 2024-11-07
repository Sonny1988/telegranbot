from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters
)
from database import get_all_clients, get_client_by_id, add_reservation
import logging
import json

logger = logging.getLogger(__name__)

class ReservationHandler:
    # États pour le processus de réservation
    (CHOIX_CLIENT, CHOIX_TYPE, 
     RESTAURANT_NAME, RESTAURANT_PEOPLE,
     TRANSFER_DEPART, TRANSFER_ARRIVEE, TRANSFER_PEOPLE,
     MONITEUR_LANGUE, MONITEUR_TYPE, MONITEUR_START, MONITEUR_END, 
     MONITEUR_COUNT, MONITEUR_PEOPLE,
     MASSAGE_TYPE, MASSAGE_DUREE,
     SKISERVICE_DETAILS, DATE, TIME) = range(18)

    @staticmethod
    async def start_reservation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Démarre le processus de réservation en affichant la liste des clients"""
        clients = get_all_clients()
        if not clients:
            await update.message.reply_text("Aucun client n'est enregistré. Veuillez d'abord ajouter un client.")
            return ConversationHandler.END

        keyboard = []
        for i, client in enumerate(clients):
            nom, prenom, _, _ = client
            keyboard.append([InlineKeyboardButton(
                f"{nom} {prenom}",
                callback_data=f"client_{i}"
            )])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Sélectionnez un client pour la réservation :",
            reply_markup=reply_markup
        )
        return ReservationHandler.CHOIX_CLIENT

    @staticmethod
    async def handle_client_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Gère la sélection du client et affiche les types de réservation"""
        query = update.callback_query
        await query.answer()
        
        client_index = int(query.data.split('_')[1])
        clients = get_all_clients()
        selected_client = clients[client_index]
        
        context.user_data['selected_client'] = {
            'id': client_index + 1,
            'nom': selected_client[0],
            'prenom': selected_client[1],
            'telephone': selected_client[2],
            'email': selected_client[3]
        }

        keyboard = [
            [InlineKeyboardButton("🍽️ Restaurant", callback_data="type_restaurant")],
            [InlineKeyboardButton("🚗 Transfert", callback_data="type_transfer")],
            [InlineKeyboardButton("💆 Massage", callback_data="type_massage")],
            [InlineKeyboardButton("⛷️ Moniteur", callback_data="type_moniteur")],
            [InlineKeyboardButton("🎿 Ski Service", callback_data="type_ski")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Client sélectionné : {selected_client[0]} {selected_client[1]}\n"
            "Choisissez le type de réservation :",
            reply_markup=reply_markup
        )
        return ReservationHandler.CHOIX_TYPE

    @staticmethod
    async def handle_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Gère la sélection du type de réservation"""
        query = update.callback_query
        await query.answer()
        
        reservation_type = query.data.split('_')[1]
        context.user_data['type_reservation'] = reservation_type

        if reservation_type == 'restaurant':
            await query.edit_message_text("Entrez le nom du restaurant :")
            return ReservationHandler.RESTAURANT_NAME
            
        elif reservation_type == 'transfer':
            await query.edit_message_text("Entrez le lieu de départ :")
            return ReservationHandler.TRANSFER_DEPART
            
        elif reservation_type == 'massage':
            keyboard = [
                [InlineKeyboardButton("Relaxant", callback_data="massage_relaxant")],
                [InlineKeyboardButton("Sportif", callback_data="massage_sportif")],
                [InlineKeyboardButton("Deep Tissue", callback_data="massage_deep")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Choisissez le type de massage :", reply_markup=reply_markup)
            return ReservationHandler.MASSAGE_TYPE
            
        elif reservation_type == 'moniteur':
            keyboard = [
                [InlineKeyboardButton("Français", callback_data="lang_fr")],
                [InlineKeyboardButton("Anglais", callback_data="lang_en")],
                [InlineKeyboardButton("Italien", callback_data="lang_it")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Choisissez la langue du moniteur :", reply_markup=reply_markup)
            return ReservationHandler.MONITEUR_LANGUE
            
        else:  # ski service
            await query.edit_message_text(
                "Décrivez les services souhaités\n"
                "(ex: affûtage des carres, fartage, etc.)"
            )
            return ReservationHandler.SKISERVICE_DETAILS

    # Handlers pour Restaurant
    @staticmethod
    async def handle_restaurant_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['restaurant_name'] = update.message.text
        await update.message.reply_text("Nombre de personnes :")
        return ReservationHandler.RESTAURANT_PEOPLE

    @staticmethod
    async def handle_restaurant_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            num_people = int(update.message.text)
            context.user_data['num_people'] = num_people
            await update.message.reply_text(
                "Entrez la date souhaitée :\n"
                "Format: DD.MM.YY (exemple: 25.12.24)"
            )
            return ReservationHandler.DATE
        except ValueError:
            await update.message.reply_text("⚠️ Veuillez entrer un nombre valide.")
            return ReservationHandler.RESTAURANT_PEOPLE

    # Handlers pour Transfer
    @staticmethod
    async def handle_transfer_depart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['transfer_depart'] = update.message.text
        await update.message.reply_text("Lieu d'arrivée :")
        return ReservationHandler.TRANSFER_ARRIVEE

    @staticmethod
    async def handle_transfer_arrivee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['transfer_arrivee'] = update.message.text
        await update.message.reply_text("Nombre de personnes :")
        return ReservationHandler.TRANSFER_PEOPLE

    @staticmethod
    async def handle_transfer_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            num_people = int(update.message.text)
            context.user_data['num_people'] = num_people
            await update.message.reply_text(
                "Date du transfert :\n"
                "Format: DD.MM.YY (exemple: 25.12.24)"
            )
            return ReservationHandler.DATE
        except ValueError:
            await update.message.reply_text("⚠️ Veuillez entrer un nombre valide.")
            return ReservationHandler.TRANSFER_PEOPLE

    # Handlers pour Moniteur
    @staticmethod
    async def handle_moniteur_langue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        langue = query.data.split('_')[1]
        context.user_data['moniteur_langue'] = langue

        keyboard = [
            [InlineKeyboardButton("Ski", callback_data="sport_ski")],
            [InlineKeyboardButton("Snowboard", callback_data="sport_snowboard")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Choisissez le type de sport :",
            reply_markup=reply_markup
        )
        return ReservationHandler.MONITEUR_TYPE

    @staticmethod
    async def handle_moniteur_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        sport = query.data.split('_')[1]
        context.user_data['moniteur_sport'] = sport
        
        await query.edit_message_text(
            "Date de début des cours :\n"
            "Format: DD.MM.YY (exemple: 25.12.24)"
        )
        return ReservationHandler.MONITEUR_START

    @staticmethod
    async def handle_moniteur_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['date_debut'] = update.message.text
        await update.message.reply_text(
            "Date de fin des cours :\n"
            "Format: DD.MM.YY (exemple: 30.12.24)"
        )
        return ReservationHandler.MONITEUR_END

    @staticmethod
    async def handle_moniteur_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['date_fin'] = update.message.text
        await update.message.reply_text("Nombre de moniteurs souhaité :")
        return ReservationHandler.MONITEUR_COUNT

    @staticmethod
    async def handle_moniteur_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            num_moniteurs = int(update.message.text)
            context.user_data['num_moniteurs'] = num_moniteurs
            await update.message.reply_text("Nombre d'élèves :")
            return ReservationHandler.MONITEUR_PEOPLE
        except ValueError:
            await update.message.reply_text("⚠️ Veuillez entrer un nombre valide.")
            return ReservationHandler.MONITEUR_COUNT

    @staticmethod
    async def handle_moniteur_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            num_people = int(update.message.text)
            context.user_data['num_people'] = num_people
            await update.message.reply_text(
                "Entrez l'heure souhaitée :\n"
                "Format: HHhMM (exemple: 09h00)"
            )
            return ReservationHandler.TIME
        except ValueError:
            await update.message.reply_text("⚠️ Veuillez entrer un nombre valide.")
            return ReservationHandler.MONITEUR_PEOPLE

    # Handlers pour Massage
    @staticmethod
    async def handle_massage_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        massage_type = query.data.split('_')[1]
        context.user_data['massage_type'] = massage_type

        keyboard = [
            [InlineKeyboardButton("30 minutes", callback_data="duree_30")],
            [InlineKeyboardButton("60 minutes", callback_data="duree_60")],
            [InlineKeyboardButton("90 minutes", callback_data="duree_90")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📝 Formulaire de réservation Massage\n"
            f"Type: {massage_type}\n\n"
            "Choisissez la durée du massage:",
            reply_markup=reply_markup
        )
        return ReservationHandler.MASSAGE_DUREE

    @staticmethod
    async def handle_massage_duree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        duree = query.data.split('_')[1]
        context.user_data['massage_duree'] = duree
        
        await query.edit_message_text(
            "Entrez la date souhaitée :\n"
            "Format: DD.MM.YY (exemple: 25.12.24)"
        )
        return ReservationHandler.DATE

    # Handler pour Ski Service
    @staticmethod
    async def handle_skiservice_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['skiservice_details'] = update.message.text
        await update.message.reply_text(
            "Entrez la date souhaitée :\n"
            "Format: DD.MM.YY (exemple: 25.12.24)"
        )
        return ReservationHandler.DATE

    # Handlers communs pour la date et l'heure
    @staticmethod
    async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        date_text = update.message.text
        if not len(date_text.split('.')) == 3:
            await update.message.reply_text(
                "⚠️ Format de date invalide.\n"
                "Veuillez utiliser le format: DD.MM.YY (exemple: 25.12.24)"
            )
            return ReservationHandler.DATE
            
        context.user_data['date'] = date_text
        await update.message.reply_text(
            "Entrez l'heure souhaitée :\n"
            "Format: HHhMM (exemple: 09h00)"
        )
        return ReservationHandler.TIME

    @staticmethod
    async def handle_time_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        time_text = update.message.text
        if 'h' not in time_text:
            await update.message.reply_text(
                "⚠️ Format d'heure invalide.\n"
                "Veuillez utiliser le format: HHhMM (exemple: 09h00)"
            )
            return ReservationHandler.TIME

        context.user_data['time'] = time_text
        
        # Création du résumé de la réservation
        summary = "✅ Réservation confirmée !\n\n"
        
        if context.user_data['type_reservation'] == 'restaurant':
            summary += (
                f"Restaurant: {context.user_data['restaurant_name']}\n"
                f"Nombre de personnes: {context.user_data['num_people']}\n"
            )
        elif context.user_data['type_reservation'] == 'transfer':
            summary += (
                f"Départ: {context.user_data['transfer_depart']}\n"
                f"Arrivée: {context.user_data['transfer_arrivee']}\n"
                f"Nombre de personnes: {context.user_data['num_people']}\n"
            )
        elif context.user_data['type_reservation'] == 'moniteur':
            summary += (
                f"Langue: {context.user_data['moniteur_langue']}\n"
                f"Sport: {context.user_data['moniteur_sport']}\n"
                f"Date début: {context.user_data['date_debut']}\n"
                f"Date fin: {context.user_data['date_fin']}\n"
                f"Nombre de moniteurs: {context.user_data['num_moniteurs']}\n"
                f"Nombre d'élèves: {context.user_data['num_people']}\n"
            )
        elif context.user_data['type_reservation'] == 'massage':
            summary += (
                f"Type: {context.user_data['massage_type']}\n"
                f"Durée: {context.user_data['massage_duree']} minutes\n"
            )
        else:  # ski service
            summary += f"Détails: {context.user_data['skiservice_details']}\n"

        summary += (
            f"\nDate: {context.user_data['date']}\n"
            f"Heure: {time_text}\n"
            f"\nClient: {context.user_data['selected_client']['nom']} "
            f"{context.user_data['selected_client']['prenom']}\n"
            f"Email: {context.user_data['selected_client']['email']}\n"
            f"Téléphone: {context.user_data['selected_client']['telephone']}"
        )

        try:
            add_reservation(
                client_id=context.user_data['selected_client']['id'],
                type_reservation=context.user_data['type_reservation'],
                date_reservation=context.user_data['date'],
                heure_reservation=time_text,
                details=context.user_data
            )
            await update.message.reply_text(summary)
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la réservation: {e}")
            await update.message.reply_text(
                "❌ Une erreur s'est produite lors de la sauvegarde de la réservation."
            )
            return ConversationHandler.END

    @staticmethod
    def get_reservation_conversation_handler():
        """Retourne le gestionnaire de conversation pour les réservations"""
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📅 Faire une réservation$"),
                    ReservationHandler.start_reservation
                )
            ],
            states={
                ReservationHandler.CHOIX_CLIENT: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_client_choice,
                        pattern="^client_"
                    )
                ],
                ReservationHandler.CHOIX_TYPE: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_type_choice,
                        pattern="^type_"
                    )
                ],
                ReservationHandler.RESTAURANT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_restaurant_name
                    )
                ],
                ReservationHandler.RESTAURANT_PEOPLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_restaurant_people
                    )
                ],
                ReservationHandler.TRANSFER_DEPART: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_transfer_depart
                    )
                ],
                ReservationHandler.TRANSFER_ARRIVEE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_transfer_arrivee
                    )
                ],
                ReservationHandler.TRANSFER_PEOPLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_transfer_people
                    )
                ],
                ReservationHandler.MONITEUR_LANGUE: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_moniteur_langue,
                        pattern="^lang_"
                    )
                ],
                ReservationHandler.MONITEUR_TYPE: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_moniteur_type,
                        pattern="^sport_"
                    )
                ],
                ReservationHandler.MONITEUR_START: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_moniteur_start
                    )
                ],
                ReservationHandler.MONITEUR_END: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_moniteur_end
                    )
                ],
                ReservationHandler.MONITEUR_COUNT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_moniteur_count
                    )
                ],
                ReservationHandler.MONITEUR_PEOPLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_moniteur_people
                    )
                ],
                ReservationHandler.MASSAGE_TYPE: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_massage_type,
                        pattern="^massage_"
                    )
                ],
                ReservationHandler.MASSAGE_DUREE: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_massage_duree,
                        pattern="^duree_"
                    )
                ],
                ReservationHandler.SKISERVICE_DETAILS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_skiservice_details
                    )
                ],
                ReservationHandler.DATE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_date
                    )
                ],
                ReservationHandler.TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_time_and_confirm
                    )
                ]
            },
            fallbacks=[
                CommandHandler("cancel", lambda u, c: ConversationHandler.END)
            ],
            allow_reentry=True
        )