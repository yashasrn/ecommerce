import os
import sys
import unittest

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


class BackendAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_check(self):
        """Test that the /health endpoint returns 200 OK and healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data.get("status"), "healthy")
        self.assertIn("timestamp", json_data)

    def test_signup_missing_fields(self):
        """Test signup validation returns 400 when required fields are missing."""
        response = self.client.post("/signup", json={})
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertIn("error", json_data)


if __name__ == "__main__":
    unittest.main()
