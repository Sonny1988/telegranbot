# utils.py

import smtplib
from email.message import EmailMessage

def send_client_data_by_email(update, context) -> None:
    update.message.reply_text("Fonction d'envoi par email en cours de développement...")
    # Ajoutez ici le code pour envoyer les données par email
