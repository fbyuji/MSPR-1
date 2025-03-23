from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

DATABASE_FILE = "/app/database/database.json"

def load_data():
    if not os.path.exists(DATABASE_FILE):
        return {"sondes": []}

    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    data = load_data()
    return render_template("dashboard.html", sondes=data["sondes"])

@app.route("/api/upload_scan", methods=["POST"])
def receive_scan():
    scan_data = request.get_json(force=True)
    if not scan_data:
        return jsonify({"message": "❌ Aucune donnée reçue"}), 400

    if not isinstance(scan_data, list):
        scan_data = [scan_data] 

    data = load_data()

    for scan in scan_data:
        sonde_existante = next((s for s in data["sondes"] if s["ip"] == scan["ip"]), None)

        scan_entry = {
            "ip": scan["ip"],
            "open_ports": scan["open_ports"],
            "status": scan["status"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if sonde_existante:
            sonde_existante.update({
                "hostname": scan["hostname"],
                "status": scan["status"],
                "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "open_ports": scan["open_ports"]
            })

            if "scans" not in sonde_existante:
                sonde_existante["scans"] = []

            sonde_existante["scans"].append(scan_entry)

        else:
            data["sondes"].append({
                "id": len(data["sondes"]),
                "ip": scan["ip"],
                "hostname": scan["hostname"],
                "status": scan["status"],
                "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "open_ports": scan["open_ports"],
                "scans": [scan_entry]
            })

    save_data(data)
    return jsonify({"message": "✅ Scan reçu avec succès"}), 201

@app.route("/api/scans", methods=["GET"])
def get_all_scans():
    data = load_data()
    return jsonify(data)

@app.route("/api/sondes/<int:sonde_id>", methods=["GET"])
def get_sonde(sonde_id):
    data = load_data()

    if sonde_id < 0 or sonde_id >= len(data["sondes"]):
        return jsonify({"message": "❌ Sonde introuvable"}), 404

    sonde = data["sondes"][sonde_id]
    sonde["id"] = sonde_id

    return render_template("details_sonde.html", sonde=sonde, sonde_id=sonde_id)

@app.route("/api/sondes/<int:sonde_id>/last_scan", methods=["GET"])
def get_last_scan(sonde_id):
    data = load_data()

    if sonde_id < 0 or sonde_id >= len(data["sondes"]):
        return jsonify({"message": "❌ Sonde introuvable"}), 404

    sonde = data["sondes"][sonde_id]

    if "last_scan" not in sonde or "open_ports" not in sonde:
        return jsonify({"message": "❌ Aucun scan trouvé pour cette sonde"}), 404

    last_scan_info = {
        "ip": sonde["ip"],
        "hostname": sonde.get("hostname", "Inconnu"),
        "status": sonde.get("status", "Inconnu"),
        "last_scan": sonde["last_scan"],
        "open_ports": sonde["open_ports"]
    }

    return render_template("last_scan.html", sonde=last_scan_info, sonde_id=sonde_id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
