# 🏥 Projet Migration Données Médicales vers MongoDB
## projet-mongodb-healthcare

Ce projet a pour but de migrer un dataset médical CSV vers MongoDB.

# 🏥 Projet Migration Données Médicales vers MongoDB
## projet-mongodb-healthcare

Ce projet migre un dataset médical (CSV) vers MongoDB. Il utilise Docker pour tout lancer facilement.

La migration :
- Lit et transforme les données (dates, types...).
- Ajoute par petits groupes (batches).
- Vérifie tout avec 3 tests unitaires.

# 📦 Dataset

Le dataset nettoyé **n’est pas dans le repo** (trop lourd).  

Télécharge-le depuis la Release GitHub :  
🔗 [dataset_ready4Mongo.csv](https://github.com/Barolax/projet-mongodb-healthcare/releases/download/v1.0/dataset_ready4Mongo.csv)

Mets-le dans `./data/dataset_ready4Mongo.csv`.

# ⚙️ Architecture du projet
projet-mongodb-healthcare/
├── automation/               # Pour le script de migration
│   ├── Dockerfile            # Recette pour la boîte Python
│   ├── migration.py         # Script qui migre les données
│   └── requirements.txt      # Outils Python nécessaires
├── schema_base/              # Schéma de la base (JSON)
│   └── schema-base_medicale-patients.json
├── tests/                    # Tests et export démo
│   ├── test_migration.py    # Les 3 tests unitaires
│   └── export_test.json     # Export démo (généré)
├── docker-compose.yml        # Orchestre tout (Mongo, migration, tests)
├── Makefile                  # Commandes rapides pour démo
└── README.md                 # Ce guide

# 🚀 Lancement

Depuis la racine :

```bash
docker compose up -d --build

Check des logs : 
docker compose logs -f migrator  # Pour la migration
docker compose logs -f tester    # Pour les tests

Pour arrêter et nettoyer :
docker compose down -v

🔄 Ce qui se passe pendant la migration
Le "migrator" exécute migration.py :

Lit le CSV avec Pandas (convertit dates, remplace vides par None).
Vérifie Record_id unique.
Crée _id = Record_id.
Se connecte à Mongo (URI avec root/example).
Vide la collection si DROP_BEFORE=true.
Crée index sur Record_id (unique) et Date_of_admission.
Insère par lots de 1000 (affiche stats).
Vérifie le nombre total.
Affiche un exemple de doc.
Exporte 5 docs en JSON (export_test.json).

✅ Tests unitaires
Le "tester" exécute test_migration.py :

Vérifie que la collection n'est pas vide.
Vérifie les champs obligatoires (ex: Medical_condition, Date_of_admission).
Vérifie le nombre exact (54966 docs).

Lancement manuel :
docker compose run --rm tester python -m unittest -v

🔒 Authentification MongoDB
Utilisateur : root
Mot de passe : example
URI pour connecter (ex: avec Compass) :
mongodb://root:example@localhost:27017/?authSource=admin

📊 Exemple de document
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

./data : Pour le CSV source.
mongo-data : Stockage persistant de MongoDB (les données restent même si c'est arrêté).

🛠️ Démo live avec Makefile
Pour une démo rapide:

make up : Lance Mongo seul.
make migrate : Construit et migre les données.
make test : Lance les tests.
make logs : Montre les logs de Mongo.
make down : Arrête et nettoie tout.

Note sur les ports
Dans docker-compose.yml, les ports sont commentés (#) pour sécurité. 
Retrait du # devant ports: - "27017:27017" si on veut connecter Compass 

