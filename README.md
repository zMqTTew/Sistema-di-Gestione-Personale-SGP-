# Sistema-di-Gestione-Personale-SGP-
Progetto personale per lo sviluppo di una suite di utilità personali (File Manager, Password Manager, Stato PC).

---

## 📐 Architettura del Software (Struttura Modulare)

Questo progetto segue i principi della **modularità** ed è suddiviso in moduli indipendenti per garantire scalabilità e manutenibilità:

* `main.py`: Il punto di ingresso dell'applicazione. Si occupa di verificare i requisiti hardware/software, inizializzare la finestra principale e avviare il ciclo dell'applicazione.
* `interfaccia.py`: Gestisce l'intera interfaccia grafica (GUI). Contiene la logica di visualizzazione delle finestre, dei pulsanti d'azione, delle barre di progresso e del sistema di switch dinamico tra i menu.
* `sicurezza.py`: Il nucleo crittografico del sistema. Gestisce la generazione degli hash, la derivazione delle chiavi, l'apertura/chiusura del caveau cifrato e la scrittura della cronologia di sistema (`log.txt`).
* `gestore_file.py`: Contiene le regole di business e la logica di I/O per la scansione delle directory e il riordino automatizzato dei file in base alle estensioni.

---

## 🛠️ Funzionalità Principali

### 1. 📁 File Manager
Consente l'analisi preventiva di una directory per verificare se è già strutturata. In caso negativo, un algoritmo sposta e organizza automaticamente i file all'interno di cartelle dedicate (`Immagini`, `Documenti`, `Video`, `Audio`, `Altro`) in base alla loro estensione.

### 2. 🔐 Password Manager
Un registro locale sicuro per salvare e recuperare credenziali. La sicurezza è garantita da:
* **Hashing della Master Password:** Tramite algoritmo `SHA-256`.
* **Derivazione della Chiave:** Utilizzo del protocollo `PBKDF2HMAC` con *salt* generato casualmente tramite funzioni crittografiche del sistema operativo (`os.urandom`).
* **Cifratura Simmetrica:** Le password dei singoli siti vengono salvate nel file `vault.json` cifrate tramite algoritmo **AES-256** (implementazione *Fernet*).

### 3. 💻 Monitoraggio Stato PC
Grafica in tempo reale integrata con la libreria `psutil`. Mostra l'utilizzo percentuale e i dettagli quantitativi di:
* Carico della CPU
* Memoria RAM (Usata vs Totale in GB)
* Spazio di archiviazione su Disco (Usato vs Libero in GB)

---

## 🚀 Installazione e Requisiti

L'applicazione è progettata per funzionare interamente in locale, senza appoggiarsi a server esterni (garantendo una moderata privacy dei dati).

### 1. Installazione delle dipendenze
Per eseguire il codice dai sorgenti, installa i moduli richiesti tramite il comando:
```bash
py -m pip install -r requirements.txt
