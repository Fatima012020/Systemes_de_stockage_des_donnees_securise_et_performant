🧠 Migration des données vers MongoDB via Docker
🎯 Objectif du projet

Ce projet vise à automatiser la migration d’un dataset CSV vers MongoDB, en utilisant une architecture conteneurisée basée sur Docker Compose.

Il démontre :

✅ une migration entre conteneurs fonctionnelle,

✅ une validation stricte des données avant insertion,

✅ des tests unitaires prouvant la fiabilité,

✅ une authentification MongoDB avec gestion des rôles,

✅ et une documentation complète pour rejouer l’expérience.

🏗️ Architecture du projet
Systemes_de_stockage_des_donnees_securise_et_performant/
│
├── data/
│   └── healthcare_dataset.csv             # Dataset source
│
├── mongo-init/
│   └── users_and_roles.js                # Script d'initialisation MongoDB (création des utilisateurs)
│
├── src/                                   # Code source principal
│   ├── app.py                             # Fonctions utilitaires : validation, formatage, batching
│   ├── script_python_mongo.py             # Script principal de migration CSV → MongoDB
│   ├── test_app.py                        # Tests unitaires (pytest)
│   ├── .gitignore                         # Fichiers et dossiers à exclure du dépôt Git
│   └── .env.example                       # Exemple de configuration d'environnement (.env modèle)
│
├── Dockerfile                             # Image du conteneur migrator
├── docker-compose.yml                     # Orchestration des services (Mongo + migrator)
├── requirements.txt                       # Dépendances Python
├── .env                                   # Variables d'environnement réelles (non versionné)
└── README.md                              # Documentation complète du projet


⚙️ 1. Installation et lancement des conteneurs

1️⃣ Pré-requis

Docker Desktop installé et lancé

Fichier .env contenant :
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=change-me-root!
MONGO_APP_DB=donnees_medicales
MONGO_APPUSER=appuser
MONGO_APPUSER_PWD=change-me-app!


2️⃣ Lancer l’environnement complet

docker compose up --build
👉 Cela :
crée MongoDB avec authentification,

exécute le script d’initialisation des utilisateurs, et prépare le conteneur migrator.

3️⃣ Vérifier l’état des conteneurs docker compose ps

Tu devrais voir :
NAME      STATUS             PORTS
mongo     Up (healthy)       0.0.0.0:27017->27017/tcp
migrator  Exit 0

📦 2. Lancer et vérifier la migration
Exécuter la migration :
docker compose run --rm migrator

Compter les documents insérés :
docker compose exec mongo mongosh \ -u appuser -p "change-me-app!" \
  --authenticationDatabase donnees_medicales \
  --eval "db.getSiblingDB('donnees_medicales').patients.countDocuments()"
👉 Si le nombre correspond à ton CSV (ex. 55500), la migration est réussie ✅

🔐 3. Authentification et rôles d’accès

Les utilisateurs sont créés automatiquement via le fichier mongo-init/users_and_roles.js.
| Utilisateur                | Base d’auth         | Rôle attribué | Droits                       |
| -------------------------- | ------------------- | ------------- | ---------------------------- |
| **root**                   | `admin`             | `root`        | accès total                  |
| **appuser**                | `donnees_medicales` | `readWrite`   | migration, lecture, écriture |
| *(optionnel)* **readonly** | `donnees_medicales` | `read`        | lecture seule                |

Test des accès :
# Lecture OK
docker compose exec mongo mongosh -u appuser -p "change-me-app!" --authenticationDatabase donnees_medicales --eval "db.getSiblingDB('donnees_medicales').patients.findOne()"

# Tentative d'insertion (OK seulement pour appuser)
docker compose exec mongo mongosh -u appuser -p "change-me-app!" --authenticationDatabase donnees_medicales --eval "db.getSiblingDB('donnees_medicales').patients.insertOne({test:1})"


🧩 4. Structure du code et refactorisation
Le code a été refactoré pour être modulaire et testable :
| Fichier / Fonction                 | Description                                                        |
| ---------------------------------- | ------------------------------------------------------------------ |
| **app.py**                         | Fonctions pures (lecture, validation, formatage, batch)            |
| **script_python_mongo.py**         | Migration complète CSV → MongoDB (connexion, nettoyage, insertion) |
| **test_app.py**                    | Tests unitaires (pytest)                                           |
| **mongo-init/001-create-users.js** | Création automatique des utilisateurs MongoDB                      |

Le script principal appelle ces fonctions dans cet ordre :

✅ Chargement du CSV

✅ Validation des colonnes et du contenu

✅ Nettoyage et batch

✅ Insertion dans MongoDB

🧪 5. Tests unitaires et de validation

Les tests sont écrits avec pytest et exécutés dans le conteneur migrator.

✅ Lancer les tests

Depuis ton dossier de projet :
docker compose run --rm migrator python -m pip install pytest
docker compose run --rm migrator pytest -v

💡 Résultat attendu :
collected 6 items                                                                      
test_app.py::test_format_row_trim PASSED                                        
test_app.py::test_make_batches_size PASSED                                       [ 33%] 
test_app.py::test_validate_headers_ok PASSED                                     [ 50%] 
test_app.py::test_validate_headers_missing PASSED                                [ 66%] 
test_app.py::test_validate_content_ok PASSED                                     [ 83%] 
test_app.py::test_validate_content_id_manquant PASSED                            [100%] 

================================== 6 passed in 0.04s ===================================


Chaque test correspond à une fonctionnalité précise :

format_row_trim → vérifie le nettoyage des données.

make_batches_size → vérifie le découpage en lots.

validate_headers → vérifie la présence des colonnes attendues.

validate_content → vérifie qu’un identifiant et des valeurs valides sont présents.

🚨 6. Validation stricte des données

Le script vérifie que :

toutes les colonnes obligatoires sont présentes (ex. id, Age, Gender), aucune ligne ne viole les contraintes (ID manquant, âge vide, etc.).

Si une erreur est détectée :
ValueError: Colonnes manquantes : ['id', 'age', 'gender']

🧱 7. Volumes et persistance
| Volume                           | Rôle                                  |
| -------------------------------- | ------------------------------------- |
| **mongo_data**                   | Persiste la base MongoDB              |
| **migration_data** *(optionnel)* | Copie du CSV utilisée par le migrator |

Les données persistent après redémarrage de Docker :
docker volume ls

♻️ 8. Réinitialiser complètement

Pour tout supprimer (conteneurs + volumes) :
docker compose down -v
docker compose up -d --build
docker compose run --rm migrator

🧾 9. Vérifications globales (“tout va bien” ✅)

| Étape                | Commande                                    | Attendu                             |                                      |
| -------------------- | ------------------------------------------- | ----------------------------------- | ------------------------------------ |
| Conteneurs OK        | `docker compose ps`                         | mongo Up (healthy), migrator Exit 0 |                                      |
| Variables présentes  | `docker compose run --rm migrator env       | Select-String "MONGO_"`             | toutes les variables MONGO_ visibles |
| CSV trouvé           | `docker compose run --rm migrator ls /data` | `healthcare_dataset.csv` présent    |                                      |
| Données migrées      | `countDocuments()` > 0                      | Données insérées                    |                                      |
| Tests unitaires      | `pytest -v`                                 | 100 % PASS                          |                                      |
| Rejouer la migration | `docker compose run --rm migrator`          | même count (idempotence)            |                                      |
