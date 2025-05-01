import unittest
from Api_file import get_weather_data, get_ndvi, get_slope


class Test_APIfunctions(unittest.TestCase):
    def setUp(self):
        self.lat, self.lon = 25.618611, -100.356977

    # Function test
    def test_weather_data(self): 
        '''Asserts data is a dictionary containing requiered parameters'''
        data = get_weather_data(self.lat, self.lon)
        self.assertIsInstance(data, dict)
        self.assertIn('humedad_relativa', data)

    def test_get_ndvi(self):
        '''Asserts ndvi is a normalized float value'''
        ndvi = get_ndvi(self.lat, self.lon)
        self.assertIsInstance(ndvi, float)
        self.assertGreaterEqual(ndvi, 0.0)
        self.assertLessEqual(ndvi, 1.0)
    
    def test_get_slope(self):
        '''Asserts slope is a positive valu between 0.0 - 90.0'''
        slope = get_slope(self.lat, self.lon)
        self.assertLessEqual(slope, 90.0)
        self.assertGreaterEqual(slope, 0.0)


if __name__ == "__main__":
    unittest.main()
