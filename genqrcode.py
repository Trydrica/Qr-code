import qrcode
import re

while True:
    # Demander le lien
    link = input("Entre le lien à transformer en QR Code : ")

    # Nettoyer le lien pour créer un nom de fichier valide
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', link)

    # Générer le QR Code
    img = qrcode.make(link)
    img.save(f"QR_{safe_filename}.png")

    print(f"QR Code sauvegardé sous : QR_{safe_filename}.png")

    # Demander si on recommence
    restart = input("Créer un nouveau QR Code ? (O/N) : ").strip().upper()

    if restart != "O":
        print("Fin du programme.")
        break