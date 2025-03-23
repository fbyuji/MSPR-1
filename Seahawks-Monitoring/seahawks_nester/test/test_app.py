import pytest
from app import app

@pytest.fixture
def client():
    """Créer un client de test pour Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Vérifier si la page d'accueil charge bien."""
    response = client.get("/")
    assert response.status_code == 200

def test_api_scans(client):
    """Tester si l'API retourne bien des scans."""
    response = client.get("/api/scans")
    assert response.status_code == 200

def test_api_sonde_not_found(client):
    """Tester la récupération d'une sonde qui n'existe pas."""
    response = client.get("/api/sondes/999")  
    assert response.status_code == 404  
