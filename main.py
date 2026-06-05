import sys

# IMPORT SICURI
try:
    import customtkinter as ctk
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    import psutil

except ImportError:
    print("❌ Librerie mancanti. Esegui: py -m pip install -r requirements.txt")
    sys.exit()

# IMPORTAZIONE DEL MODULO GRAFICO LOCALE
import interfaccia

# CONFIGURAZIONE INTERFACCIA
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("900x630")
app.title("Sistema Gestione Personale (SGP)")

# PASSAGGIO DEL RIFERIMENTO DELLA FINESTRA PRINCIPALE AL MODULO DI INTERFACCIA
interfaccia.app = app

# AVVIO APPLICAZIONE
interfaccia.login()
app.mainloop()