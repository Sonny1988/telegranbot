# database.py
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def connect_db():
    """Établit la connexion avec la base de données."""
    try:
        conn = sqlite3.connect("concierge.db")
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        raise

def init_database():
    """Initialise toutes les tables nécessaires."""
    create_clients_table()
    create_reservations_table()
    logger.info("Base de données initialisée avec succès")

def create_clients_table():
    """Crée la table des clients."""
    conn, cursor = connect_db()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                telephone TEXT NOT NULL,
                email TEXT NOT NULL,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logger.info("Table clients créée ou vérifiée")
    finally:
        conn.close()

def create_reservations_table():
    """Crée la table des réservations."""
    conn, cursor = connect_db()
    try:
        # Supprime la table si elle existe
        cursor.execute("DROP TABLE IF EXISTS reservations")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                type_reservation TEXT NOT NULL,
                restaurant_name TEXT,
                num_people INTEGER,
                date_reservation TEXT NOT NULL,
                heure_reservation TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        conn.commit()
        logger.info("Table reservations créée ou réinitialisée")
    finally:
        conn.close()

def add_client(nom, prenom, telephone, email):
    """Ajoute un nouveau client."""
    conn, cursor = connect_db()
    try:
        cursor.execute('''
            INSERT INTO clients (nom, prenom, telephone, email)
            VALUES (?, ?, ?, ?)
        ''', (nom, prenom, telephone, email))
        conn.commit()
        logger.info(f"Client ajouté: {nom} {prenom}")
        return cursor.lastrowid
    finally:
        conn.close()

def get_client_by_id(client_id):
    """Récupère un client par son ID."""
    conn, cursor = connect_db()
    try:
        cursor.execute('''
            SELECT id, nom, prenom, telephone, email
            FROM clients WHERE id = ?
        ''', (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_all_clients():
    """Récupère tous les clients."""
    conn, cursor = connect_db()
    try:
        cursor.execute("SELECT id, nom, prenom, telephone, email FROM clients")
        return cursor.fetchall()
    finally:
        conn.close()

def add_reservation(client_id, type_reservation, date_reservation, heure_reservation, details=None):
    """Ajoute une nouvelle réservation."""
    conn, cursor = connect_db()
    try:
        logger.info(f"Tentative de sauvegarde de réservation pour client_id={client_id}")
        logger.info(f"Détails de la réservation: {details}")
        
        cursor.execute('''
            INSERT INTO reservations (
                client_id,
                type_reservation,
                restaurant_name,
                num_people,
                date_reservation,
                heure_reservation,
                details
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            type_reservation,
            details.get('restaurant_name') if details else None,
            details.get('num_people') if details else None,
            date_reservation,
            heure_reservation,
            str(details) if details else None
        ))
        conn.commit()
        reservation_id = cursor.lastrowid
        logger.info(f"Réservation sauvegardée avec succès, ID={reservation_id}")
        return reservation_id
    except sqlite3.Error as e:
        logger.error(f"Erreur SQLite lors de la sauvegarde: {e}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la sauvegarde: {e}")
        raise
    finally:
        conn.close()

def get_reservations_by_client(client_id):
    """Récupère toutes les réservations d'un client."""
    conn, cursor = connect_db()
    try:
        cursor.execute('''
            SELECT r.*, c.nom, c.prenom
            FROM reservations r
            JOIN clients c ON r.client_id = c.id
            WHERE r.client_id = ?
            ORDER BY r.date_reservation, r.heure_reservation
        ''', (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def delete_reservation(reservation_id):
    """Supprime une réservation."""
    conn, cursor = connect_db()
    try:
        cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
        logger.info(f"Réservation {reservation_id} supprimée")
    finally:
        conn.close()

def delete_client(client_id):
    """Supprime un client et ses réservations."""
    conn, cursor = connect_db()
    try:
        cursor.execute("DELETE FROM reservations WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        logger.info(f"Client {client_id} et ses réservations supprimés")
    finally:
        conn.close()