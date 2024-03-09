import unittest
from datetime import datetime
import pandas as pd
import psycopg2

class DataValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="invstodb",
            user="admin",
            password="adminadmin"
        )

    def tearDown(self):
        self.conn.close()

    def test_data_validation(self):
        # Read data from the database table
        query = "SELECT * FROM ticker_data"
        data = pd.read_sql_query(query, self.conn)

        self.assertTrue(self.validate_data(data))

    def validate_data(self, data):
        for idx, row in data.iterrows():
            if not isinstance(row['datetime'], datetime):
                return False
            if not isinstance(row['close'], float) or not isinstance(row['high'], float) or not isinstance(row['low'], float) or not isinstance(row['open'], float):
                return False
            if not isinstance(row['volume'], int):
                return False
            if not isinstance(row['instrument'], str):
                return False
        return True

if __name__ == '__main__':
    unittest.main()