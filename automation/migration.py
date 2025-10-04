"""Script pour migrer des données CSV vers MongoDB."""

import os
import math
import pandas as pd
from pymongo import MongoClient, errors
from pathlib import Path
import json #Pour l'export JSON valide

# ==== Config ====
CSV_FILE = os.getenv('CSV_FILE', '/Users/axellerolain/Desktop/P5/projet-mongodb-healthcare/data/dataset_ready4Mongo.csv')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:example@localhost:27017/?authSource=admin')
DB_NAME = os.getenv('DB_NAME', 'base_medicale')
COLLECTION = os.getenv('COLLECTION_NAME', 'patients')
DROP_BEFORE = os.getenv('DROP_BEFORE', 'true').lower() == 'true'
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
DATE_COLUMNS = [c.strip() for c in os.getenv('DATE_COLUMNS', 'Date_of_admission,Discharge_date').split(',') if c.strip()]  # Ajouté les dates par défaut pour les parser

print(f"[CFG] CSV_FILE={CSV_FILE}")
print(f"[CFG] MONGO_URI={MONGO_URI}")
print(f"[CFG] DB={DB_NAME} COL={COLLECTION} DROP_BEFORE={DROP_BEFORE}")
print(f"[CFG] BATCH_SIZE={BATCH_SIZE} DATE_COLUMNS={DATE_COLUMNS or 'none'}")

# ==== Lecture CSV ====
p = Path(CSV_FILE)
if not p.exists():
    print(f"[ERREUR] Fichier introuvable: {p}")
    raise SystemExit(1)

read_kwargs = {}
if DATE_COLUMNS:
    read_kwargs["parse_dates"] = DATE_COLUMNS

df = pd.read_csv(p, **read_kwargs)
print(f"[INFO] CSV OK: {len(df)} lignes, colonnes: {list(df.columns)}")

# Exploration légère (puisque nettoyé, juste pour info)
print("[EXPLORATION] Nombre de lignes : ", len(df))
print("[EXPLORATION] Colonnes : ", list(df.columns))
print("[EXPLORATION] Types de données : \n", df.dtypes)

# Sécurité Record_id (on garde, même si nettoyé, pour être sûre)
if 'Record_id' not in df.columns:
    print("[ERREUR] Colonne 'Record_id' manquante.")
    raise SystemExit(1)
if not df['Record_id'].is_unique:
    dup = df['Record_id'].duplicated(keep=False).sum()
    print(f"[ERREUR] Record_id non unique ({dup} doublons).")
    raise SystemExit(1)

# NaN -> None et _id
df = df.where(pd.notnull(df), None)
df['_id'] = df['Record_id']

# ==== Connexion Mongo ====
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    client.admin.command('ping')
    db = client[DB_NAME]
    col = db[COLLECTION]
    print("[INFO] Connexion Mongo OK.")
except Exception as e:
    print(f"[ERREUR] Connexion Mongo: {e}")
    raise SystemExit(1)

# --- 1) DROP d'abord ---
if DROP_BEFORE:
    col.drop()
    print("[INFO] Collection vidée.")

# --- 2) Index APRÈS le drop (et seulement si colonnes présentes) ---
try:
    if 'Record_id' in df.columns:
        col.create_index('Record_id', unique=True)
    if 'Date_of_admission' in df.columns:
        col.create_index('Date_of_admission')
    print("[INFO] Index créés.")
except Exception as e:
    print(f"[WARN] Création d'index: {e}")

docs = df.to_dict('records')
total = len(docs)
print(f"[INFO] {total} documents à insérer.")

# ==== Insertion par lots ====
inserted = 0
errors_total = 0
batches = math.ceil(total / BATCH_SIZE)

for i in range(batches):
    chunk = docs[i*BATCH_SIZE : min((i+1)*BATCH_SIZE, total)]
    try:
        res = col.insert_many(chunk, ordered=False)
        inserted += len(res.inserted_ids)
        print(f"[INFO] Batch {i+1}/{batches}: {len(res.inserted_ids)} insérés (cumul={inserted}).")
    except errors.BulkWriteError as bwe:
        we = bwe.details.get('writeErrors', [])
        dup_errors = sum(1 for e in we if e.get('code') == 11000)
        other = len(we) - dup_errors
        ok = len(chunk) - len(we)
        inserted += max(ok, 0)
        errors_total += len(we)
        print(f"[WARN] Batch {i+1}/{batches}: {ok} ok, {dup_errors} doublons, {other} autres erreurs.")
    except Exception as e:
        print(f"[ERREUR] Batch {i+1}/{batches}: {e}")
        raise SystemExit(1)

mongo_count = col.count_documents({})
print(f"[CHECK] CSV={total} | Mongo={mongo_count} | Insérés={inserted} | Erreurs={errors_total}")

# Test intégrité après (simple comparaison)
if mongo_count == total:
    print("[TEST] Intégrité OK : Nombre de documents identique.")
else:
    print("[TEST] Problème : Différence de", abs(mongo_count - total), "documents.")

# Exemple de test sur un champ (vérifie un document au hasard)
sample_doc = col.find_one()
if sample_doc:
    print("[TEST] Exemple de document : ", sample_doc)
    if isinstance(sample_doc.get('Age'), int):
        print("[TEST] Type 'Age' OK (nombre).")
    else:
        print("[TEST] Type 'Age' KO (pas un nombre).")

# --- 3) Export JSON valide (5 docs) ---
export_file = 'export_test.json'
with open(export_file, 'w', encoding='utf-8') as f:
    for doc in col.find().limit(5):
        f.write(json.dumps(doc, default=str, ensure_ascii=False) + '\n')
print("[INFO] Export test dans", export_file)
print("✅ Migration terminée." if mongo_count >= total - errors_total else "⚠️ Divergences, voir logs.")
client.close()