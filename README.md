# 🏥 Projet Migration Données Médicales vers MongoDB
## projet-mongodb-healthcare

Ce projet a pour but de migrer un dataset médical CSV vers MongoDB.

La migration s’assure que :

Les données sont correctement lues et transformées (dates, identifiants, types numériques).

La base MongoDB est alimentée par lots. 

3 tests unitaires garantissent l’intégrité de la migration.

# 📦 Dataset

Le dataset nettoyé **n’est pas versionné dans le repo** (pour éviter d’alourdir l’historique).  

➡️ Téléchargement direct depuis la Release GitHub :

🔗 [Télécharger dataset_ready4Mongo.csv](https://github.com/Barolax/projet-mongodb-healthcare/releases/download/v1.0/dataset_ready4Mongo.csv)

Placez le fichier dans ./data sous le nom : dataset_ready4Mongo.csv

⚙️ Architecture du projet
projet-mongodb-healthcare/
├── automation/               # Service migrateur
│   ├── Dockerfile
│   ├── migration.py
│   ├── requirements.txt
│   └── docker-compose.yml    # Orchestration des services (mongo, migrator, tester)
├── schema_base/              # Schéma JSON MongoDB
│   └── schema-base_medicale-patients.json
├── tests/                    # Tests unitaires & export (démo)
│   ├── test_migration.py
│   └── export_test.json
└── README.md

🚀 Lancement de la migration

Depuis la racine du projet :

docker compose up -d --build


Vérifiez les logs :

docker compose logs -f migrator
docker compose logs -f tester

🔄 Que se passe-t-il pendant la migration ?

Le service migrator exécute migration.py, qui suit ce processus :

Lecture du CSV avec Pandas

Les colonnes de type date (Date_of_admission, Discharge_date) sont converties en objets datetime.

Les NaN sont transformés en None pour être compatibles avec le format BSON.

Préparation des données

Vérification que Record_id est bien unique. (PK) 

Transformation de certains champs en types corrects (int, double, date).

Création d’un champ _id = Record_id pour l’unicité dans Mongo.

Connexion à MongoDB

Authentification via l’URI mongodb://root:example@mongo:27017/?authSource=admin.

Sélection de la base base_medicale et de la collection patients.

Nettoyage et indexation

Si DROP_BEFORE=true, la collection est vidée.

Création d’index sur Record_id (unicité) et Date_of_admission. 

Insertion par lots (batch) 

Découpage des documents par blocs de 1000 pour faciliter ingestion. 

Affichage des statistiques (ok, doublons, erreurs).

Contrôle d’intégrité

Check le nombre de documents insérés = taille du CSV.

Affiche un échantillon de document pour contrôle. 

Export d’un fichier export_test.json contenant 5 documents en JSON depuis MongoCompass

✅ Tests unitaires

Le service tester exécute test_migration.py et vérifie que :

La collection n’est pas vide.

Les champs obligatoires (Medical_condition, Date_of_admission, etc.) existent.

Le nombre total de documents insérés correspond à celui du CSV. (nbre : 54966)

Exécution manuelle :

docker compose run --rm tester python -m unittest -v

🔒 Authentification MongoDB

Utilisateur : root

Mot de passe : example

URI :

mongodb://root:example@localhost:27017/?authSource=admin 

📊 Exemple de document inséré
{
  "_id": 1,
  "Record_id": 1,
  "Prenom": "Bobby",
  "Nom": "Jackson",
  "Age": 30,
  "Gender": "Male",
  "Blood_type": "B-",
  "Medical_condition": "Cancer",
  "Date_of_admission": "2024-01-31T00:00:00.000Z",
  "Doctor": "Matthew Smith",
  "Hospital": "Sons and Miller",
  "Insurance_provider": "Blue Cross",
  "Billing_amount": 18856.28,
  "Room_number": 328,
  "Admission_type": "Urgent",
  "Discharge_date": "2024-02-02T00:00:00.000Z",
  "Medication": "Paracetamol",
  "Test_results": "Normal"
}

📦 Volumes

./data → CSV source.

mongo-data → stockage persistant de MongoDB.
