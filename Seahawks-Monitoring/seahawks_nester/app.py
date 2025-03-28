from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

DATABASE_FILE = "database.json"

def load_data():
    if not os.path.exists(DATABASE_FILE):
        return {"sondes": []}
    try:
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"sondes": []}

def save_data(data):
    try:
        with open(DATABASE_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("❌ Erreur de sauvegarde :", e)

@app.route("/")
def home():
    data = load_data()
    sondes = data.get("sondes", [])
    return render_template("dashboard.html", sondes=sondes)

@app.route("/api/upload_sonde", methods=["POST"])
def upload_sonde():
    new_data = request.json
    if not new_data:
        return jsonify({"message": "❌ Aucune donnée reçue"}), 400

    data = load_data()
    sondes = data.get("sondes", [])

    existing_ips = {s['ip'] for s in new_data if 'ip' in s}
    sondes = [s for s in sondes if s.get("ip") not in existing_ips]

    sondes.extend(new_data)
    data["sondes"] = sondes

    save_data(data)
    print("✅ Nouvelles sondes enregistrées :", new_data)
    return jsonify({"message": "Données enregistrées"}), 201

@app.route("/api/sondes", methods=["GET"])
def get_sondes():
    data = load_data()
    return jsonify(data.get("sondes", []))

@app.route("/sonde/<int:sonde_id>")
def get_sonde(sonde_id):
    data = load_data()
    sondes = data.get("sondes", [])
    
    if 0 <= sonde_id < len(sondes):
        sonde = sondes[sonde_id]
        return render_template("sonde_detail.html", sonde=sonde)
    else:
        return "Sonde non trouvée", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
