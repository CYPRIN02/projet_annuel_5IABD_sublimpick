import os
import sys


backend_path = os.path.join(os.path.dirname(__file__), 'backend')
print(f"Ajout du chemin backend au PYTHONPATH: {backend_path}")
sys.path.append(backend_path)


frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
print(f"Ajout du chemin frontend au PYTHONPATH: {frontend_path}")
sys.path.append(frontend_path)

try:
    from backend.app import app  
    print("Importation de 'backend.app' réussie")

except ImportError as e:
    print(f"Erreur d'importation dans 'backend.app': {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Lancement de l'application Flask sur le port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
