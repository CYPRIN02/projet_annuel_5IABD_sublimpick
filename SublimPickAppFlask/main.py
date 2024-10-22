import os
import sys

# Ajout du chemin pour 'backend'
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
print(f"Ajout du chemin backend au PYTHONPATH: {backend_path}")
sys.path.append(backend_path)

# Ajout du chemin pour 'frontend'
frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
print(f"Ajout du chemin frontend au PYTHONPATH: {frontend_path}")
sys.path.append(frontend_path)

# Importation de l'application Flask depuis 'backend/app.py'
try:
    from backend.app import app  # Importer l'application Flask
    print("Importation de 'backend.app' réussie")
except ImportError as e:
    print(f"Erreur d'importation dans 'backend.app': {e}")

if __name__ == "__main__":
    print("Lancement de l'application Flask")
    app.run(host="0.0.0.0", port=8080, debug=False)
