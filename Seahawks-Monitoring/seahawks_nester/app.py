from flask import Flask, request, jsonify
import json

app = Flask(__name__)

DATABASE_FILE = "database.json"

def load_data():
    """Charge les données du fichier JSON"""
    try:
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"scans": []}

def save_data(data):
    """Sauvegarde les résultats de scan"""
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    """Page d'accueil"""
    return "Seahawks Nester API est en cours d'exécution."

@app.route("/api/upload_scan", methods=["POST"])
def receive_scan():
    """Réception des scans depuis Harvester"""
    scan_data = request.json
    if not scan_data:
        return jsonify({"message": "Aucune donnée reçue"}), 400

    # Sauvegarde les données
    data = load_data()
    data["scans"].append(scan_data)
    save_data(data)

    return jsonify({"message": "Scan reçu avec succès"}), 201

@app.route("/api/scans", methods=["GET"])
def get_scans():
    """Retourne tous les scans enregistrés"""
    data = load_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
