import unittest
from pymongo import MongoClient

MONGO_URI = "mongodb://root:example@mongo:27017/?authSource=admin"
DB_NAME = "base_medicale"
COLL_NAME = "patients"

class TestMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = MongoClient(MONGO_URI)
        cls.collection = cls.client[DB_NAME][COLL_NAME]

    def test_has_documents(self):
        self.assertGreater(self.collection.estimated_document_count(), 0, "La collection ne doit pas être vide")

    def test_sample_has_required_fields(self):
        doc = self.collection.find_one({}, {"_id": 0, "Medical_condition": 1, "Date_of_admission": 1, "Discharge_date": 1})
        self.assertIsNotNone(doc, "Aucun document trouvé")
        self.assertIn("Medical_condition", doc, "Le champ Medical_condition doit exister")

    def test_exact_count(self):
        self.assertEqual(self.collection.count_documents({}), 54966, "Le nombre de documents doit être 54966")

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
