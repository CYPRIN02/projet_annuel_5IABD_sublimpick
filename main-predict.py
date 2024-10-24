import pandas as pd
from google.cloud import storage
from tensorflow import keras
import io
import time
import numpy as np
from fastapi import FastAPI, UploadFile, File
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
import os
import nltk
from nltk.corpus import stopwords
from rake_nltk import Rake
from datetime import datetime


os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

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

# Charger le tokenizer (ceci est un exemple ; ajustez pour charger le vrai tokenizer)
tokenizer = Tokenizer()  # Assurez-vous de charger le tokenizer correspondant au modèle

# Fonction de prédiction
def predict(text, include_neutral=True):
    maxlen = 100
    start_at = time.time()

    # Tokenize le texte
    x_test = pad_sequences(tokenizer.texts_to_sequences([text]), maxlen=maxlen)
    
    # Prédire
    score = model.predict([x_test])[0]

    # Décoder le sentiment
    if include_neutral:        
        label_idx = np.argmax(score)
        label = ["NEGATIVE", "NEUTRAL", "POSITIVE"][label_idx]
    else:
        label = "NEGATIVE" if score[0] > 0.5 else "POSITIVE"

    return {
        "label": label, 
        "score": float(score[label_idx]),
        "elapsed_time": time.time() - start_at
    }

# Fonction pour télécharger un fichier CSV depuis GCS
def download_csv_from_gcs(bucket_name, file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    csv_data = blob.download_as_text()
    return csv_data

nltk.download('stopwords')
nltk.download('punkt_tab')
stopwords = set(stopwords.words('english'))

def extract_keywords(text):
    r = Rake(stopwords=stopwords)  # Uses stopwords for english from NLTK, and all puntuation characters.
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()  # To get keyword phrases ranked highest to lowest.


# Endpoint local pour tester les prédictions sur un fichier CSV
@app.post("/predict_from_csv/")
async def predict_from_csv(file: UploadFile = File(...)):
    try:

        # Lire le contenu du fichier chargé
        csv_data = await file.read()

        # Lire le CSV avec pandas
        df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')), sep=',')
        
        # Ensure that the DataFrame contains the 'review_thoughts' column
        if 'review_thoughts' not in df.columns:
            raise ValueError("The column 'review_thoughts' is missing from the CSV file!")

        # Create lists to store predictions
        predictions = []
        scores = []
        times = []
        
        # Iterate over each row and predict sentiment
        for index, row in df.iterrows():
            text = row['review_thoughts']
            pred = predict(text)
            predictions.append(pred['label'])
            scores.append(pred['score'])
            times.append(pred['elapsed_time'])

        # Add predictions back to the DataFrame
        df['predicted_sentiment'] = predictions
        df['keywords'] = df['review_thoughts'].apply(extract_keywords)
        
        # Sauvegarder les prédictions dans un bucket GCS
        output_bucket_name = "sublime_bucket_2024"
        client = storage.Client()
        bucket = client.bucket(output_bucket_name)
        output_blob = bucket.blob(f"scrapping/10/prediction/predictions_{datetime.now().strftime('%Y-%m-%d')}.csv")
        output_blob.upload_from_string(df.to_csv(index=False), content_type="text/csv")
        return {"status": "success", "message": f"Prédictions enregistrées dans {output_bucket_name}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

