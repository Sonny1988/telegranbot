# handlers/reservation_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import get_all_clients, get_client_by_id, add_reservation
import logging

logger = logging.getLogger(__name__)

class ReservationHandler:
    # États pour tous les types de réservation
    (CHOIX_CLIENT, CHOIX_TYPE, 
     # Restaurant
     RESTAURANT_NAME, RESTAURANT_PEOPLE,
     # Transfert
     TRANSFER_DEPART, TRANSFER_ARRIVEE, TRANSFER_PEOPLE,
     # Moniteur
     MONITEUR_LANGUE, MONITEUR_TYPE, MONITEUR_START, MONITEUR_END, 
     MONITEUR_COUNT, MONITEUR_PEOPLE,
     # Massage
     MASSAGE_TYPE, MASSAGE_DUREE,
     # Ski Service
     SKISERVICE_DETAILS,
     # Commun
     DATE, TIME) = range(18)

    # Pour gérer les retours
    previous_states = {
        CHOIX_TYPE: CHOIX_CLIENT,
        RESTAURANT_NAME: CHOIX_TYPE,
        RESTAURANT_PEOPLE: RESTAURANT_NAME,
        TRANSFER_DEPART: CHOIX_TYPE,
        TRANSFER_ARRIVEE: TRANSFER_DEPART,
        TRANSFER_PEOPLE: TRANSFER_ARRIVEE,
        MONITEUR_LANGUE: CHOIX_TYPE,
        MONITEUR_TYPE: MONITEUR_LANGUE,
        MONITEUR_START: MONITEUR_TYPE,
        MONITEUR_END: MONITEUR_START,
        MONITEUR_COUNT: MONITEUR_END,
        MONITEUR_PEOPLE: MONITEUR_COUNT,
        MASSAGE_TYPE: CHOIX_TYPE,
        MASSAGE_DUREE: MASSAGE_TYPE,
        SKISERVICE_DETAILS: CHOIX_TYPE,
        DATE: None,  # Sera géré dynamiquement
        TIME: DATE
    }

    @staticmethod
    def add_back_button(keyboard=None):
        """Ajoute un bouton retour au clavier."""
        if keyboard is None:
            keyboard = []
        keyboard.append([InlineKeyboardButton("⬅️ Retour", callback_data="back")])
        return keyboard

    @staticmethod
    async def start_reservation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Démarre le processus de réservation."""
        context.user_data.clear()  # Réinitialise les données
        context.user_data['current_state'] = ReservationHandler.CHOIX_CLIENT
        
        clients = get_all_clients()
        if not clients:
            await update.message.reply_text("❌ Aucun client n'est enregistré.")
            return ConversationHandler.END

        keyboard = []
        for client in clients:
            button = InlineKeyboardButton(
                f"{client[1]} {client[2]}", 
                callback_data=f"client_{client[0]}"
            )
            keyboard.append([button])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👤 Sélectionnez le client pour la réservation:",
            reply_markup=reply_markup
        )
        context.user_data['clients'] = {str(client[0]): client for client in clients}
        return ReservationHandler.CHOIX_CLIENT

    @staticmethod
    async def handle_client_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Gère le choix du client."""
        query = update.callback_query
        await query.answer()
        
        client_id = int(query.data.split('_')[1])
        selected_client = context.user_data['clients'][str(client_id)]
        context.user_data['client'] = {
            'id': selected_client[0],
            'nom': selected_client[1],
            'prenom': selected_client[2],
            'telephone': selected_client[3],
            'email': selected_client[4]
        }
        context.user_data['current_state'] = ReservationHandler.CHOIX_TYPE

        keyboard = [
            [InlineKeyboardButton("🍽️ Restaurant", callback_data="type_restaurant")],
            [InlineKeyboardButton("🚗 Transfert", callback_data="type_transfer")],
            [InlineKeyboardButton("⛷️ Moniteur", callback_data="type_moniteur")],
            [InlineKeyboardButton("💆 Massage", callback_data="type_massage")],
            [InlineKeyboardButton("🎿 Ski Service", callback_data="type_skiservice")]
        ]
        keyboard = ReservationHandler.add_back_button(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Client sélectionné: {selected_client[1]} {selected_client[2]}\n\n"
            "🎯 Choisissez le type de réservation:",
            reply_markup=reply_markup
        )
        return ReservationHandler.CHOIX_TYPE

    @staticmethod
    async def handle_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Gère le choix du type de réservation."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await ReservationHandler.handle_back(update, context)
        
        res_type = query.data.split('_')[1]
        context.user_data['type_reservation'] = res_type

        client_info = (
            f"Last name: {context.user_data['client']['nom']}\n"
            f"First name: {context.user_data['client']['prenom']}\n"
            f"Email: {context.user_data['client']['email']}\n"
            f"Phone: {context.user_data['client']['telephone']}\n\n"
        )

        if res_type == 'restaurant':
            context.user_data['current_state'] = ReservationHandler.RESTAURANT_NAME
            keyboard = ReservationHandler.add_back_button()
            reply_markup = InlineKeyboardMarkup(keyboard)
            form_text = (
                "📝 Formulaire de réservation Restaurant\n\n"
                f"{client_info}"
                "Veuillez entrer le nom du restaurant:"
            )
            await query.edit_message_text(form_text, reply_markup=reply_markup)
            return ReservationHandler.RESTAURANT_NAME

        elif res_type == 'transfer':
            context.user_data['current_state'] = ReservationHandler.TRANSFER_DEPART
            keyboard = ReservationHandler.add_back_button()
            reply_markup = InlineKeyboardMarkup(keyboard)
            form_text = (
                "📝 Formulaire de réservation Transfert\n\n"
                f"{client_info}"
                "Veuillez entrer le point de départ:"
            )
            await query.edit_message_text(form_text, reply_markup=reply_markup)
            return ReservationHandler.TRANSFER_DEPART

        elif res_type == 'moniteur':
            context.user_data['current_state'] = ReservationHandler.MONITEUR_LANGUE
            keyboard = [
                [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")],
                [InlineKeyboardButton("🇬🇧 Anglais", callback_data="lang_en")],
                [InlineKeyboardButton("🇩🇪 Allemand", callback_data="lang_de")],
                [InlineKeyboardButton("🇮🇹 Italien", callback_data="lang_it")]
            ]
            keyboard = ReservationHandler.add_back_button(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard)
            form_text = (
                "📝 Formulaire de réservation Moniteur\n\n"
                f"{client_info}"
                "Choisissez la langue du moniteur:"
            )
            await query.edit_message_text(form_text, reply_markup=reply_markup)
            return ReservationHandler.MONITEUR_LANGUE

        elif res_type == 'massage':
            context.user_data['current_state'] = ReservationHandler.MASSAGE_TYPE
            keyboard = [
                [InlineKeyboardButton("Relaxant", callback_data="massage_relaxant")],
                [InlineKeyboardButton("Sportif", callback_data="massage_sportif")],
                [InlineKeyboardButton("Deep Tissue", callback_data="massage_deep")]
            ]
            keyboard = ReservationHandler.add_back_button(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard)
            form_text = (
                "📝 Formulaire de réservation Massage\n\n"
                f"{client_info}"
                "Choisissez le type de massage:"
            )
            await query.edit_message_text(form_text, reply_markup=reply_markup)
            return ReservationHandler.MASSAGE_TYPE

        else:  # ski service
            context.user_data['current_state'] = ReservationHandler.SKISERVICE_DETAILS
            keyboard = ReservationHandler.add_back_button()
            reply_markup = InlineKeyboardMarkup(keyboard)
            form_text = (
                "📝 Formulaire de réservation Ski Service\n\n"
                f"{client_info}"
                "Décrivez votre demande en détail\n"
                "(type de service, nombre de skis/snowboards, etc.):"
            )
            await query.edit_message_text(form_text, reply_markup=reply_markup)
            return ReservationHandler.SKISERVICE_DETAILS

    @staticmethod
    async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Gère le retour en arrière."""
        query = update.callback_query
        if query:
            await query.answer()

        current_state = context.user_data.get('current_state')
        if current_state is None:
            return ReservationHandler.CHOIX_CLIENT

        # Gestion spéciale pour DATE qui dépend du type de réservation
        if current_state == ReservationHandler.DATE:
            res_type = context.user_data.get('type_reservation')
            if res_type == 'restaurant':
                return ReservationHandler.RESTAURANT_PEOPLE
            elif res_type == 'transfer':
                return ReservationHandler.TRANSFER_PEOPLE
            elif res_type == 'moniteur':
                return ReservationHandler.MONITEUR_PEOPLE
            elif res_type == 'massage':
                return ReservationHandler.MASSAGE_DUREE
            else:  # ski service
                return ReservationHandler.SKISERVICE_DETAILS

        previous_state = ReservationHandler.previous_states.get(current_state)
        if previous_state == ReservationHandler.CHOIX_CLIENT:
            return await ReservationHandler.start_reservation(update, context)

        # Mettre à jour l'état actuel
        context.user_data['current_state'] = previous_state
        return previous_state
# Handlers pour Restaurant
    @staticmethod
    async def handle_restaurant_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.callback_query and update.callback_query.data == "back":
            return await ReservationHandler.handle_back(update, context)
            
        context.user_data['restaurant_name'] = update.message.text
        context.user_data['current_state'] = ReservationHandler.RESTAURANT_PEOPLE

        keyboard = ReservationHandler.add_back_button()
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        form_text = (
            "📝 Formulaire de réservation Restaurant\n\n"
            f"Restaurant: {update.message.text}\n\n"
            "Veuillez entrer le nombre de personnes:"
        )
        await update.message.reply_text(form_text, reply_markup=reply_markup)
        return ReservationHandler.RESTAURANT_PEOPLE

    @staticmethod
    async def handle_restaurant_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.callback_query and update.callback_query.data == "back":
            return await ReservationHandler.handle_back(update, context)

        try:
            num_people = int(update.message.text)
            context.user_data['num_people'] = num_people
            context.user_data['current_state'] = ReservationHandler.DATE

            keyboard = ReservationHandler.add_back_button()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            form_text = (
                "📝 Formulaire de réservation Restaurant\n\n"
                f"Restaurant: {context.user_data['restaurant_name']}\n"
                f"Nombre de personnes: {num_people}\n\n"
                "Veuillez entrer la date:\n"
                "Format: DD.MM.YY (exemple: 12.12.24)"
            )
            await update.message.reply_text(form_text, reply_markup=reply_markup)
            return ReservationHandler.DATE
        except ValueError:
            await update.message.reply_text("⚠️ Veuillez entrer un nombre valide.")
            return ReservationHandler.RESTAURANT_PEOPLE

    # Handlers communs pour la date et l'heure
    @staticmethod
    async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.callback_query and update.callback_query.data == "back":
            return await ReservationHandler.handle_back(update, context)

        date_text = update.message.text
        
        if not len(date_text.split('.')) == 3:
            await update.message.reply_text(
                "⚠️ Format de date invalide.\n"
                "Veuillez utiliser le format: DD.MM.YY (exemple: 12.12.24)"
            )
            return ReservationHandler.DATE
            
        context.user_data['date'] = date_text
        context.user_data['current_state'] = ReservationHandler.TIME
        
        # Afficher le récapitulatif selon le type de réservation
        form_text = "📝 Formulaire de réservation"
        if context.user_data['type_reservation'] == 'restaurant':
            form_text += (
                f"\n\nRestaurant: {context.user_data['restaurant_name']}\n"
                f"Nombre de personnes: {context.user_data['num_people']}"
            )
        
        form_text += (
            f"\nDate: {date_text}\n\n"
            "Veuillez entrer l'heure:\n"
            "Format: HHhMM (exemple: 09h00)"
        )
        
        keyboard = ReservationHandler.add_back_button()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(form_text, reply_markup=reply_markup)
        return ReservationHandler.TIME

    @staticmethod
    async def handle_time_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.callback_query and update.callback_query.data == "back":
            return await ReservationHandler.handle_back(update, context)

        time_text = update.message.text
        
        if 'h' not in time_text:
            await update.message.reply_text(
                "⚠️ Format d'heure invalide.\n"
                "Veuillez utiliser le format: HHhMM (exemple: 09h00)"
            )
            return ReservationHandler.TIME
            
        context.user_data['time'] = time_text

        try:
            logger.info("Préparation de la sauvegarde de la réservation")
            logger.info(f"Type de réservation: {context.user_data['type_reservation']}")
            
            # Préparation des détails selon le type
            details = {
                'client_id': context.user_data['client']['id'],
                'type': context.user_data['type_reservation']
            }
            
            if context.user_data['type_reservation'] == 'restaurant':
                details.update({
                    'restaurant_name': context.user_data.get('restaurant_name'),
                    'num_people': context.user_data.get('num_people')
                })
            
            logger.info(f"Détails préparés: {details}")

            # Sauvegarde en base de données
            reservation_id = add_reservation(
                client_id=context.user_data['client']['id'],
                type_reservation=context.user_data['type_reservation'],
                date_reservation=context.user_data['date'],
                heure_reservation=time_text,
                details=details
            )
            
            logger.info(f"Réservation sauvegardée avec ID: {reservation_id}")

            # Création du résumé
            summary = "✅ Réservation confirmée !\n\n"
            if context.user_data['type_reservation'] == 'restaurant':
                summary += (
                    f"Restaurant: {context.user_data['restaurant_name']}\n"
                    f"Nombre de personnes: {context.user_data['num_people']}\n"
                )

            summary += (
                f"Date: {context.user_data['date']}\n"
                f"Heure: {time_text}\n"
                f"Client: {context.user_data['client']['nom']} {context.user_data['client']['prenom']}\n"
                f"Email: {context.user_data['client']['email']}\n"
                f"Téléphone: {context.user_data['client']['telephone']}"
            )

            await update.message.reply_text(summary)
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            await update.message.reply_text(
                "❌ Une erreur s'est produite lors de la sauvegarde de la réservation."
            )
            return ConversationHandler.END

    @staticmethod
    def get_reservation_conversation_handler():
        """Retourne le gestionnaire de conversation pour les réservations."""
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📅 Réservation - Faire une nouvelle réservation$"),
                    ReservationHandler.start_reservation
                )
            ],
            states={
                ReservationHandler.CHOIX_CLIENT: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_client_choice,
                        pattern="^client_"
                    ),
                    CallbackQueryHandler(
                        ReservationHandler.handle_back,
                        pattern="^back$"
                    )
                ],
                ReservationHandler.CHOIX_TYPE: [
                    CallbackQueryHandler(
                        ReservationHandler.handle_type_choice,
                        pattern="^type_"
                    ),
                    CallbackQueryHandler(
                        ReservationHandler.handle_back,
                        pattern="^back$"
                    )
                ],
                ReservationHandler.RESTAURANT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_restaurant_name
                    ),
                    CallbackQueryHandler(
                        ReservationHandler.handle_back,
                        pattern="^back$"
                    )
                ],
                ReservationHandler.RESTAURANT_PEOPLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_restaurant_people
                    ),
                    CallbackQueryHandler(
                        ReservationHandler.handle_back,
                        pattern="^back$"
                    )
                ],
                ReservationHandler.DATE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_date
                    ),
                    CallbackQueryHandler(
                        ReservationHandler.handle_back,
                        pattern="^back$"
                    )
                ],
                ReservationHandler.TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ReservationHandler.handle_time_and_confirm
                    ),
                    CallbackQueryHandler(
                        ReservationHandler.handle_back,
                        pattern="^back$"
                    )
                ]
            },
            fallbacks=[
                MessageHandler(
                    filters.COMMAND,
                    lambda u, c: ConversationHandler.END
                ),
                CallbackQueryHandler(
                    ReservationHandler.handle_back,
                    pattern="^back$"
                )
            ]
        )