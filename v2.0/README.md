# Sistema di Gestione Personale - SGP

Progetto personale per lo sviluppo di una suite di utilità personali (File Manager, Password Manager, Stato PC).

> 📌 Questo repository contiene due versioni: `v1.0/` (locale, mono-utente) e `v2.0/` (multi-utente, con database remoto). Questo README descrive la **versione 2.0**.

---

## 📐 Architettura del Software (Struttura Modulare)

Questo progetto segue i principi della **modularità** ed è suddiviso in moduli indipendenti per garantire scalabilità e manutenibilità:

* `main.py`: Il punto di ingresso dell'applicazione. Si occupa di verificare i requisiti hardware/software, inizializzare la finestra principale e avviare il ciclo dell'applicazione.
* `interfaccia.py`: Gestisce l'intera interfaccia grafica (GUI). Contiene la logica di visualizzazione delle finestre (login, registrazione, reset password, menu, file manager, password manager, stato PC) e del sistema di switch dinamico tra le schermate.
* `sicurezza.py`: Il nucleo di autenticazione e crittografia del sistema. Gestisce la connessione al database remoto, la registrazione e l'autenticazione degli utenti, la derivazione delle chiavi, la cifratura/decifratura delle credenziali e la scrittura della cronologia di sistema (`log.txt`).
* `gestore_file.py`: Contiene le regole di business e la logica di I/O per la scansione delle directory e il riordino automatizzato dei file in base alle estensioni.

---

## 🆕 Novità della versione 2.0

La v2.0 introduce un'architettura **multi-utente con database remoto**, sostituendo l'archiviazione locale della v1.0:

* **Account personali**: ogni utente registra un proprio profilo (username + Master Password), invece di un accesso libero al primo avvio.
* **Database PostgreSQL remoto**: utenti e credenziali cifrate sono salvati su un server centrale, raggiungibile tramite connessione VPN.
* **Reset password**: possibilità di reimpostare la propria Master Password tramite username.
* **Vault con elenco paginato**: visualizzazione di tutti i servizi salvati, navigabile a pagine.
* **Monitoraggio GPU**: il pannello "Stato PC" include ora anche utilizzo, temperatura e memoria VRAM della scheda video (se rilevata).

---

## 🛠️ Funzionalità Principali

### 1. 🔑 Autenticazione e Gestione Account

Il sistema richiede la creazione di un account personale per poter accedere:

* **Registrazione:** scelta di username e Master Password, con controllo automatico sui duplicati.
* **Login:** autenticazione tramite username e Master Password, verificata contro l'hash salvato nel database remoto.
* **Reset Password:** reimpostazione della Master Password tramite username, con ricalcolo di hash e salt.

### 2. 📁 File Manager

Consente l'analisi preventiva di una directory per verificare se è già strutturata. In caso negativo, un algoritmo sposta e organizza automaticamente i file all'interno di cartelle dedicate (`Immagini`, `Documenti`, `Video`, `Audio`, `Programmazione`, `Altro`) in base alla loro estensione. Se la cartella è già ordinata, il riordino non viene eseguito.

### 3. 🔐 Password Manager (Vault Cifrato)

Un registro sicuro, sincronizzato sul database remoto, per salvare e recuperare credenziali. La sicurezza è garantita da:

* **Hashing della Master Password:** tramite algoritmo `SHA-256` con *salt* casuale (`os.urandom`).
* **Derivazione della Chiave:** utilizzo del protocollo `PBKDF2HMAC` per generare una chiave simmetrica temporanea legata alla sessione di login.
* **Cifratura Simmetrica:** le password dei singoli servizi vengono cifrate tramite algoritmo **AES-256** (implementazione *Fernet*) prima di essere salvate nel database.
* **Vault navigabile:** elenco di tutti i servizi salvati, consultabile a pagine fisse.

### 4. 💻 Monitoraggio Stato PC

Grafica in tempo reale integrata con le librerie `psutil` e `pynvml`. Mostra l'utilizzo percentuale e i dettagli quantitativi di:

* Carico della CPU
* Memoria RAM (Usata vs Totale in GB)
* Spazio di archiviazione su Disco (Usato vs Libero in GB)
* Utilizzo GPU, temperatura e memoria VRAM (se una scheda video compatibile è rilevata)

---

## 🚀 Installazione e Requisiti

A differenza della v1.0, questa versione richiede una **connessione di rete attiva** (tramite VPN) per comunicare con il database PostgreSQL remoto, dove sono salvati account e credenziali cifrate.

### 1. Installazione delle dipendenze

Per eseguire il codice dai sorgenti, installa i moduli richiesti tramite il comando:

```bash
py -m pip install -r requirements.txt
```

### 2. Configurazione delle variabili d'ambiente

Le credenziali di connessione al database **non sono incluse nel codice sorgente** per motivi di sicurezza. Prima di avviare l'applicazione:

1. Copia il file `.env.example` e rinominalo in `.env`.
2. Compila i valori richiesti con i dati del tuo database PostgreSQL:

```
DB_HOST=indirizzo_ip_o_host_del_server
DB_NAME=nome_database
DB_USER=utente_postgres
DB_PASSWORD=password_postgres
DB_PORT=5432
```

⚠️ Il file `.env` non va mai condiviso o caricato su repository pubblici: è incluso nel `.gitignore` per essere escluso automaticamente.

### 3. Avvio dell'applicazione

```bash
py main.py
```

Al primo utilizzo, registra un nuovo account dalla schermata di login per iniziare a usare il Password Manager e le altre funzionalità.

---

Sviluppato da: Matteo Giorgio (Classe 5ª B Informatica)
