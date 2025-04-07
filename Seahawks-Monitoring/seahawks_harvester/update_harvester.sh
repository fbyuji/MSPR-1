#!/bin/bash

echo "🔄 Mise à jour du Harvester..."

GIT_USER="gitlab+deploy-token-7740950"
GIT_TOKEN="gldt-7RpJWMxPR42n1G14cvvV"
REPO_URL="https://${GIT_USER}:${GIT_TOKEN}@gitlab.com/mariamadide.diallo.1/seahawks_monitoring.git"

cd /app || exit

git pull "$REPO_URL" main

echo "✅ Mise à jour terminée !"
