import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from google.cloud import storage
from fastapi import FastAPI, UploadFile, File
from io import StringIO
from tensorflow import keras

# Initialisation de l'application FastAPI
app = FastAPI()

# Chemin local temporaire pour stocker le modèle téléchargé depuis GCS
LOCAL_MODEL_PATH = "/app/modele/sentiment_analysis_model.h5"

# Fonction pour télécharger le modèle depuis GCS vers le chemin local
def download_model_from_gcs(bucket_name, source_blob_name, destination_file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Modèle téléchargé depuis gs://{bucket_name}/{source_blob_name} vers {destination_file_name}")

# Télécharger et charger le modèle (cette partie est exécutée une fois pour optimiser les performances)
bucket_name = 'sublime_bucket_2024'
model_path_in_gcs = 'modele/sentiment_analysis_model.h5'

# Télécharger le modèle depuis GCS
download_model_from_gcs(bucket_name, model_path_in_gcs, LOCAL_MODEL_PATH)


# Charger le modèle téléchargé dans TensorFlow
model = keras.models.load_model(LOCAL_MODEL_PATH)

# Fonction pour télécharger un fichier CSV depuis GCS
def download_csv_from_gcs(bucket_name, file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    csv_data = blob.download_as_text()
    return csv_data

# Fonction de prétraitement des données
def load_and_preprocess(data):
    # Rename columns
    data = data.rename(columns={'review_thoughts': 'text', 'review_stars': 'sentiment'})

    # Replace NaNs with empty strings
    data['text'] = data['text'].fillna('')

    # Preprocess the text data
    data['text'] = data['text'].apply(lambda x: x.lower())

    # Convert ratings into sentiment
    data['sentiment'] = data['sentiment'].apply(lambda x: 'positive' if x > 3 else ('neutral' if x == 3 else 'negative'))

    return data

# Route pour déclencher l'entraînement du modèle
@app.post("/train/")
async def train_model(file: UploadFile = File(...)):
    try:
        
        # Télécharger le fichier CSV depuis GCS
        csv_data = await file.read()

        # Convertir le texte CSV en DataFrame
        df = pd.read_csv(StringIO(csv_data.decode('utf-8')), sep=',')

        # Prétraiter les données
        data = load_and_preprocess(df)

        # Tokenization
        tokenizer = Tokenizer(num_words=5000, split=" ")
        tokenizer.fit_on_texts(data['text'].values)
        
        # Convertir le texte en séquences et padding
        X = tokenizer.texts_to_sequences(data['text'].values)
        X = pad_sequences(X, maxlen=100)

        # Encoder les étiquettes
        le = LabelEncoder()
        data['sentiment'] = le.fit_transform(data['sentiment'])
        y = to_categorical(data['sentiment'].values)

        # Split des données en train et test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entraîner le modèle
        model.fit(X_train, y_train, epochs=5, validation_data=(X_test, y_test))

        # Sauvegarder le modèle dans GCS après l'entraînement
        model.save(LOCAL_MODEL_PATH)

        # Uploader le modèle sur GCS
        bucket_name = "sublime_bucket_2024"
        blob = storage.Client().bucket(bucket_name).blob('modele/sentiment_analysis_model.h5')
        blob.upload_from_filename(LOCAL_MODEL_PATH)

        return {"status": "Model trained and saved successfully"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
