import os
import json
from datetime import datetime
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# CONFIGURAZIONE VAULT e LOG (cronologia)
FILE_VAULT = "vault.json"
FILE_LOG = "log.txt"

cipher = None
vault = {}

# FUNZIONI CRITTOGRAFICHE
def genera_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def deriva_chiave(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# GESTIONE FILE VAULT
def carica_vault():
    if os.path.exists(FILE_VAULT):
        with open(FILE_VAULT, "r") as f:
            return json.load(f)
    return None

def salva_vault(dati):
    with open(FILE_VAULT, "w") as f:
        json.dump(dati, f, indent=4)

def scrivi_log(messaggio):
    with open(FILE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {messaggio}\n")

# LOGICA PASSWORD MANAGER
def salva_password(app_name, username, password):
    criptato = cipher.encrypt(password.encode()).decode()
    vault["data"][app_name] = {
        "username": username,
        "password": criptato
    }
    salva_vault(vault)
    scrivi_log(f"Password salvata per l'applicazione: {app_name}")

def recupera_password(app_name):
    if app_name in vault["data"]:
        decriptato = cipher.decrypt(vault["data"][app_name]["password"].encode()).decode()
        return vault["data"][app_name]["username"], decriptato
    return None