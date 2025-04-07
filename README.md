# Seahawks Monitoring 🏈

Projet de supervision réseau développé dans le cadre de la certification RNCP n°35594 – Bloc E6.1  
**Objectif :** Concevoir une application répartie client/serveur pour centraliser la supervision réseau des franchises NFL.

---

## 🧰 Getting started

Voici comment démarrer rapidement le projet en local.

### 🔧 Prérequis :
- Docker
- Docker Compose

### ▶️ Lancer les conteneurs :

```bash
git clone https://gitlab.com/mariamadide.diallo.1/seahawks_monitoring.git
cd seahawks_monitoring
docker-compose up --build
```

📍 Accès :
- Harvester (client) : http://localhost:5000  
- Nester (serveur) : http://localhost:5001

---

## 🧱 Structure du projet

```
seahawks_monitoring/
├── seahawks_harvester/   # Application de scan local (Flask)
├── seahawks_nester/      # Serveur web de supervision (Flask + JSON)
├── docker-compose.yml
└── README.md
```

---

## 🚀 Fonctionnalités principales

### Seahawks Harvester (Client)
- Scan réseau local (IP + ports ouverts)
- Latence WAN
- Dashboard local (Flask)
- Envoi automatique au serveur Nester
- Rapport HTML/JSON généré localement

### Seahawks Nester (Serveur)
- API REST pour recevoir les données
- Stockage en base JSON
- Dashboard web avec liste des sondes
- Vue détaillée de chaque sonde + scan

---

## 🧪 Tests

Des tests unitaires sont disponibles pour chaque module :

```bash
docker exec -it seahawks_harvester pytest
docker exec -it seahawks_nester pytest
```

---

## 📦 CI/CD

Le projet intègre GitLab CI pour :
- Lancer les tests automatiquement
- Construire les images Docker
- Préparer un déploiement via `docker-compose`

---

## 🔜 Prochaines évolutions (Bloc TPTE511)

- Télémaintenance à distance
- Tunnel sécurisé
- Gestion d’utilisateurs
- Haute disponibilité via cluster

---

📁 Dépôt GitLab :  
[https://gitlab.com/mariamadide.diallo.1/seahawks_monitoring](https://gitlab.com/mariamadide.diallo.1/seahawks_monitoring)
