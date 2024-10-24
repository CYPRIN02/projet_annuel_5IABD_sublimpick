# projet_annuel_5IABD_sublimpick
projet octobre 2024

# Sublime Pick Application

## Description

Sublime Pick est une application web développée en **Python** avec **Flask** et déployée sur **Google App Engine**. Elle permet de rechercher des produits, d'afficher leurs détails et d'analyser les avis utilisateurs à l'aide de graphiques générés à partir des données d'avis clients stockées dans **Google Cloud Storage**. 

L'application charge une fois un fichier de données JSON contenant les avis produits et utilise cette base pour fournir des résultats de recherche rapide et des visualisations sous forme de graphiques.

## Fonctionnalités

- **Recherche de Produits** : Les utilisateurs peuvent rechercher des produits par nom, et l'application retourne une liste des résultats correspondants.
- **Détails des Produits** : Pour chaque produit, une page détaillée affiche les avis et des graphiques analytiques comme la distribution des notes, l'analyse de sentiment, la tendance des avis dans le temps, et les mots-clés les plus courants.
- **Visualisation de Données** : Utilisation de **Matplotlib** pour générer des graphiques d'analyse des avis utilisateurs.

## Technologies Utilisées

- **Backend** : Flask (Python)
- **Frontend** : HTML, CSS (gérés via des templates Flask)
- **Stockage** : Google Cloud Storage pour le stockage des données JSON contenant les avis produits.
- **Déploiement** : Google App Engine
- **Visualisation** : Matplotlib pour les graphiques

## Configuration

### Prérequis

- Python 3.10 ou supérieur
- Google Cloud SDK installé
- Google Cloud Storage configuré avec un bucket contenant le fichier `merged_product_reviews.json`

### Variables d'environnement

Les variables suivantes doivent être définies pour que l'application fonctionne correctement :

- `BUCKET_NAME` : Nom du bucket dans Google Cloud Storage (par défaut : `sublime_bucket_bis`).
- `STORAGE_PATH` : Chemin vers le fichier des avis produits dans le bucket (par défaut : `10/reviews/merged_product_reviews.json`).

### Installation et Exécution

1. **Cloner le repository** :
    ```bash
    git clone https://github.com/votre-repository.git
    cd SublimePickAppFlask
    ```

2. **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

3. **Configurer les variables d'environnement** :
    Vous pouvez utiliser un fichier `.env` pour configurer les variables d'environnement ou définir les valeurs dans votre environnement système.

4. **Exécuter l'application en local** :
    ```bash
    gunicorn -b 127.0.0.1:8080 main:app --timeout 120
    ```

5. **Déployer sur Google App Engine** :
    Pour déployer l'application sur App Engine, utilisez la commande suivante :
    ```bash
    gcloud app deploy
    ```

### Utilisation

- Accéder à la page d'accueil : `http://127.0.0.1:8080/`
- Rechercher des produits par nom sur la page de recherche.
- Consulter les détails d'un produit en cliquant sur son nom.


### Contributeurs

- **PRINCY**
- **MICKAEL**
- **WILLY**

### Licence

Ce projet est sous licence [MIT](LICENSE).

