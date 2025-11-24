from flask import Flask, render_template, request, send_from_directory
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

app = Flask(__name__)

# Dossier où seront enregistrés les QR codes
OUTPUT_FOLDER = "static/qrcodes"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    link = request.form.get("link")
    filename = request.form.get("filename")

    if not link:
        return render_template("index.html", error="Veuillez entrer un lien.")

    if not filename.endswith(".png"):
        filename += ".png"

    filepath = os.path.join(OUTPUT_FOLDER, filename)

    # QR code stylisé
    qr = qrcode.QRCode(
        version=3,
        box_size=100,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer()
    )

    img.save(filepath)

    return render_template(
        "index.html",
        link=link,
        filename=filename,
        qr_path=f"/static/qrcodes/{filename}",
    )

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)