import csv
import os
from typing import List, Dict, Any

def load_csv(path: str) -> List[Dict]:
    """Charge un CSV et renvoie une liste de dict."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV introuvable : {path}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def validate_headers(rows: List[Dict[str, Any]], required: List[str]) -> None:
    """Vérifie que le CSV contient bien toutes les colonnes attendues."""
    if not rows:
        raise ValueError("CSV vide")
    first = rows[0]
    missing = [col for col in required if col not in first]
    if missing:
        raise ValueError(f"Colonnes manquantes : {missing}")

def validate_content(
    rows: List[Dict[str, Any]],
    strict_id: bool = False,
) -> None:
    """
    Valide quelques règles simples.
    - si on trouve une colonne d'identifiant connue -> on la contrôle
    - si on ne la trouve pas :
        - en mode strict -> on lève une erreur
        - sinon -> on affiche un warning mais on laisse passer
    """
    if not rows:
        raise ValueError("CSV vide")

    first_row = rows[0]
    cols = set(first_row.keys())

    possible_id_cols = ["id", "ID", "Id", "patient_id", "PatientID", "patientId"]

    id_col = None
    for c in possible_id_cols:
        if c in cols:
            id_col = c
            break

    if id_col is None:
        if strict_id:
            # mode très strict (celui qui t'a fait planter)
            raise ValueError("Aucune colonne d'identifiant trouvée dans le CSV")
        else:
            # on laisse passer mais on informe
            print("⚠️ Avertissement: aucune colonne d'identifiant standard trouvée, validation ID ignorée.")
            return

    # si on est là, on a trouvé une colonne d'id -> on la vérifie
    for i, r in enumerate(rows):
        if not r.get(id_col):
            raise ValueError(f"Ligne {i}: '{id_col}' est obligatoire")


def format_row(row: Dict) -> Dict:
    """Ici tu fais tes petits nettoyages : trim, types, etc."""
    # exemple simple
    return {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}

def format_batch(rows: List[Dict]) -> List[Dict]:
    """Applique format_row à tout le monde."""
    return [format_row(r) for r in rows]

def make_batches(rows: List[Dict], batch_size: int = 1000) -> List[List[Dict]]:
    """Découpe en lots pour insérer en batch dans Mongo."""
    return [rows[i:i+batch_size] for i in range(0, len(rows), batch_size)]
