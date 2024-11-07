# main.py
from client_form import handle_client_info 
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler,
    CallbackQueryHandler, 
    MessageHandler, 
    ConversationHandler, 
    filters, 
    ContextTypes
)
from config import BOT_TOKEN
from database import add_client, get_all_clients, delete_client
from client_form import client_form_conversation  # Importation corrigée
from reservations import ReservationHandler
from preferences import set_preferences
from utils import send_client_data_by_email

# États pour les conversations
START_ROUTES = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fonction de démarrage - affiche le menu principal"""
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal avec toutes les options"""
    keyboard = [
        ["📝 Ajouter un client", "📋 Liste des clients"],
        ["🎛️ Définir les préférences", "📅 Faire une réservation"],
        ["📧 Envoyer les données par email", "🗑️ Supprimer un client"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Bienvenue sur le bot de conciergerie ! Utilisez le menu ci-dessous pour naviguer dans les options.",
        reply_markup=reply_markup
    )

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les choix du menu principal"""
    text = update.message.text

    if text == "📝 Ajouter un client":
        return await client_form_conversation.entry_points[0].callback(update, context)
    elif text == "📋 Liste des clients":
        await list_clients(update, context)
    elif text == "🗑️ Supprimer un client":
        await list_clients_for_deletion(update, context)
    elif text == "📅 Faire une réservation":
        await start_reservation_process(update, context)
    elif text == "🎛️ Définir les préférences":
        await set_preferences(update, context)
    elif text == "📧 Envoyer les données par email":
        await send_client_data_by_email(update, context)
    else:
        await show_main_menu(update, context)

async def list_clients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste de tous les clients"""
    clients = get_all_clients()
    if not clients:
        await update.message.reply_text("Aucun client n'est enregistré pour le moment.")
        await show_main_menu(update, context)
        return

    client_list = "Liste des clients enregistrés :\n\n"
    for client in clients:
        nom, prenom, telephone, email = client
        client_list += f"📌 {nom} {prenom}\n📞 {telephone}\n📧 {email}\n\n"
    
    await update.message.reply_text(client_list)
    await show_main_menu(update, context)

async def list_clients_for_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la liste des clients avec des boutons pour la suppression"""
    clients = get_all_clients()
    if not clients:
        await update.message.reply_text("Aucun client n'est enregistré pour le moment.")
        await show_main_menu(update, context)
        return

    keyboard = []
    for i, client in enumerate(clients):
        nom, prenom, _, _ = client
        keyboard.append([InlineKeyboardButton(
            f"{nom} {prenom}",
            callback_data=f"delete_{i}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Sélectionnez un client à supprimer :",
        reply_markup=reply_markup
    )

async def handle_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère la suppression d'un client"""
    query = update.callback_query
    await query.answer()
    
    client_index = int(query.data.split('_')[1])
    clients = get_all_clients()
    client = clients[client_index]
    
    delete_client(client_index + 1)  # +1 car les IDs commencent à 1 dans la BD
    
    await query.edit_message_text(
        f"Le client {client[0]} {client[1]} a été supprimé avec succès."
    )
    
async def start_reservation_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Démarre le processus de réservation"""
    clients = get_all_clients()
    if not clients:
        await update.message.reply_text(
            "Aucun client n'est enregistré. Veuillez d'abord ajouter un client."
        )
        await show_main_menu(update, context)
        return

    keyboard = []
    for i, client in enumerate(clients):
        # On sait que client contient [nom, prenom, telephone, email]
        nom, prenom, _, _ = client  # Correction ici
        keyboard.append([InlineKeyboardButton(
            f"{nom} {prenom}",
            callback_data=f"reserve_{i}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Sélectionnez un client pour la réservation :",
        reply_markup=reply_markup
    )

async def handle_reservation_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère la sélection du client pour la réservation"""
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
        f"Client sélectionné: {selected_client[0]} {selected_client[1]}\n"
        "Choisissez le type de réservation:",
        reply_markup=reply_markup
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annule et termine la conversation."""
    await update.message.reply_text(
        "Opération annulée. Retour au menu principal."
    )
    await show_main_menu(update, context)
    return ConversationHandler.END

def main() -> None:
    """Fonction principale pour démarrer le bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(handle_client_info) 
    # Handler pour le menu principal et les commandes de base
    application.add_handler(CommandHandler("start", start))
    application.add_handler(client_form_conversation)
    application.add_handler(CommandHandler("cancel", cancel))

    # Handler pour les boutons de suppression
    application.add_handler(CallbackQueryHandler(
        handle_deletion,
        pattern="^delete_"
    ))

    # Handler pour les boutons de réservation
    application.add_handler(CallbackQueryHandler(
        handle_reservation_choice,
        pattern="^reserve_"
    ))

    # Handler pour le processus de réservation
    reservation_handler = ReservationHandler.get_reservation_conversation_handler()
    application.add_handler(reservation_handler)

    # Handler pour le menu principal
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_menu_choice
    ))

    print("Bot démarré...")
    application.run_polling()

if __name__ == "__main__":
    main()