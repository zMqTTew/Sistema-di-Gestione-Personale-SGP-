import os
import shutil
import sicurezza

# LOGICA FILE MANAGER
TIPI_FILE = {
    "Immagini": [".jpg", ".png", ".jpeg"],
    "Documenti": [".pdf", ".docx", ".txt"],
    "Video": [".mp4", ".mkv"],
    "Audio": [".mp3"]
}

def anteprima_cartella(cartella):
    elementi = []
    for file in os.listdir(cartella):
        percorso = os.path.join(cartella, file)

        if os.path.isdir(percorso):
            elementi.append(f"📁 {file}")
        else:
            estensione = os.path.splitext(file)[1].lower()
            icona = "📄"

            if estensione in [".jpg", ".png", ".jpeg"]:
                icona = "🖼️"
            elif estensione in [".mp4", ".mkv"]:
                icona = "🎬"
            elif estensione == ".mp3":
                icona = "🎵"

            elementi.append(f"{icona} {file}")

    return elementi[:30]

def cartella_ordinata(cartella):
    for file in os.listdir(cartella):
        percorso = os.path.join(cartella, file)

        if os.path.isdir(percorso):
            continue

        estensione = os.path.splitext(file)[1].lower()
        trovato = False
        
        for categoria, estensioni in TIPI_FILE.items():
            if estensione in estensioni:
                if not os.path.exists(os.path.join(cartella, categoria, file)):
                    return False
                trovato = True
                break

        if not trovato:
            if not os.path.exists(os.path.join(cartella, "Altro", file)):
                return False

    return True

def organizza_cartella(cartella):
    for file in os.listdir(cartella):
        percorso = os.path.join(cartella, file)

        if os.path.isdir(percorso):
            continue

        estensione = os.path.splitext(file)[1].lower()
        spostato = False

        for categoria, estensioni in TIPI_FILE.items():
            if estensione in estensioni:
                destinazione = os.path.join(cartella, categoria)
                os.makedirs(destinazione, exist_ok=True)
                shutil.move(percorso, os.path.join(destinazione, file))
                sicurezza.scrivi_log(f"Spostato {file} -> {categoria}")
                spostato = True
                break

        if not spostato:
            destinazione = os.path.join(cartella, "Altro")
            os.makedirs(destinazione, exist_ok=True)
            shutil.move(percorso, os.path.join(destinazione, file))