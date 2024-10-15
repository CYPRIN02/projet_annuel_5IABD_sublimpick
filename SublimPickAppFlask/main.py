from backend.app import app  # Importer l'application Flask depuis backend/app.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
