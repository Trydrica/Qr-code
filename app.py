from flask import Flask, render_template, request, send_from_directory
import qrcode
import os

app = Flask(__name__)

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

    # Génération du QR code
    img = qrcode.make(link)
    img.save(filepath)

    return render_template(
        "index.html",
        link=link,
        filename=filename,
        qr_path=f"/static/qrcodes/{filename}"
    )

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)