from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from PIL import Image
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Verzeichnis zum Speichern der Bilder
UPLOAD_FOLDER = 'uploaded_images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return "Server läuft. Web-Frontend ist bereit."

@app.route('/upload', methods=['POST'])
def upload_image():
    username = request.form.get('username')
    file = request.files['image']
    if not username or not file:
        return jsonify({'error': 'Benutzername oder Datei fehlt'}), 400

    # Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{username}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Bild speichern
    image = Image.open(file)
    image.save(filepath)

    # Bild an alle Clients senden
    socketio.emit('new_image', {'username': username, 'filepath': filename})

    return jsonify({'message': 'Bild erfolgreich hochgeladen'}), 200

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)
