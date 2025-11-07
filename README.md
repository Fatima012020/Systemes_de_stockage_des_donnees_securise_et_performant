🧠 Migration des données vers MongoDB via Docker
🎯 Objectif du projet

Ce projet vise à automatiser la migration d’un dataset CSV vers MongoDB, en utilisant une architecture conteneurisée basée sur Docker Compose.

Il démontre :

- une migration fonctionnelle entre conteneurs,

- une refactorisation claire du code Python,

- une validation stricte de la donnée avant insertion,

- des tests unitaires pour prouver la fiabilité du code,

- et une documentation complète pour rejouer l’expérience.

🏗️ Architecture du projet
Systemes_de_stockage_des_donnees_securise_et_performant/
│
├── data/
│   └── healthcare_dataset.csv
│
├── src/                          
│   ├── app.py
│   ├── script_python_mongo.py
│   ├── test_app.py
│
├── Dockerfile                    
├── requirements.txt              
├── docker-compose.yml
└── README.md

⚙️ 1. Installation et lancement des conteneurs

Avant de commencer, assure-toi que Docker Desktop est bien lancé sur Windows.
Place-toi dans le dossier du projet :
cd "C:\Users\adjab\Desktop\Formation\Systemes_de_stockage_des_donnees_securise_et_performant"

🧱 Lancer l’environnement complet
docker compose up --build
Cela construit et lance les conteneurs mongo et migrator.

Le script lit ton CSV, valide les données et insère tout dans MongoDB.

🔍 Vérifier les conteneurs actifs
docker compose ps

Tu devrais voir :
NAME        STATUS          PORTS
mongo       Up              0.0.0.0:27017->27017/tcp
migrator    Exit 0

📦 2. Vérifier que la migration fonctionne
📊 Compter les documents importés dans MongoDB
docker compose exec mongo mongosh --eval "db.getSiblingDB('donnees_medicales').patients.countDocuments()"

👉 Si c’est le cas, ta migration fonctionne parfaitement.
🧩 3. Structure du code et refactorisation

Le code a été refactoré pour être modulaire et testable :
| Fichier / Fonction         | Rôle                                                                 |
| -------------------------- | -------------------------------------------------------------------- |
| **app.py**                 | Contient les fonctions pures : lecture, validation, formatage, batch |
| **script_python_mongo.py** | Conteneur principal orchestrant la migration                         |
| **validate_headers()**     | Vérifie les colonnes obligatoires                                    |
| **validate_content()**     | Vérifie la qualité des données (id, âge, etc.)                       |
| **format_row()**           | Nettoie les valeurs (espaces, formats)                               |
| **make_batches()**         | Crée des lots d’insertion                                            |
| **format_batch()**         | Applique `format_row()` à tous les enregistrements                   |

Le script principal appelle ces fonctions dans cet ordre :

Chargement du CSV

Validation des colonnes et du contenu

Nettoyage et batch

Insertion dans MongoDB

🧪 4. Tests unitaires et de validation

Les tests sont écrits avec pytest et exécutés dans le conteneur migrator.

✅ Lancer les tests

Depuis ton dossier de projet :
docker compose run --rm migrator python -m pip install pytest
docker compose run --rm migrator pytest -v

💡 Résultat attendu :
test_app.py::test_format_row_trim PASSED
test_app.py::test_make_batches_size PASSED
test_app.py::test_validate_headers_ok PASSED
test_app.py::test_validate_content_ok PASSED
============================= 5 passed in 0.04s =============================

Chaque test correspond à une fonctionnalité précise :

format_row_trim → vérifie le nettoyage des données.

make_batches_size → vérifie le découpage en lots.

validate_headers → vérifie la présence des colonnes attendues.

validate_content → vérifie qu’un identifiant et des valeurs valides sont présents.

🚨 5. Validation stricte des données

Avant toute insertion, le script :

vérifie que le CSV contient les colonnes obligatoires (ex. patient_id, Age, Gender, etc.),

et que chaque ligne respecte des règles de base (ID non vide, âge positif, etc.).

🧭 Test manuel de validation

1. Crée une copie du fichier CSV :
copy .\data\healthcare_dataset.csv .\data\healthcare_dataset_bad.csv

2. Ouvre healthcare_dataset_bad.csv et supprime une colonne obligatoire (patient_id par ex.).

3. Modifie le docker-compose.yml pour pointer vers ce fichier :
environment:
  CSV_SOURCE: /seed/healthcare_dataset_bad.csv
4. Relance la migration :
docker compose run --rm migrator
🔴 Résultat attendu :
ValueError: Colonnes manquantes : ['patient_id']
Aucune donnée n’est insérée → la validation fonctionne ✅
♻️ 6. Repartir à zéro

Pour tout supprimer (conteneurs + volumes) :
docker compose down -v
Puis relancer :
docker compose up --build

📘 7. Commandes principales (résumé)
| Étape                 | Commande PowerShell                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Lancer les conteneurs | `docker compose up --build`                                                                                       |
| Vérifier MongoDB      | `docker compose exec mongo mongosh --eval "db.getSiblingDB('donnees_medicales').patients.countDocuments()"`       |
| Lancer les tests      | `docker compose run --rm migrator python -m pip install pytest` puis `docker compose run --rm migrator pytest -v` |
| Nettoyer tout         | `docker compose down -v`                                                                                          |
💡 8. Conseils pour la soutenance

👉 Montre en direct ces 3 choses :

docker compose up --build → migration OK

pytest -v → tous les tests PASS

ValueError si CSV erroné → validation intégrée