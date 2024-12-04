from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from PIL import Image
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Ordner für Bilder
UPLOAD_FOLDER = 'uploaded_images'
COLLAGE_FOLDER = 'collages'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COLLAGE_FOLDER, exist_ok=True)

# Maximale Anzahl der Bilder pro Collage
MAX_IMAGES_PER_COLLAGE = 16  # z.B. 4x4

# Aktuelle Bilder in der Collage
current_collage_images = []

# Startseite
@app.route('/')
def home():
    return "Server läuft. Web-Frontend ist bereit."

# Kamera-Seite für Besucher
@app.route('/camera')
def camera_page():
    return render_template('camera.html')

# Leinwand-Seite
@app.route('/leinwand')
def leinwand_page():
    return render_template('leinwand.html')

# Upload-Endpunkt für Bilder
@app.route('/upload', methods=['POST'])
def upload():
    username = request.form.get('username', 'Unbekannt')
    image = request.files.get('image')

    if not image:
        return jsonify({'message': 'Kein Bild hochgeladen'}), 400

    # Bild speichern
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{username}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    # Bild URL für das Frontend
    image_url = f"/uploaded_images/{filename}"

    # Bild zur aktuellen Collage hinzufügen
    current_collage_images.append(filepath)

    # Echtzeit-Update an Leinwand senden
    socketio.emit('new_image', {'username': username, 'image_path': image_url})

    # Überprüfen, ob die Collage voll ist
    if len(current_collage_images) >= MAX_IMAGES_PER_COLLAGE:
        save_collage(current_collage_images)
        current_collage_images.clear()
        # Benachrichtige die Leinwand, dass die Collage gespeichert wurde
        socketio.emit('collage_saved', {'message': 'Collage gespeichert und neu gestartet.'})

    return jsonify({'message': 'Bild erfolgreich hochgeladen'}), 200

# Serve hochgeladene Bilder
@app.route('/uploaded_images/<path:filename>')
def uploaded_images(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Funktion zum Speichern der Collage
def save_collage(images):
    if not images:
        return

    collage_filename = f"collage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    collage_path = os.path.join(COLLAGE_FOLDER, collage_filename)

    # Öffne alle Bilder und bereite sie für die Collage vor
    image_objects = [Image.open(img).convert('RGB') for img in images]
    grid_size = 4  # 4x4 Grid

    # Festlegen der Größe jedes Thumbnails
    thumb_width = 200
    thumb_height = 200

    # Erstellen der Thumbnails
    thumbnail_images = [img.resize((thumb_width, thumb_height)) for img in image_objects]

    # Erstellen der Collage
    collage_width = grid_size * thumb_width
    collage_height = grid_size * thumb_height
    collage = Image.new('RGB', (collage_width, collage_height), color=(255, 255, 255))

    for idx, img in enumerate(thumbnail_images):
        row = idx // grid_size
        col = idx % grid_size
        x = col * thumb_width
        y = row * thumb_height
        collage.paste(img, (x, y))

    # Speichern der Collage
    collage.save(collage_path)
    print(f"Collage gespeichert unter {collage_path}")

# Hauptprogramm
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
