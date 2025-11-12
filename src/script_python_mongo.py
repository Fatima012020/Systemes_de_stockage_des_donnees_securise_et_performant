import os
import time
import shutil
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app import load_csv, validate_headers, validate_content, format_batch, make_batches

# --- ENV ---
CSV_SOURCE = os.getenv("CSV_SOURCE", "/seed/healthcare_dataset.csv")
CSV_PATH = os.getenv("CSV_PATH", "/migration_data/healthcare_dataset.csv")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "donnees_medicales")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "patients")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# --- Copier le CSV dans le volume s'il n'y est pas encore ---
if not os.path.exists(CSV_PATH) and os.path.exists(CSV_SOURCE):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    shutil.copyfile(CSV_SOURCE, CSV_PATH)
print(f"CSV utilisé: {CSV_PATH} (existe={os.path.exists(CSV_PATH)})")

# --- Charger + valider + formatter ---
rows = load_csv(CSV_PATH)

# ⚠️ Mets ici les colonnes RÉELLEMENT présentes dans ton fichier
required_cols = ["Name", "Age", "Gender"]
validate_headers(rows, required_cols)
validate_content(rows, strict_id=False)
rows = format_batch(rows)

# --- Construire l'URI AUTH dès le départ ---
if not (MONGO_USER and MONGO_PASSWORD):
    raise RuntimeError("Variables MONGO_USER / MONGO_PASSWORD manquantes dans l'environnement")

mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_DB}"
print(f"Connexion Mongo: mongodb://<user>:***@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_DB}")

# --- Connexion (attente jusqu'à 60s) ---
client = None
for _ in range(30):
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.server_info()
        break
    except ServerSelectionTimeoutError:
        print("Mongo pas prêt, j'attends...")
        time.sleep(2)
else:
    raise RuntimeError("Mongo n'a pas démarré à temps")

db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# --- Idempotence: vider puis insérer ---
collection.delete_many({})
batches = make_batches(rows, batch_size=2000)
inserted = 0
for batch in batches:
    collection.insert_many(batch)
    inserted += len(batch)
    print(f"{inserted} insérés...")

print(f"✅ Migration terminée : {inserted} documents.")
client.close()
