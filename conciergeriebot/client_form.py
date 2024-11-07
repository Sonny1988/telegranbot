# client_form.py

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from database import add_client

# États de la conversation
NOM, PRENOM, TELEPHONE, EMAIL = range(4)

async def start_add_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Commence le processus d'ajout d'un client"""
    await update.message.reply_text("Entrez le nom du client :")
    return NOM

async def ask_prenom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Demande le prénom après avoir reçu le nom"""
    context.user_data['nom'] = update.message.text
    await update.message.reply_text("Entrez le prénom du client :")
    return PRENOM

async def ask_telephone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Demande le téléphone après avoir reçu le prénom"""
    context.user_data['prenom'] = update.message.text
    await update.message.reply_text("Entrez le numéro de téléphone du client :")
    return TELEPHONE

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Demande l'email après avoir reçu le téléphone"""
    context.user_data['telephone'] = update.message.text
    await update.message.reply_text("Entrez l'email du client :")
    return EMAIL

async def save_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sauvegarde les informations du client"""
    email = update.message.text
    context.user_data['email'] = email
    
    try:
        add_client(
            context.user_data['nom'],
            context.user_data['prenom'],
            context.user_data['telephone'],
            email
        )
        await update.message.reply_text("✅ Client ajouté avec succès !")
    except Exception as e:
        await update.message.reply_text("❌ Erreur lors de l'ajout du client. Veuillez réessayer.")
        print(f"Erreur: {e}")
    
    return ConversationHandler.END

# Créer le gestionnaire de conversation pour l'ajout de client
client_form_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("add_client", start_add_client),
        MessageHandler(filters.Regex("^📝 Ajouter un client$"), start_add_client)
    ],
    states={
        NOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_prenom)],
        PRENOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_telephone)],
        TELEPHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_client)],
    },
    fallbacks=[
        CommandHandler("cancel", lambda u, c: ConversationHandler.END)
    ]
)

# Nous gardons les deux noms pour la compatibilité
handle_client_info = client_form_conversation