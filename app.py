from flask import Flask, render_template, request, send_from_directory, abort
import os
import re
import json
import time
import logging
from datetime import datetime
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

app = Flask(__name__)

# Dossier où seront enregistrés les fichiers QR
OUTPUT_FOLDER = "static/qrcodes"
HISTORY_FILE = "history.json"
LOG_FILE = "app.log"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- SETUP LOGGING ----------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("Application démarrée.")

# ---------- Chargement de l'historique ----------
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history_cache = json.load(f)
else:
    history_cache = []


def secure_filename(filename):
    """Empêche des noms illégaux ou des attaques."""
    original = filename
    filename = filename.strip().replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9._-]", "", filename)

    if filename != original:
        logging.warning(f"Nom de fichier nettoyé : '{original}' -> '{filename}'")

    return filename


# ---------- Filtre pour afficher les dates ----------
@app.template_filter("datetime")
def datetime_filter(value):
    return datetime.fromtimestamp(value).strftime("%d/%m/%Y %H:%M")


@app.route("/")
def index():
    logging.info("Page d'accueil affichée.")
    return render_template("index.html", history=history_cache)


@app.route("/generate", methods=["POST"])
def generate():
    link = request.form.get("link", "").strip()
    filename = request.form.get("filename", "").strip()

    logging.info(f"Requête de génération reçue. Lien = '{link}', filename = '{filename}'")

    if not link:
        logging.error("Aucun lien fourni dans le formulaire.")
        return render_template("index.html", error="Veuillez entrer un lien.", history=history_cache)

    filename = secure_filename(filename)

    if not filename:
        logging.error("Nom de fichier invalide.")
        return render_template("index.html", error="Nom de fichier invalide.", history=history_cache)

    if not filename.endswith(".png"):
        filename += ".png"

    filepath = os.path.join(OUTPUT_FOLDER, filename)

    # ---------- Si fichier déjà existant, gain de vitesse ----------
    if os.path.exists(filepath):
        logging.info(f"QR déjà existant, aucune régénération : {filename}")
    else:
        try:
            logging.info(f"Génération du QR code : {filename}")

            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=4,
                error_correction=qrcode.constants.ERROR_CORRECT_M
            )

            qr.add_data(link)
            qr.make(fit=True)

            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer()
            )

            img.save(filepath)

            logging.info(f"QR généré et sauvegardé : {filepath}")

            # Ajout dans l'historique
            new_entry = {
                "filename": filename,
                "link": link,
                "path": f"/static/qrcodes/{filename}",
                "timestamp": int(time.time())
            }

            history_cache.append(new_entry)

            with open(HISTORY_FILE, "w") as f:
                json.dump(history_cache, f, indent=4)

            logging.info(f"Ajout à l'historique : {filename}")

        except Exception as e:
            logging.exception("Erreur lors de la génération du QR code.")
            return render_template("index.html", error=f"Erreur lors de la génération : {e}", history=history_cache)

    return render_template(
        "index.html",
        link=link,
        filename=filename,
        qr_path=f"/static/qrcodes/{filename}",
        history=history_cache
    )


@app.route("/download/<filename>")
def download(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(filepath):
        logging.error(f"Tentative de téléchargement d'un fichier inexistant : {filename}")
        abort(404)

    logging.info(f"Téléchargement du fichier : {filename}")
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route("/purge", methods=["POST"])
def purge_history():
    logging.warning("Purge de l'historique et suppression des fichiers QR demandée.")

    # 1. Vider le cache en mémoire
    history_cache.clear()

    # 2. Sauvegarder un fichier JSON vide
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

    # 3. Supprimer les fichiers du dossier static/qrcodes
    removed_files = 0
    for file in os.listdir(OUTPUT_FOLDER):
        path = os.path.join(OUTPUT_FOLDER, file)
        try:
            os.remove(path)
            removed_files += 1
        except Exception as e:
            logging.error(f"Erreur suppression {file} : {e}")

    logging.info(f"Purge terminée. Fichiers supprimés : {removed_files}")

    return render_template("index.html", history=history_cache, message="Historique purgé avec succès !")
    
if __name__ == "__main__":
    logging.info("Serveur Flask lancé en mode debug.")
    app.run(debug=True)