import unittest
from server import app
import os
import os

class TestServer(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Let's build a flight delay prediction api!")

    def test_predict(self):
        response = self.app.get('/predict?airport_id=123&day_of_week=1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('model_prediction', data)
        self.assertIn('confidence_percent', data)
        self.assertIn('delayed_percent', data)
        self.assertIn('interpretation', data)

    def test_airports(self):
        response = self.app.get('/airports')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('airports', data)
        airports = data['airports']
        self.assertIsInstance(airports, list)
        self.assertTrue(all(isinstance(airport, dict) for airport in airports))
        self.assertTrue(all('id' in airport and 'name' in airport for airport in airports))
        def test_predict_missing_params(self):
            response = self.app.get('/predict')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertIn("Missing required query parameters", data['error'])

        def test_predict_invalid_params(self):
            response = self.app.get('/predict?airport_id=abc&day_of_week=xyz')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertTrue("invalid literal" in data['error'] or "invalid" in data['error'].lower())

        def test_airports_file_not_found(self):
            # Temporarily rename the file if it exists
            if os.path.exists('origin_airport.csv'):
                os.rename('origin_airport.csv', 'origin_airport.csv.bak')
                renamed = True
            else:
                renamed = False
            try:
                response = self.app.get('/airports')
                self.assertEqual(response.status_code, 400)
                data = response.get_json()
                self.assertIn('error', data)
                self.assertTrue('No such file' in data['error'] or 'No such file or directory' in data['error'])
            finally:
                if renamed:
                    os.rename('origin_airport.csv.bak', 'origin_airport.csv')

        def test_airports_invalid_format(self):
            test_filename = 'origin_airport.csv'
            backup = None
            if os.path.exists(test_filename):
                with open(test_filename, 'r') as f:
                    backup = f.read()
            try:
                with open(test_filename, 'w') as f:
                    f.write("id,name\ninvalid_line_without_comma\n")
                response = self.app.get('/airports')
                self.assertEqual(response.status_code, 400)
                data = response.get_json()
                self.assertIn('error', data)
            finally:
                if backup is not None:
                    with open(test_filename, 'w') as f:
                        f.write(backup)
                else:
                    os.remove(test_filename)
if __name__ == '__main__':
    unittest.main()