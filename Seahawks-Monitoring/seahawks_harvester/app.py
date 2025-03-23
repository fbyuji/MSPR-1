from flask import Flask, render_template, send_file
import socket
import os
import subprocess
import nmap
import time
import statistics
import json
import glob
import requests
from datetime import datetime

app = Flask(__name__)

last_scan_results = []  

def get_local_network():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = ".".join(local_ip.split(".")[:-1]) + ".0/24"
        return local_ip, network_prefix
    except Exception:
        return "Erreur", "192.168.1.0/24"

def perform_network_scan():
    global last_scan_results
    nm = nmap.PortScanner()
    local_ip, network_prefix = get_local_network()
    scan_results = []

    try:
        nm.scan(hosts=network_prefix, arguments='-sS -p 22,80,443,3389,3306')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for idx, host in enumerate(nm.all_hosts()):
            open_ports = []
            if 'tcp' in nm[host]:
                for port, details in nm[host]['tcp'].items():
                    if details['state'] == 'open':
                        open_ports.append(str(port))

            scan_results.append({
                "id": idx, 
                "ip": host,
                "hostname": nm[host].hostname() or "Inconnu",
                "status": nm[host].state(),
                "open_ports": open_ports if open_ports else ["Aucun"],
                "scan_time": now,  
                "last_scan_date": now,  
                "scans": [{
                    "ip": host,
                    "open_ports": open_ports if open_ports else ["Aucun"],
                    "status": nm[host].state()
                }]
            })

        last_scan_results = scan_results
        return scan_results

    except Exception as e:
        return [{
            "id": -1,
            "ip": "Erreur",
            "hostname": "N/A",
            "status": "N/A",
            "open_ports": [str(e)],
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scans": []
        }]

def get_latency():
    try:
        target = "8.8.8.8"
        latencies = []

        for _ in range(4):
            start_time = time.time()
            response = os.system("ping -c 1 " + target if os.name != "nt" else "ping -n 1 " + target)
            end_time = time.time()

            if response == 0:
                latencies.append((end_time - start_time) * 1000)

        if latencies:
            return f"{round(statistics.mean(latencies), 2)} ms"
        return "Indisponible"
    except Exception as e:
        return f"Erreur : {e}"

def save_scan_report(scan_results):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    json_filename = f"scan_report_{timestamp}.json"
    with open(json_filename, "w") as f:
        json.dump(scan_results, f, indent=4)

    html_filename = f"scan_report_{timestamp}.html"
    with open(html_filename, "w") as f:
        f.write("<html><head><title>Rapport de Scan Réseau</title></head><body>")
        f.write("<h1>Rapport de Scan Réseau</h1>")
        f.write(f"<p><strong>Date du rapport :</strong> {timestamp}</p>")  
        for machine in scan_results:
            f.write(f"<p><strong>IP :</strong> {machine['ip']} - <strong>Ports ouverts :</strong> {', '.join(machine['open_ports'])}</p>")
        f.write("</body></html>")

    return json_filename, html_filename

def send_scan_results(scan_results):
    url = "http://seahawks_nester:5001/api/upload_scan"
    headers = {"Content-Type": "application/json"}

    print("📤 Envoi des données au serveur Nester...")
    try:
        print(f"➡️ Payload : {json.dumps(scan_results)}") 
        response = requests.post(url, json=scan_results, headers=headers)
        response.raise_for_status()
        print(f"✅ Réponse serveur : {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi : {e}")

def load_version():
    try:
        with open("version.json", "r") as version_file:
            version_data = json.load(version_file)
            return version_data["version"]
    except Exception:
        return "Inconnue"

@app.route("/")
def home():
    local_ip, network_prefix = get_local_network()
    vm_name = socket.gethostname()

    nm = nmap.PortScanner()
    nm.scan(hosts=network_prefix, arguments='-sn')
    connected_machines = len(nm.all_hosts())

    data = {
        "local_ip": local_ip,
        "vm_name": vm_name,
        "connected_machines": connected_machines,
        "latency": get_latency(),
        "version": load_version(),
        "last_scan": last_scan_results
    }

    return render_template("dashboard.html", data=data)

@app.route("/scan")
def scan():
    return render_template("loading.html")

@app.route("/scan/results")
def scan_results():
    global last_scan_results
    last_scan_results = perform_network_scan()
    save_scan_report(last_scan_results)

    print("📡 Appel de send_scan_results...") 

    send_scan_results(last_scan_results)

    return render_template("scan.html", results=last_scan_results)

@app.route("/scan/download/json")
def download_json_report():
    files = sorted(glob.glob("scan_report_*.json"), reverse=True)
    if files:
        return send_file(files[0], as_attachment=True)
    return "Aucun rapport disponible", 404

@app.route("/scan/download/html")
def download_html_report():
    files = sorted(glob.glob("scan_report_*.html"), reverse=True)
    if files:
        return send_file(files[0], as_attachment=True)
    return "Aucun rapport disponible", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
