from flask import Flask, render_template
import socket
import os
import subprocess
import nmap
import time
import statistics

app = Flask(__name__)

def get_local_network():
    """Récupère l'adresse IP locale et la plage réseau"""
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = ".".join(local_ip.split(".")[:-1]) + ".0/24"
        return local_ip, network_prefix
    except Exception as e:
        return "Erreur", "192.168.1.0/24"

def perform_network_scan():
    """Effectue un scan réseau sur les ports 22, 80, 443, 3389, 3306"""
    nm = nmap.PortScanner()
    local_ip, network_prefix = get_local_network()

    try:
        nm.scan(hosts=network_prefix, arguments='-sS -p 22,80,443,3389,3306')
        scan_results = []

        for host in nm.all_hosts():
            open_ports = []
            if 'tcp' in nm[host]:
                for port, details in nm[host]['tcp'].items():
                    if details['state'] == 'open':
                        open_ports.append(str(port))  # Convertir les ports en chaînes

            scan_results.append({
                "ip": host,
                "hostname": nm[host].hostname() if nm[host].hostname() else "Inconnu",
                "status": nm[host].state(),
                "open_ports": open_ports if open_ports else ["Aucun"]
            })

        return scan_results
    except Exception as e:
        return [{"ip": "Erreur", "hostname": "N/A", "status": "N/A", "open_ports": [str(e)]}]

def get_latency():
    """Mesure la latence WAN en pingant Google"""
    try:
        target = "8.8.8.8"
        latencies = []

        for _ in range(4):  # Effectuer 4 pings
            start_time = time.time()
            response = os.system("ping -c 1 " + target if os.name != "nt" else "ping -n 1 " + target)
            end_time = time.time()

            if response == 0:
                latencies.append((end_time - start_time) * 1000)  # Convertir en ms
        
        if latencies:
            return f"{round(statistics.mean(latencies), 2)} ms"
        return "Indisponible"
    except Exception as e:
        return f"Erreur : {e}"

@app.route("/")
def home():
    """Affiche le tableau de bord"""
    local_ip, network_prefix = get_local_network()
    vm_name = socket.gethostname()

    # Scan rapide pour détecter les machines connectées
    nm = nmap.PortScanner()
    nm.scan(hosts=network_prefix, arguments='-sn')
    connected_machines = len(nm.all_hosts())

    data = {
        "local_ip": local_ip,
        "vm_name": vm_name,
        "connected_machines": connected_machines,
        "latency": get_latency(),
        "version": "1.0.0",
        "last_scan": perform_network_scan()
    }

    return render_template("dashboard.html", data=data)

@app.route("/scan")
def scan():
    """Affiche une page de chargement avant le scan"""
    return render_template("loading.html")

@app.route("/scan/results")
def scan_results():
    """Affiche les résultats du scan réseau"""
    results = perform_network_scan()
    return render_template("scan.html", results=results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
