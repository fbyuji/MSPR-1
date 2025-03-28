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
from zoneinfo import ZoneInfo 
from version import __version__

app = Flask(__name__)
last_scan_results = []

def get_local_network():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = ".".join(local_ip.split(".")[:-1]) + ".0/24"
        return local_ip, network_prefix
    except Exception:
        return "Erreur", "192.168.1.0/24"

def get_current_paris_time(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.now(ZoneInfo("Europe/Paris")).strftime(fmt)

def perform_network_scan():
    global last_scan_results
    nm = nmap.PortScanner()
    local_ip, network_prefix = get_local_network()

    try:
        nm.scan(hosts=network_prefix, arguments='-sS -p 22,80,443,3389,3306')
        scan_results = []
        timestamp = get_current_paris_time() 

        for host in nm.all_hosts():
            open_ports = []
            if 'tcp' in nm[host]:
                for port, details in nm[host]['tcp'].items():
                    if details['state'] == 'open':
                        open_ports.append(str(port))

            scan_results.append({
                "id": host.replace(".", "-"),
                "ip": host,
                "hostname": nm[host].hostname() or "Inconnu",
                "status": nm[host].state(),
                "open_ports": open_ports,
                "last_scan": timestamp
            })

        last_scan_results = scan_results
        return scan_results

    except Exception as e:
        return [{
            "id": "erreur",
            "ip": "Erreur",
            "hostname": "N/A",
            "status": "N/A",
            "open_ports": [str(e)],
            "last_scan": get_current_paris_time()
        }]

def get_latency():
    try:
        target = "8.8.8.8"
        latencies = []

        for _ in range(4):
            start_time = time.time()
            response = os.system("ping -n 1 " + target if os.name == "nt" else "ping -c 1 " + target)
            end_time = time.time()
            if response == 0:
                latencies.append((end_time - start_time) * 1000)

        return f"{round(statistics.mean(latencies), 2)} ms" if latencies else "Indisponible"
    except Exception as e:
        return f"Erreur : {e}"

def save_scan_report(scan_results):
    timestamp = get_current_paris_time(fmt="%Y-%m-%d_%H-%M-%S") 

    json_filename = f"scan_report_{timestamp}.json"
    with open(json_filename, "w") as f:
        json.dump(scan_results, f, indent=4)

    html_filename = f"scan_report_{timestamp}.html"
    with open(html_filename, "w") as f:
        f.write("<html><head><title>Rapport de Scan Réseau</title></head><body>")
        f.write("<h1>Rapport de Scan Réseau</h1>")
        for machine in scan_results:
            f.write(f"<p><strong>IP :</strong> {machine['ip']} - <strong>Ports ouverts :</strong> {', '.join(machine['open_ports'])}</p>")
        f.write("</body></html>")

    return json_filename, html_filename

def send_scan_results(scan_results):
    url = "http://seahawks_nester:5001/api/upload_sonde"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=scan_results, headers=headers)
        print("📤 Envoi au Nester :", response.status_code)
        return response.status_code
    except Exception as e:
        print("❌ Envoi échoué :", e)
        return 500

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
        "version": __version__,
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
    send_scan_results(last_scan_results)
    return render_template("scan.html", results=last_scan_results)

@app.route("/scan/download/json")
def download_json_report():
    files = sorted(glob.glob("scan_report_*.json"), reverse=True)
    return send_file(files[0], as_attachment=True) if files else ("Aucun rapport disponible", 404)

@app.route("/scan/download/html")
def download_html_report():
    files = sorted(glob.glob("scan_report_*.html"), reverse=True)
    return send_file(files[0], as_attachment=True) if files else ("Aucun rapport disponible", 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
