import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet
import psutil

try:
    import pynvml
    pynvml.nvmlInit()
    GPU_DISPONIBILE = True
except Exception:
    GPU_DISPONIBILE = False

# IMPORTAZIONE DEI MODULI LOCALI
import sicurezza
import gestore_file

# COLLEGAMENTO DELLA FINESTRA PRINCIPALE (viene assegnata dal main)
app = None

VERDE         = "#2ecc71"
VERDE_HOVER   = "#27ae60"
ARANCIO       = "#e67e22"
ARANCIO_HOVER = "#d35400"
GRIGIO_BTN    = "#34495e"
GRIGIO_HOVER  = "#2c3e50"
ROSSO         = "#e74c3c"

# RESET INTERFACCIA
def pulisci_finestra():
    for componente in app.winfo_children():
        componente.destroy()

# SCHERMATA LOGIN GENERALE (MULTI-UTENTE)
def login():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    frame_card = ctk.CTkFrame(frame_pagina, width=500, corner_radius=16)
    frame_card.pack()

    frame_interno = ctk.CTkFrame(frame_card, fg_color="transparent")
    frame_interno.pack(padx=50, pady=40)

    ctk.CTkLabel(frame_interno, text="SGP", font=("Arial", 38, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_interno, text="Sistema Gestione Personale", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

    # SEPARATORE
    ctk.CTkFrame(frame_interno, height=1, fg_color="#3a3a3a", width=340).pack(pady=(0, 20))

    campo_user = ctk.CTkEntry(frame_interno, placeholder_text="Username", width=340, height=40, corner_radius=8, justify="center")
    campo_user.pack(pady=6)

    campo_pass = ctk.CTkEntry(frame_interno, placeholder_text="Master Password", show="*", width=340, height=40, corner_radius=8, justify="center")
    campo_pass.pack(pady=6)

    def esegui_accesso():
        username = campo_user.get()
        password = campo_pass.get()

        if not username or not password:
            messagebox.showwarning("Attenzione", "Tutti i campi sono obbligatori per l'accesso.")
            return
        try:
            successo = sicurezza.autentica_utente(username, password)
            if successo:
                menu_principale()
            else:
                messagebox.showerror("Errore", "Username o Master Password errati.")
        except Exception:
            messagebox.showerror("Errore di Rete", "Impossibile raggiungere il database remoto.\nVerifica la connessione VPN.")

    ctk.CTkButton(frame_interno, text="Accedi", font=("Arial", 13, "bold"), width=340, height=42, corner_radius=8, command=esegui_accesso).pack(pady=(18, 12))

    ctk.CTkFrame(frame_interno, height=1, fg_color="#3a3a3a", width=340).pack(pady=(0, 14))

    frame_opzioni = ctk.CTkFrame(frame_interno, fg_color="transparent")
    frame_opzioni.pack()

    ctk.CTkButton(frame_opzioni, text="Registrati", font=("Arial", 12, "bold"), width=158, height=34, corner_radius=8, fg_color=GRIGIO_BTN, hover_color=GRIGIO_HOVER, command=schermata_registrazione).pack(side="left", padx=6)
    ctk.CTkButton(frame_opzioni, text="Reset Password", font=("Arial", 12, "bold"), width=158, height=34, corner_radius=8, fg_color=GRIGIO_BTN, hover_color=GRIGIO_HOVER, command=schermata_reset_password).pack(side="left", padx=6)


# SCHERMATA DI REGISTRAZIONE NUOVO ACCOUNT
def schermata_registrazione():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    frame_card = ctk.CTkFrame(frame_pagina, width=500, corner_radius=16)
    frame_card.pack()

    frame_interno = ctk.CTkFrame(frame_card, fg_color="transparent")
    frame_interno.pack(padx=50, pady=40)

    ctk.CTkLabel(frame_interno, text="Registra Profilo", font=("Arial", 26, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_interno, text="Crea un nuovo account SGP", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

    ctk.CTkFrame(frame_interno, height=1, fg_color="#3a3a3a", width=340).pack(pady=(0, 20))

    campo_nuovo_user = ctk.CTkEntry(frame_interno, placeholder_text="Scegli Username", width=340, height=40, corner_radius=8, justify="center")
    campo_nuovo_user.pack(pady=7)

    campo_nuova_pass = ctk.CTkEntry(frame_interno, placeholder_text="Imposta Master Password", show="*", width=340, height=40, corner_radius=8, justify="center")
    campo_nuova_pass.pack(pady=7)

    def invia_registrazione():
        username = campo_nuovo_user.get()
        password = campo_nuova_pass.get()

        if not username or not password:
            messagebox.showwarning("Errore", "Compila tutti i campi richiesti.")
            return
        try:
            creato = sicurezza.registra_nuovo_utente(username, password)
            if creato:
                messagebox.showinfo("Successo", "Account creato! Ora puoi effettuare il login.")
                login()
            else:
                messagebox.showwarning("Errore", "Questo username è già registrato nel sistema.")
        except Exception:
            messagebox.showerror("Errore", "Impossibile completare la registrazione sul server remoto.")

    ctk.CTkButton(frame_interno, text="Crea Account", font=("Arial", 13, "bold"), fg_color=VERDE, hover_color=VERDE_HOVER, width=340, height=42, corner_radius=8, command=invia_registrazione).pack(pady=(16, 8))
    ctk.CTkButton(frame_interno, text="← Torna al Login", font=("Arial", 12), fg_color="transparent", border_width=1, width=340, height=38, corner_radius=8, command=login).pack()


# SCHERMATA RESET PASSWORD
def schermata_reset_password():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    frame_card = ctk.CTkFrame(frame_pagina, width=500, corner_radius=16)
    frame_card.pack()

    frame_interno = ctk.CTkFrame(frame_card, fg_color="transparent")
    frame_interno.pack(padx=50, pady=40)

    ctk.CTkLabel(frame_interno, text="Reset Password", font=("Arial", 26, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_interno, text="Aggiorna la tua Master Password", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

    ctk.CTkFrame(frame_interno, height=1, fg_color="#3a3a3a", width=340).pack(pady=(0, 20))

    campo_user_reset = ctk.CTkEntry(frame_interno, placeholder_text="Il tuo Username", width=340, height=40, corner_radius=8, justify="center")
    campo_user_reset.pack(pady=7)

    campo_pass_reset = ctk.CTkEntry(frame_interno, placeholder_text="Nuova Master Password", show="*", width=340, height=40, corner_radius=8, justify="center")
    campo_pass_reset.pack(pady=7)

    def esegui_reset():
        username = campo_user_reset.get()
        nuova_pass = campo_pass_reset.get()

        if not username or not nuova_pass:
            messagebox.showwarning("Errore", "Compila tutti i campi richiesti.")
            return
        try:
            aggiornato = sicurezza.resetta_master_password(username, nuova_pass)
            if aggiornato:
                messagebox.showinfo("Successo", "Password aggiornata correttamente sul database remoto!")
                login()
            else:
                messagebox.showerror("Errore", "Username non trovato nel database.")
        except Exception:
            messagebox.showerror("Errore", "Impossibile comunicare con il server per il cambio password.")

    ctk.CTkButton(frame_interno, text="Aggiorna Password", font=("Arial", 13, "bold"), fg_color=ARANCIO, hover_color=ARANCIO_HOVER, width=340, height=42, corner_radius=8, command=esegui_reset).pack(pady=(16, 8))
    ctk.CTkButton(frame_interno, text="← Torna al Login", font=("Arial", 12), fg_color="transparent", border_width=1, width=340, height=38, corner_radius=8, command=login).pack()


# MENU PRINCIPALE
def menu_principale():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="SGP", font=("Arial", 42, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_pagina, text="Sistema Gestione Personale", font=("Arial", 13), text_color="gray").pack(pady=(0, 36))

    ctk.CTkButton(frame_pagina, text="📁   File Manager", font=("Arial", 15), width=320, height=48, corner_radius=10, command=gestione_file).pack(pady=8)
    ctk.CTkButton(frame_pagina, text="🔐   Password Manager", font=("Arial", 15), width=320, height=48, corner_radius=10, command=menu_password).pack(pady=8)
    ctk.CTkButton(frame_pagina, text="💻   Stato PC", font=("Arial", 15), width=320, height=48, corner_radius=10, command=stato_pc).pack(pady=8)


# INTERFACCIA FILE MANAGER CON PAGINAZIONE GRAFICA FISSA
def gestione_file():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="File Manager", font=("Arial", 28, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_pagina, text="Esplora la cartella locale con navigazione a pagine fisse", font=("Arial", 12), text_color="gray").pack(pady=(0, 16))

    cartella_selezionata = ctk.StringVar()
    
    lista_file = []
    pagina_corrente = [0] 
    ELEMENTI_PER_PAGINA = 5

    frame_bacheca = ctk.CTkFrame(frame_pagina, width=460, height=180, fg_color="#2b2b2b", corner_radius=10)
    frame_bacheca.pack(pady=6)
    frame_bacheca.pack_propagate(False)

    etichetta_pagine = ctk.CTkLabel(frame_pagina, text="Pagina 0 di 0", font=("Arial", 11), text_color="gray")
    etichetta_pagine.pack()

    frame_navigazione = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_navigazione.pack(pady=4)

    btn_prev = ctk.CTkButton(frame_navigazione, text="◀ Anteriore", font=("Arial", 11), width=90, height=26, state="disabled")
    btn_prev.pack(side="left", padx=4)

    btn_next = ctk.CTkButton(frame_navigazione, text="Successivo ▶", font=("Arial", 11), width=90, height=26, state="disabled")
    btn_next.pack(side="left", padx=4)

    etichetta_stato = ctk.CTkLabel(frame_pagina, text="Nessuna cartella selezionata", font=("Arial", 12, "italic"), text_color="gray")
    etichetta_stato.pack(pady=6)

    frame_pulsanti = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_pulsanti.pack(pady=10)

    bottone_sfoglia  = ctk.CTkButton(frame_pulsanti, text="Sfoglia Cartella", font=("Arial", 13), width=170, height=38, corner_radius=8)
    bottone_sfoglia.pack(side="left", padx=8)

    bottone_riordino = ctk.CTkButton(frame_pulsanti, text="Avvia Riordino", font=("Arial", 13, "bold"), fg_color=VERDE, hover_color=VERDE_HOVER, width=170, height=38, corner_radius=8)
    bottone_riordino.pack(side="left", padx=8)

    ctk.CTkButton(frame_pagina, text="← Menu", font=("Arial", 12), width=160, height=34, corner_radius=8, fg_color="transparent", border_width=1, command=menu_principale).pack(pady=(10, 0))

    def renderizza_pagina():
        for widget in frame_bacheca.winfo_children():
            widget.destroy()
            
        if not lista_file:
            ctk.CTkLabel(frame_bacheca, text="Nessun file presente", font=("Arial", 13, "italic"), text_color="gray").place(relx=0.5, rely=0.5, anchor="center")
            etichetta_pagine.configure(text="Pagina 0 di 0")
            btn_prev.configure(state="disabled")
            btn_next.configure(state="disabled")
            return

        totale_pagine = (len(lista_file) - 1) // ELEMENTI_PER_PAGINA + 1
        etichetta_pagine.configure(text=f"Pagina {pagina_corrente[0] + 1} di {totale_pagine}")

        # CALCOLO INDICI DELLA PORZIONE DI LISTA CORRENTE
        inizio = pagina_corrente[0] * ELEMENTI_PER_PAGINA
        fine = inizio + ELEMENTI_PER_PAGINA
        porzione = lista_file[inizio:fine]

        for file in porzione:
            ctk.CTkLabel(frame_bacheca, text=f"📄  {file}", font=("Courier New", 12), anchor="w").pack(fill="x", padx=15, pady=4)

        btn_prev.configure(state="normal" if pagina_corrente[0] > 0 else "disabled")
        btn_next.configure(state="normal" if fine < len(lista_file) else "disabled")

    def cambia_pagina(direzione):
        pagina_corrente[0] += direzione
        renderizza_pagina()

    btn_prev.configure(command=lambda: cambia_pagina(-1))
    btn_next.configure(command=lambda: cambia_pagina(1))

    def collega_funzionalità():
        def seleziona():
            cartella = filedialog.askdirectory()
            if not cartella: return
            
            cartella_selezionata.set(cartella)
            
            nonlocal lista_file
            lista_file = gestore_file.anteprima_cartella(cartella)
            pagina_corrente[0] = 0
            renderizza_pagina()

            if gestore_file.cartella_ordinata(cartella):
                etichetta_stato.configure(text="✨  Cartella già ordinata in modo corretto!", text_color=VERDE)
            else:
                etichetta_stato.configure(text="📂  Cartella non ordinata — pronta per la riorganizzazione.", text_color=ARANCIO)

        def esegui():
            percorso = cartella_selezionata.get()
            if not percorso:
                messagebox.showwarning("Attenzione", "Seleziona prima una cartella!")
                return
            
            if gestore_file.cartella_ordinata(percorso):
                messagebox.showinfo("Informazione", "I file in questa cartella sono già strutturati e ordinati.")
                return
            
            gestore_file.organizza_cartella(percorso)
            messagebox.showinfo("Successo", "Cartella organizzata con successo!")
            
            nonlocal lista_file
            lista_file = gestore_file.anteprima_cartella(percorso)
            pagina_corrente[0] = 0
            renderizza_pagina()
            etichetta_stato.configure(text="✨  Cartella già ordinata in modo corretto!", text_color=VERDE)

        bottone_sfoglia.configure(command=seleziona)
        bottone_riordino.configure(command=esegui)

    renderizza_pagina()
    app.after(0, collega_funzionalità)


# INTERFACCIA STATO PC
def stato_pc():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="Stato PC", font=("Arial", 28, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_pagina, text="Monitoraggio risorse di sistema in tempo reale", font=("Arial", 12), text_color="gray").pack(pady=(0, 16))

    frame_metriche = ctk.CTkFrame(frame_pagina, width=520, corner_radius=14)
    frame_metriche.pack(pady=4)

    frame_metriche_interno = ctk.CTkFrame(frame_metriche, fg_color="transparent")
    frame_metriche_interno.pack(padx=28, pady=20)

    Cpu_Label = ctk.CTkLabel(frame_metriche_interno, text="Carico CPU", font=("Arial", 13, "bold"))
    Cpu_Label.pack(anchor="w", pady=(6, 3))
    Cpu_Bar = ctk.CTkProgressBar(frame_metriche_interno, width=440, height=10, progress_color="#3498db", corner_radius=5)
    Cpu_Bar.set(0)
    Cpu_Bar.pack(pady=(0, 4))

    Ram_Label = ctk.CTkLabel(frame_metriche_interno, text="Utilizzo RAM", font=("Arial", 13, "bold"))
    Ram_Label.pack(anchor="w", pady=(10, 3))
    Ram_Bar = ctk.CTkProgressBar(frame_metriche_interno, width=440, height=10, progress_color=VERDE, corner_radius=5)
    Ram_Bar.set(0)
    Ram_Bar.pack(pady=(0, 2))
    Ram_Dettaglio = ctk.CTkLabel(frame_metriche_interno, text="", font=("Arial", 11), text_color="gray")
    Ram_Dettaglio.pack(anchor="w", pady=(0, 4))

    Disco_Label = ctk.CTkLabel(frame_metriche_interno, text="Spazio Disco", font=("Arial", 13, "bold"))
    Disco_Label.pack(anchor="w", pady=(10, 3))
    Disco_Bar = ctk.CTkProgressBar(frame_metriche_interno, width=440, height=10, progress_color=ARANCIO, corner_radius=5)
    Disco_Bar.set(0)
    Disco_Bar.pack(pady=(0, 2))
    Disco_Dettaglio = ctk.CTkLabel(frame_metriche_interno, text="", font=("Arial", 11), text_color="gray")
    Disco_Dettaglio.pack(anchor="w", pady=(0, 6))

    Gpu_Label = ctk.CTkLabel(frame_metriche_interno, text="Utilizzo GPU", font=("Arial", 13, "bold"))
    Gpu_Label.pack(anchor="w", pady=(10, 3))
    Gpu_Bar = ctk.CTkProgressBar(frame_metriche_interno, width=440, height=10, progress_color="#9b59b6", corner_radius=5)
    Gpu_Bar.set(0)
    Gpu_Bar.pack(pady=(0, 2))
    Gpu_Dettaglio = ctk.CTkLabel(frame_metriche_interno, text="", font=("Arial", 11), text_color="gray")
    Gpu_Dettaglio.pack(anchor="w", pady=(0, 4))

    def leggi_dati_gpu():
        if not GPU_DISPONIBILE:
            return 0, None, "GPU non rilevata"

        try:
            gpu = pynvml.nvmlDeviceGetHandleByIndex(0)
            utilizzo = pynvml.nvmlDeviceGetUtilizationRates(gpu).gpu
            memoria = pynvml.nvmlDeviceGetMemoryInfo(gpu)
            memoria_usata_gb = round(memoria.used / 1024**3, 2)
            memoria_totale_gb = round(memoria.total / 1024**3, 2)

            try:
                # LETTURA TEMPERATURA SEPARATA PER EVITARE CHE LA GPU POSSA NASCONDERLA
                temperatura = pynvml.nvmlDeviceGetTemperature(gpu, pynvml.NVML_TEMPERATURE_GPU)
            except Exception:
                temperatura = None

            dettaglio = f"{memoria_usata_gb} GB usati di {memoria_totale_gb} GB VRAM"
            return utilizzo, temperatura, dettaglio
        except Exception:
            return 0, None, "GPU non rilevata"

    def aggiorna_dati():
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disco = psutil.disk_usage("/")
        gpu_percento, gpu_temperatura, gpu_dettaglio = leggi_dati_gpu()

        ram_totale_gb = round(ram.total / 1024**3, 2)
        ram_usata_gb = round((ram.total - ram.available) / 1024**3, 2)
        disco_usato_gb = round(disco.used / 1024**3, 2)
        disco_libero_gb = round(disco.free / 1024**3, 2)

        cpu_color = VERDE if cpu < 50 else (ARANCIO if cpu < 80 else ROSSO)
        Cpu_Bar.configure(progress_color=cpu_color)

        Cpu_Label.configure(text=f"Carico CPU  —  {cpu}%")
        Cpu_Bar.set(cpu / 100)
        Ram_Label.configure(text=f"Utilizzo RAM  —  {ram.percent}%")
        Ram_Bar.set(ram.percent / 100)
        Ram_Dettaglio.configure(text=f"{ram_usata_gb} GB usati di {ram_totale_gb} GB totali")
        Disco_Label.configure(text=f"Spazio Disco  —  {disco.percent}%")
        Disco_Bar.set(disco.percent / 100)
        Disco_Dettaglio.configure(text=f"{disco_usato_gb} GB occupati  |  {disco_libero_gb} GB disponibili")

        if gpu_temperatura is not None:
            gpu_color = VERDE if gpu_temperatura < 70 else (ARANCIO if gpu_temperatura < 85 else ROSSO)
            Gpu_Label.configure(text=f"Utilizzo GPU  —  {gpu_percento}%  |  {gpu_temperatura}°C")
        else:
            gpu_color = "#9b59b6"
            Gpu_Label.configure(text=f"Utilizzo GPU  —  {gpu_percento}%")

        Gpu_Bar.configure(progress_color=gpu_color)
        Gpu_Bar.set(gpu_percento / 100)
        Gpu_Dettaglio.configure(text=gpu_dettaglio)

    aggiorna_dati()

    frame_btn = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_btn.pack(pady=16)

    ctk.CTkButton(frame_btn, text="Aggiorna", font=("Arial", 13), width=160, height=38, corner_radius=8, command=aggiorna_dati).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="← Menu", font=("Arial", 13), width=160, height=38, corner_radius=8, fg_color="transparent", border_width=1, command=menu_principale).pack(side="left", padx=8)


# INTERFACCIA PASSWORD MANAGER
def menu_password():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="Password Manager", font=("Arial", 28, "bold")).pack(pady=(0, 6))
    ctk.CTkLabel(frame_pagina, text="Gestisci le tue credenziali in modo sicuro", font=("Arial", 12), text_color="gray").pack(pady=(0, 32))

    ctk.CTkButton(frame_pagina, text="➕   Registra Nuova Password", font=("Arial", 14), width=300, height=44, corner_radius=10, command=registra_password).pack(pady=7)
    ctk.CTkButton(frame_pagina, text="🔎   Recupera Credenziali", font=("Arial", 14), width=300, height=44, corner_radius=10, command=recupera_password_ui).pack(pady=7)
    ctk.CTkButton(frame_pagina, text="📋   Mostra Elenco Vault", font=("Arial", 14), width=300, height=44, corner_radius=10, command=vault_ui).pack(pady=7)

    ctk.CTkButton(frame_pagina, text="← Menu", font=("Arial", 12), width=160, height=34, corner_radius=8, fg_color="transparent", border_width=1, command=menu_principale).pack(pady=28)


def registra_password():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="Registra Password", font=("Arial", 26, "bold")).pack(pady=(0, 6))
    ctk.CTkLabel(frame_pagina, text="Aggiungi nuove credenziali al vault", font=("Arial", 12), text_color="gray").pack(pady=(0, 22))

    campo_app = ctk.CTkEntry(frame_pagina, placeholder_text="Nome App / Sito Web", width=320, height=40, corner_radius=8)
    campo_app.pack(pady=7)

    campo_utente = ctk.CTkEntry(frame_pagina, placeholder_text="Username / Email", width=320, height=40, corner_radius=8)
    campo_utente.pack(pady=7)

    campo_password = ctk.CTkEntry(frame_pagina, placeholder_text="Password", show="*", width=320, height=40, corner_radius=8)
    campo_password.pack(pady=7)

    def invia_dati():
        if not campo_app.get() or not campo_utente.get() or not campo_password.get():
            messagebox.showwarning("Errore", "Tutti i campi sono obbligatori!")
            return
        sicurezza.salva_password(campo_app.get(), campo_utente.get(), campo_password.get())
        messagebox.showinfo("Successo", "Credenziali salvate nel database cifrato.")
        menu_password()

    frame_btn = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_btn.pack(pady=20)

    ctk.CTkButton(frame_btn, text="Salva nel Vault", font=("Arial", 13, "bold"), fg_color=VERDE, hover_color=VERDE_HOVER, width=170, height=40, corner_radius=8, command=invia_dati).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="Annulla", font=("Arial", 13), width=170, height=40, corner_radius=8, fg_color="transparent", border_width=1, command=menu_password).pack(side="left", padx=8)


def recupera_password_ui():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="Recupera Password", font=("Arial", 26, "bold")).pack(pady=(0, 6))
    ctk.CTkLabel(frame_pagina, text="Cerca le credenziali per nome app o sito", font=("Arial", 12), text_color="gray").pack(pady=(0, 22))

    # CAMPO DI TESTO LIBERO
    campo_app = ctk.CTkEntry(frame_pagina, placeholder_text="Nome App / Sito Web", width=320, height=40, corner_radius=8)
    campo_app.pack(pady=8)

    # CARD RISULTATO (Dimensione fissa per evitare scatti nell'interfaccia)
    card_risultato = ctk.CTkFrame(frame_pagina, width=360, height=80, corner_radius=12, fg_color="transparent")
    card_risultato.pack(pady=14)
    card_risultato.pack_propagate(False)

    etichetta_risultato = ctk.CTkLabel(card_risultato, text="", font=("Arial", 13, "bold"), justify="left")
    etichetta_risultato.place(relx=0.5, rely=0.5, anchor="center")

    def esegui_ricerca():
        nome_cercato = campo_app.get().strip()
        if not nome_cercato:
            messagebox.showwarning("Attenzione", "Inserisci il nome del servizio da cercare.")
            return

        try:
            risultato = sicurezza.recupera_password(nome_cercato)
            
            if risultato:
                card_risultato.configure(fg_color="#1e3a2a")
                etichetta_risultato.configure(text=f"👤  {risultato[0]}\n🔑  {risultato[1]}", text_color=VERDE)
            else:
                card_risultato.configure(fg_color="#3a1e1e")
                etichetta_risultato.configure(text="❌  Elemento non trovato nel database.", text_color=ROSSO)
                
        except InvalidToken:
            # INTERCETTAZIONE ERRORE SE LA CHIAVE DI DECIFRATURA È ERRATA
            card_risultato.configure(fg_color="#3a1e1e")
            etichetta_risultato.configure(text="⚠️  Errore: Impossibile decifrare i dati.\nLa chiave simmetrica non è valida.", text_color=ROSSO)
        except Exception as e:
            # Gestisce altri imprevisti (es. disconnessione improvvisa dal DB remoto)
            card_risultato.configure(fg_color="#3a1e1e")
            etichetta_risultato.configure(text="⚠️  Errore critico durante la decifratura.", text_color=ROSSO)

    frame_btn = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_btn.pack(pady=8)

    ctk.CTkButton(frame_btn, text="Cerca", font=("Arial", 13), width=170, height=38, corner_radius=8, command=esegui_ricerca).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="← Indietro", font=("Arial", 13), width=170, height=38, corner_radius=8, fg_color="transparent", border_width=1, command=menu_password).pack(side="left", padx=8)


# INTERFACCIA VAULT
def vault_ui():
    pulisci_finestra()

    frame_pagina = ctk.CTkFrame(app, fg_color="transparent")
    frame_pagina.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame_pagina, text="Vault Cifrato", font=("Arial", 28, "bold")).pack(pady=(0, 4))
    ctk.CTkLabel(frame_pagina, text="Elenco dei servizi archiviati suddivisi in pagine fisse", font=("Arial", 12), text_color="gray").pack(pady=(0, 16))

    lista_chiavi = []
    pagina_corrente = [0]
    ELEMENTI_PER_PAGINA = 5

    frame_bacheca = ctk.CTkFrame(frame_pagina, width=440, height=180, fg_color="#2b2b2b", corner_radius=10)
    frame_bacheca.pack(pady=6)
    frame_bacheca.pack_propagate(False)

    etichetta_pagine = ctk.CTkLabel(frame_pagina, text="Pagina 0 di 0", font=("Arial", 11), text_color="gray")
    etichetta_pagine.pack()

    frame_navigazione = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_navigazione.pack(pady=4)

    btn_prev = ctk.CTkButton(frame_navigazione, text="◀ Precedente", font=("Arial", 11), width=95, height=26, state="disabled")
    btn_prev.pack(side="left", padx=4)

    btn_next = ctk.CTkButton(frame_navigazione, text="Successivo ▶", font=("Arial", 11), width=95, height=26, state="disabled")
    btn_next.pack(side="left", padx=4)

    frame_btn = ctk.CTkFrame(frame_pagina, fg_color="transparent")
    frame_btn.pack(pady=12)

    bottone_aggiorna = ctk.CTkButton(frame_btn, text="Aggiorna Lista", font=("Arial", 13), width=160, height=38, corner_radius=8)
    bottone_aggiorna.pack(side="left", padx=8)

    bottone_indietro = ctk.CTkButton(frame_btn, text="← Indietro", font=("Arial", 13), width=160, height=38, corner_radius=8, fg_color="transparent", border_width=1, command=menu_password)
    bottone_indietro.pack(side="left", padx=8)

    def renderizza_pagina():
        for widget in frame_bacheca.winfo_children():
            widget.destroy()
            
        if not lista_chiavi:
            ctk.CTkLabel(frame_bacheca, text="Il vault è vuoto.", font=("Arial", 13, "italic"), text_color="gray").place(relx=0.5, rely=0.5, anchor="center")
            etichetta_pagine.configure(text="Pagina 0 di 0")
            btn_prev.configure(state="disabled")
            btn_next.configure(state="disabled")
            return

        totale_pagine = (len(lista_chiavi) - 1) // ELEMENTI_PER_PAGINA + 1
        etichetta_pagine.configure(text=f"Pagina {pagina_corrente[0] + 1} di {totale_pagine}")

        inizio = pagina_corrente[0] * ELEMENTI_PER_PAGINA
        fine = inizio + ELEMENTI_PER_PAGINA
        porzione = lista_chiavi[inizio:fine]

        for chiave in porzione:
            ctk.CTkLabel(frame_bacheca, text=f"🔐  {chiave}", font=("Courier New", 12), anchor="w").pack(fill="x", padx=15, pady=4)

        btn_prev.configure(state="normal" if pagina_corrente[0] > 0 else "disabled")
        btn_next.configure(state="normal" if fine < len(lista_chiavi) else "disabled")

    def cambia_pagina(direzione):
        pagina_corrente[0] += direzione
        renderizza_pagina()

    btn_prev.configure(command=lambda: cambia_pagina(-1))
    btn_next.configure(command=lambda: cambia_pagina(1))

    def collega_funzionalità():
        def visualizza_lista():
            nonlocal lista_chiavi
            try:
                lista_chiavi = sicurezza.ottieni_lista_applicazioni()
                pagina_corrente[0] = 0
                renderizza_pagina()
            except Exception:
                for widget in frame_bacheca.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(frame_bacheca, text="Errore di caricamento dal database remoto.", font=("Arial", 12), text_color=ROSSO).place(relx=0.5, rely=0.5, anchor="center")

        bottone_aggiorna.configure(command=visualizza_lista)
        visualizza_lista()

    app.after(0, collega_funzionalità)