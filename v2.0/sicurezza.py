import os
from datetime import datetime
import hashlib
import base64
import psycopg2  # LIBRERIA RELAZIONALE PER CONNETTERSI A PostgreSQL
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

FILE_LOG = "log.txt"

load_dotenv()

# VARIABILI GLOBALI PER GESTIRE LA SESSIONE DELL'UTENTE ATTIVO
id_utente_attivo = None
username_attivo = None
cipher = None

# CONFIGURAZIONE PARAMETRI DEL DATABASE
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432"),
    "connect_timeout": 3
}

def ottieni_connessione():
    # CONNESSIONE CON IL DB REMOTO ATTRAVERSO IL TUNNEL VPN
    return psycopg2.connect(**DB_CONFIG)

def scrivi_log(messaggio):
    with open(FILE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {messaggio}\n")

def genera_hash(password, salt):
    stringa_da_hashare = password + salt
    return hashlib.sha256(stringa_da_hashare.encode()).hexdigest()

def deriva_chiave(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )

    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def registra_nuovo_utente(username, password):
    # CREAZIONE NUOVO UTENTE CON CONTROLLO DUPLICATI
    username = username.strip()
    password = password.strip()
    
    salt = os.urandom(16).hex()
    p_hash = genera_hash(password, salt)
    
    conn = None
    try:
        conn = ottieni_connessione()
        cursor = conn.cursor()
        
        # VERIFICA SE L'USERNAME NON È OCCUPATO
        cursor.execute("SELECT id_utente FROM utenti WHERE username = %s;", (username,))
        if cursor.fetchone():
            return False  # UTENTE GIÀ ESISTENTE
            
        # INSERIMENTO NUOVO UTENTE
        cursor.execute(
            "INSERT INTO utenti (username, password_hash, salt) VALUES (%s, %s, %s);",
            (username, p_hash, salt)
        )

        conn.commit()
        scrivi_log(f"Nuovo utente registrato con successo: {username}")
        return True
    except Exception as e:
        scrivi_log(f"Errore durante la registrazione dell'utente: {str(e)}")
        raise e
    finally:
        if conn: conn.close()

def autentica_utente(username, password):
    # VERIFICA LE CREDENZIALI NEL DB
    global cipher, id_utente_attivo, username_attivo
    username = username.strip()
    password = password.strip()
    conn = None

    try:
        conn = ottieni_connessione()
    except Exception as e:
        # ERRORE DI CONNESSIONE (SERVER/VPN NON RAGGIUNGIBILE)
        scrivi_log(f"Errore di connessione durante la fase di login: {str(e)}")
        raise e

    try:
        conn = ottieni_connessione()
        cursor = conn.cursor()
        cursor.execute("SELECT id_utente, password_hash, salt FROM utenti WHERE username = %s;", (username,))
        record = cursor.fetchone()
        
        if not record:
            return False # UTENTE NON TROVATO
            
        id_utente, p_hash, salt = record
        if genera_hash(password, salt) == p_hash:
            # SALVATAGGIO STATO SESSIONE
            id_utente_attivo = id_utente
            username_attivo = username
            
            # GENERAZIONE DELLA CHIAVE SIMMETRICA TEMPORANEA LOCALE
            chiave = deriva_chiave(password, salt)
            cipher = Fernet(chiave)
            
            return True
        return False  # PASSWORD ERRATA
    except Exception as e:
        scrivi_log(f"Errore durante la fase di login: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def resetta_master_password(username, nuova_password):
    # REIMPOSTAZIONE MASTER PASSWORD E RICALCOLO SALT E HASH
    username = username.strip()
    nuova_password = nuova_password.strip()
    
    nuovo_salt = os.urandom(16).hex()
    nuovo_hash = genera_hash(nuova_password, nuovo_salt)
    
    conn = None
    try:
        conn = ottieni_connessione()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_utente FROM utenti WHERE username = %s;", (username,))
        if not cursor.fetchone():
            return False
            
        # AGGIORNAMENTO CREDENZIALI DI SICUREZZA
        cursor.execute(
            "UPDATE utenti SET password_hash = %s, salt = %s WHERE username = %s;",
            (nuovo_hash, nuovo_salt, username)
        )

        conn.commit()
        scrivi_log(f"Master password modificata per l'utente: {username}")
        return True
    except Exception as e:
        scrivi_log(f"Errore durante il reset password: {str(e)}")
        raise e
    finally:
        if conn: conn.close()

def salva_password(app_nome, username_servizio, password_servizio):
    criptato = cipher.encrypt(password_servizio.encode()).decode()
    
    conn = ottieni_connessione()
    try:
        cursor = conn.cursor()
        # INSERISCE O AGGIORNA SE LA COPPIA (id_utente, app_nome) ESISTE GIÀ
        query = """
            INSERT INTO password_manager (id_utente, app_nome, username, password_criptata)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_utente, app_nome) 
            DO UPDATE SET username = EXCLUDED.username, password_criptata = EXCLUDED.password_criptata;
        """
        cursor.execute(query, (id_utente_attivo, app_nome, username_servizio, criptato))
        conn.commit()
        scrivi_log(f"Record salvato nel DB remoto per l'applicazione: {app_nome} (Utente: {username_attivo})")
    finally:
        conn.close()

def recupera_password(app_nome):
    conn = ottieni_connessione()
    try:
        cursor = conn.cursor()
        query = "SELECT username, password_criptata FROM password_manager WHERE id_utente = %s AND app_nome = %s;"
        cursor.execute(query, (id_utente_attivo, app_nome))
        record = cursor.fetchone()
        
        if record:
            user_serv, pass_criptata = record
            # DECIFRATURA SIMMETRICA
            decriptato = cipher.decrypt(pass_criptata.encode()).decode()
            return user_serv, decriptato
        return None
    finally:
        conn.close()

def ottieni_lista_applicazioni():
    conn = ottieni_connessione()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT app_nome FROM password_manager WHERE id_utente = %s ORDER BY app_nome;", (id_utente_attivo,))
        return [r[0] for r in cursor.fetchall()]
    finally:
        conn.close()