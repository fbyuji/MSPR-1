from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

DATABASE_FILE = "database.json"

def load_data():
    """Charge les données du fichier JSON"""
    try:
        if not os.path.exists(DATABASE_FILE):
            print("⚠️ Le fichier database.json n'existe pas, création en cours...")
            return {"scans": []}

        with open(DATABASE_FILE, "r") as f:
            data = json.load(f)
            print("📂 Contenu du fichier database.json :", data)  # ✅ Débogage
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("❌ Erreur lors du chargement de database.json :", e)  # ✅ Affiche l'erreur
        return {"scans": []}

def save_data(data):
    """Sauvegarde les résultats de scan"""
    try:
        with open(DATABASE_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("✅ Données sauvegardées dans database.json")
    except Exception as e:
        print("❌ Erreur lors de la sauvegarde :", e)

@app.route("/")
def home():
    """Affiche directement la page de tableau de bord"""
    data = load_data()
    
    if "scans" not in data or not isinstance(data["scans"], list):
        print("⚠️ Problème avec les données chargées :", data)
        scans = []
    else:
        scans = data["scans"]
    
    print("📊 Affichage des scans :", scans)  # ✅ Vérification
    
    return render_template("dashboard.html", scans=scans)

@app.route("/api/upload_scan", methods=["POST"])
def receive_scan():
    """Réception des scans depuis Harvester"""
    scan_data = request.json
    if not scan_data:
        return jsonify({"message": "❌ Aucune donnée reçue"}), 400

    # Ajout du scan dans la base de données
    data = load_data()
    if isinstance(scan_data, list):
        data["scans"].extend(scan_data)  # 🔥 Ajoute chaque élément de la liste individuellement
    else:
        data["scans"].append(scan_data)  # ✅ Ajoute directement un objet scan

    save_data(data)

    print("📥 Scan reçu et enregistré :", scan_data)  # ✅ Vérification

    return jsonify({"message": "✅ Scan reçu avec succès"}), 201

@app.route("/api/scans", methods=["GET"])
def get_scans():
    """Retourne tous les scans enregistrés"""
    data = load_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
