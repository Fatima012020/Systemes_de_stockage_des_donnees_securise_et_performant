import os
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app import load_csv, validate_headers, validate_content, format_batch, make_batches  # 👈 on réutilise

CSV_SOURCE = os.getenv("CSV_SOURCE", "/seed/healthcare_dataset.csv")
CSV_PATH = os.getenv("CSV_PATH", "/migration_data/healthcare_dataset.csv")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "donnees_medicales")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "patients")

# 0. copier si besoin
import shutil
if not os.path.exists(CSV_PATH) and os.path.exists(CSV_SOURCE):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    shutil.copyfile(CSV_SOURCE, CSV_PATH)

rows = load_csv(CSV_PATH)

# 1. valider la donnée 
required_cols = ["Name", "Age", "Gender"]  # 👉 mets les colonnes de TON dataset
validate_headers(rows, required_cols)

# 2. valider le contenu
validate_content(rows, strict_id=False)

# 3. formatter
rows = format_batch(rows)

# 4. connexion Mongo
client = None
for _ in range(10):
    try:
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, serverSelectionTimeoutMS=2000)
        client.server_info()
        break
    except ServerSelectionTimeoutError:
        print("Mongo pas prêt, j'attends...")
        time.sleep(2)

db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# rendre idempotent
collection.delete_many({})

# 5. insertion en batch
batches = make_batches(rows, batch_size=2000)
inserted = 0
for batch in batches:
    collection.insert_many(batch)
    inserted += len(batch)
    print(f"{inserted} insérés...")

print(f"✅ Migration terminée : {inserted} documents.")
client.close()
