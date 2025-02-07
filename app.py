from flask import Flask, render_template
import nmap

app = Flask(__name__)


def perform_network_scan():
    # Spécifier explicitement le chemin de nmap.exe
    nm = nmap.PortScanner()

    # Scanner une plage réseau
    nm.scan(hosts='192.168.1.0/24', arguments='-sS -p 22,80,443')

    # Stocker les résultats
    scan_results = []
    for host in nm.all_hosts():
        open_ports = []
        if 'tcp' in nm[host]:
            for port, details in nm[host]['tcp'].items():
                if details['state'] == 'open':
                    open_ports.append(port)
        
        scan_results.append({
            "ip": host,
            "hostname": nm[host].hostname(),
            "status": nm[host].state(),
            "open_ports": open_ports
        })

    return scan_results

@app.route("/")
def home():
    # Simuler des données pour le tableau de bord
    data = {
        "local_ip": "192.168.1.10",
        "vm_name": "Seahawks-VM",
        "connected_machines": 5,
        "last_scan": [
            {"ip": "192.168.1.2", "status": "open"},
            {"ip": "192.168.1.3", "status": "closed"}
        ],
        "latency": "15ms",
        "version": "1.0.0"
    }
    return render_template("dashboard.html", data=data)

# Route pour le scan
@app.route("/scan")
def scan():
    return render_template("loading.html")  # Affiche la page de chargement

# Route pour afficher les résultats après le scan
@app.route("/scan/results")
def scan_results():
    results = perform_network_scan()
    return render_template("scan.html", results=results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

