import os
import sys
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'helpers'))

from backend.app import app  # Importer l'application Flask depuis backend/app.py
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
