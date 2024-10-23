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
    from backend.helpers.rating_distrubition_reviews import create_review_graphs
    from backend.helpers.sentiment_analysis_reviews import create_sentiment_graph
    from backend.helpers.trend_reviews_over_time import create_review_trend_graph
    from backend.helpers.keywords_top_reviews import create_keyword_graph
    print("Importation de 'helpers' réussie")
except ImportError as e:
    print(f"Erreur d'importation dans 'backend.app': {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Lancement de l'application Flask sur le port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
