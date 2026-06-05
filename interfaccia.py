import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
from cryptography.fernet import Fernet
import psutil

# IMPORTAZIONE DEI MODULI LOCALI
import sicurezza
import gestore_file

# COLLEGAMENTO DELLA FINESTRA PRINCIPALE (viene assegnata dal main)
app = None

# RESET INTERFACCIA
def pulisci_finestra():
    for componente in app.winfo_children():
        componente.destroy()

# SCHERMATA LOGIN
def login():
    pulisci_finestra()

    # RIQUADRO GRIGIO LOGIN
    frame = ctk.CTkFrame(app, width=350, height=250)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame, text="   Sistema Gestione Personale (SGP)   ", font=("Arial", 22, "bold")).pack(pady=(35, 15))

    # CAMPO PASSWORD
    campo_ingresso = ctk.CTkEntry(frame, placeholder_text="Master Password", show="*", width=180, height=35, justify="center")
    campo_ingresso.pack(pady=10)

    def esegui_accesso():
        password = campo_ingresso.get()
        if not password:
            messagebox.showwarning("Attenzione", "La password non può essere vuota.")
            return

        vault_archiviato = sicurezza.carica_vault()

        if vault_archiviato is None:
            salt = os.urandom(16).hex()
            sicurezza.vault = {
                "salt": salt,
                "password_hash": sicurezza.genera_hash(password),
                "data": {}
            }
            sicurezza.salva_vault(sicurezza.vault)

            chiave = sicurezza.deriva_chiave(password, salt)
            sicurezza.cipher = Fernet(chiave)
            menu_principale()
            return

        if sicurezza.genera_hash(password) != vault_archiviato["password_hash"]:
            messagebox.showerror("Errore", "Password principale errata")
            return

        salt = vault_archiviato["salt"]
        chiave = sicurezza.deriva_chiave(password, salt)
        sicurezza.cipher = Fernet(chiave)
        sicurezza.vault = vault_archiviato
        menu_principale()

    # PULSANTE STANDARD COORDINATO CON LA LARGHEZZA DEL CAMPO DI TESTO
    ctk.CTkButton(frame, text="Accedi", font=("Arial", 13, "bold"), width=180, height=35, command=esegui_accesso).pack(pady=20)

# MENU PRINCIPALE
def menu_principale():
    pulisci_finestra()

    ctk.CTkLabel(app, text="Sistema Gestione Personale (SGP)", font=("Arial", 30, "bold")).pack(pady=(60, 40))

    # Pulsanti d'azione grandi e strutturati
    ctk.CTkButton(app, text="📁  File Manager", font=("Arial", 16), width=320, height=45, command=gestione_file).pack(pady=12)
    ctk.CTkButton(app, text="🔐  Password Manager", font=("Arial", 16), width=320, height=45, command=menu_password).pack(pady=12)
    ctk.CTkButton(app, text="💻  Stato PC", font=("Arial", 16), width=320, height=45, command=stato_pc).pack(pady=12)

# INTERFACCIA FILE MANAGER
def gestione_file():
    pulisci_finestra()

    ctk.CTkLabel(app, text="FILE MANAGER", font=("Arial", 26, "bold")).pack(pady=20)

    cartella_selezionata = ctk.StringVar()
    
    anteprima_testo = ctk.CTkTextbox(app, width=700, height=280, font=("Courier New", 12))
    anteprima_testo.pack(pady=10)

    etichetta_stato = ctk.CTkLabel(app, text="Nessuna cartella selezionata", font=("Arial", 13, "italic"), text_color="gray")
    etichetta_stato.pack(pady=5)

    def seleziona():
        cartella = filedialog.askdirectory()
        
        nessuna_selezione = (not cartella)
        if nessuna_selezione:
            return
            
        cartella_selezionata.set(cartella)
        anteprima_testo.delete("0.0", "end")
        
        for file in gestore_file.anteprima_cartella(cartella):
            anteprima_testo.insert("end", file + "\n")

        if gestore_file.cartella_ordinata(cartella):
            etichetta_stato.configure(text="✨ Cartella già ordinata in modo corretto!", text_color="#2ecc71")
        else:
            etichetta_stato.configure(text="📂 Cartella non ordinata. Pronta per la riorganizzazione.", text_color="#e67e22")

    def esegui():
        percorso = cartella_selezionata.get()
        if not percorso:
            messagebox.showwarning("Attenzione", "Seleziona prima una cartella!")
            return

        if gestore_file.cartella_ordinata(percorso):
            messagebox.showinfo("Informazione", "I file in questa cartella sono già strutturati e ordinati.")
            return

        gestore_file.organizza_cartella(percorso)
        messagebox.showinfo("Successo", "Cartella organized con successo!")
        
        anteprima_testo.delete("0.0", "end")
        for file in gestore_file.anteprima_cartella(percorso):
            anteprima_testo.insert("end", file + "\n")
        etichetta_stato.configure(text="✨ Cartella già ordinata in modo corretto!", text_color="#2ecc71")

    frame_pulsanti = ctk.CTkFrame(app, fg_color="transparent")
    frame_pulsanti.pack(pady=15)

    ctk.CTkButton(frame_pulsanti, text="Sfoglia Cartella", font=("Arial", 13), width=160, height=35, command=seleziona).pack(side="left", padx=10)
    ctk.CTkButton(frame_pulsanti, text="Avvia Riordino", font=("Arial", 13, "bold"), fg_color="#2ecc71", hover_color="#27ae60", width=160, height=35, command=esegui).pack(side="left", padx=10)
    
    ctk.CTkButton(app, text="Torna al Menu", font=("Arial", 13), width=180, height=35, fg_color="transparent", border_width=1, command=menu_principale).pack(pady=(10, 0))

# INTERFACCIA STATO PC
def stato_pc():
    pulisci_finestra()

    ctk.CTkLabel(app, text="MONITORAGGIO STATO PC", font=("Arial", 26, "bold")).pack(pady=20)

    contenitore_metriche = ctk.CTkFrame(app, width=550, height=350, fg_color="transparent")
    contenitore_metriche.pack(pady=10)

    # --- CPU ---
    Cpu_Label = ctk.CTkLabel(contenitore_metriche, text="Carico CPU: 0%", font=("Arial", 14, "bold"))
    Cpu_Label.pack(anchor="w", padx=40, pady=(10, 2))
    Cpu_Bar = ctk.CTkProgressBar(contenitore_metriche, width=470, height=12)
    Cpu_Bar.pack(padx=40, pady=(0, 15))

    # --- RAM ---
    Ram_Label = ctk.CTkLabel(contenitore_metriche, text="Utilizzo RAM: 0%", font=("Arial", 14, "bold"))
    Ram_Label.pack(anchor="w", padx=40, pady=(5, 2))
    Ram_Bar = ctk.CTkProgressBar(contenitore_metriche, width=470, height=12)
    Ram_Bar.pack(padx=40, pady=(0, 4))
    Ram_Dettaglio = ctk.CTkLabel(contenitore_metriche, text="Dati RAM: -- GB / -- GB", font=("Arial", 12), text_color="gray")
    Ram_Dettaglio.pack(anchor="w", padx=45, pady=(0, 15))

    # --- DISCO ---
    Disco_Label = ctk.CTkLabel(contenitore_metriche, text="Spazio Disco Usato: 0%", font=("Arial", 14, "bold"))
    Disco_Label.pack(anchor="w", padx=40, pady=(5, 2))
    Disco_Bar = ctk.CTkProgressBar(contenitore_metriche, width=470, height=12)
    Disco_Bar.pack(padx=40, pady=(0, 4))
    Disco_Dettaglio = ctk.CTkLabel(contenitore_metriche, text="Disco: -- GB Usati | -- GB Liberi", font=("Arial", 12), text_color="gray")
    Disco_Dettaglio.pack(anchor="w", padx=45, pady=(0, 10))

    def aggiorna_dati():
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disco = psutil.disk_usage("/")

        ram_totale_gb = round(ram.total / 1024**3, 2)
        ram_usata_gb = round((ram.total - ram.available) / 1024**3, 2)
        disco_usato_gb = round(disco.used / 1024**3, 2)
        disco_libero_gb = round(disco.free / 1024**3, 2)

        Cpu_Label.configure(text=f"Carico CPU: {cpu}%")
        Cpu_Bar.set(cpu / 100)

        Ram_Label.configure(text=f"Utilizzo RAM: {ram.percent}%")
        Ram_Bar.set(ram.percent / 100)
        Ram_Dettaglio.configure(text=f"Dettaglio: {ram_usata_gb} GB usati di {ram_totale_gb} GB totali")

        Disco_Label.configure(text=f"Spazio Disco Usato: {disco.percent}%")
        Disco_Bar.set(disco.percent / 100)
        Disco_Dettaglio.configure(text=f"Dettaglio: {disco_usato_gb} GB occupati | {disco_libero_gb} GB disponibili")

    aggiorna_dati()

    ctk.CTkButton(app, text="Aggiorna Dati", font=("Arial", 13), width=180, height=35, command=aggiorna_dati).pack(pady=10)
    ctk.CTkButton(app, text="Torna al Menu", font=("Arial", 13), width=180, height=35, fg_color="transparent", border_width=1, command=menu_principale).pack(pady=5)

# INTERFACCIA PASSWORD MANAGER
def menu_password():
    pulisci_finestra()

    ctk.CTkLabel(app, text="PASSWORD MANAGER", font=("Arial", 26, "bold")).pack(pady=25)

    ctk.CTkButton(app, text="➕ Registra Nuova Password", font=("Arial", 14), width=280, height=40, command=registra_password).pack(pady=8)
    ctk.CTkButton(app, text="🔎 Recupera Credenziali", font=("Arial", 14), width=280, height=40, command=recupera_password_ui).pack(pady=8)
    ctk.CTkButton(app, text="📋 Mostra Elenco Vault", font=("Arial", 14), width=280, height=40, command=vault_ui).pack(pady=8)
    
    ctk.CTkButton(app, text="Torna al Menu", font=("Arial", 13), width=180, height=35, fg_color="transparent", border_width=1, command=menu_principale).pack(pady=30)

def registra_password():
    pulisci_finestra()

    ctk.CTkLabel(app, text="REGISTRA PASSWORD", font=("Arial", 24, "bold")).pack(pady=20)

    campo_app = ctk.CTkEntry(app, placeholder_text="Nome App / Sito Web", width=300, height=35)
    campo_utente = ctk.CTkEntry(app, placeholder_text="Username / Email", width=300, height=35)
    campo_password = ctk.CTkEntry(app, placeholder_text="Password", show="*", width=300, height=35)

    campo_app.pack(pady=8)
    campo_utente.pack(pady=8)
    campo_password.pack(pady=8)

    def invia_dati():
        if not campo_app.get() or not campo_utente.get() or not campo_password.get():
            messagebox.showwarning("Errore", "Tutti i campi sono obbligatori!")
            return
        sicurezza.salva_password(campo_app.get(), campo_utente.get(), campo_password.get())
        messagebox.showinfo("Successo", "Credenziali salvate nel database cifrato.")
        menu_password()

    ctk.CTkButton(app, text="Salva nel Vault", font=("Arial", 13, "bold"), fg_color="#2ecc71", hover_color="#27ae60", width=180, height=35, command=invia_dati).pack(pady=20)
    ctk.CTkButton(app, text="Annulla", font=("Arial", 13), width=180, height=35, fg_color="transparent", border_width=1, command=menu_password).pack(pady=5)

def recupera_password_ui():
    pulisci_finestra()

    ctk.CTkLabel(app, text="RECUPERA PASSWORD", font=("Arial", 24, "bold")).pack(pady=20)

    campo_app = ctk.CTkEntry(app, placeholder_text="Inserisci il nome dell'App / Sito", width=300, height=35)
    campo_app.pack(pady=15)

    etichetta_risultato = ctk.CTkLabel(app, text="", font=("Arial", 14, "bold"))
    etichetta_risultato.pack(pady=15)

    def esegui_ricerca():
        risultato = sicurezza.recupera_password(campo_app.get())
        if risultato:
            etichetta_risultato.configure(text=f"👤 Username: {risultato[0]}\n🔑 Password: {risultato[1]}", text_color="#2ecc71")
        else:
            etichetta_risultato.configure(text="❌ Elemento non trovato nel database.", text_color="#e74c3c")

    ctk.CTkButton(app, text="Avvia Ricerca", font=("Arial", 13), width=180, height=35, command=esegui_ricerca).pack(pady=10)
    ctk.CTkButton(app, text="Indietro", font=("Arial", 13), width=180, height=35, fg_color="transparent", border_width=1, command=menu_password).pack(pady=5)

def vault_ui():
    pulisci_finestra()

    ctk.CTkLabel(app, text="ELENCO APPLICAZIONI SALVATE", font=("Arial", 24, "bold")).pack(pady=20)

    box_testo = ctk.CTkTextbox(app, width=450, height=280, font=("Courier New", 12))
    box_testo.pack(pady=10)

    def visualizza_lista():
        box_testo.delete("0.0", "end")
        if not sicurezza.vault.get("data"):
            box_testo.insert("end", "Il database è vuoto.")
            return
        for chiave in sicurezza.vault["data"].keys():
            box_testo.insert("end", f"🔐 {chiave}\n")

    visualizza_lista()

    ctk.CTkButton(app, text="Aggiorna Lista", font=("Arial", 13), width=180, height=35, command=visualizza_lista).pack(pady=10)
    ctk.CTkButton(app, text="Indietro", font=("Arial", 13), width=180, height=35, fg_color="transparent", border_width=1, command=menu_password).pack(pady=5)