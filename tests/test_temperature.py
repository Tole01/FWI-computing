import unittest
import random as r
from temperature import normalize_temperature, get_temperature


class TemperatureAnalysis(unittest.TestCase):
    def setUp(self):
        self.row, self.col = 9, 16
        self.temp_matrix = [ [r.randint(20, 140) for col in range(self.col)] for row in range(self.row) ]

    def test_normalize_temperature(self):
        # Test normalize_temperature function
        normalized = normalize_temperature(self.temp_matrix)                 
        self.assertEqual(len(normalized), self.row)  # Verifies numerbs of rows remains unchanged
        val = normalized[0][0]
        self.assertGreaterEqual(val, 0.0)            # Asserts number in range between 0.0 - 1.0
        self.assertLessEqual(val, 1.0)


    def test_get_temperature(self): 
        # Test get_temperature function
        self.assertTrue(self.temp_matrix[2][4])
        self.assertRaises(IndexError, get_temperature, self.temp_matrix, 17, 10) # Out of index for matrix raises Exception


if __name__ == "__main__":
    unittest.main()