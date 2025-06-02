import unittest
from utils import get_weather_data, get_ndvi, get_slope, get_weather_data2
import timeit, time, numpy as np


class Test_APIfunctions(unittest.TestCase):
    def setUp(self):
        self.lat, self.lon = 25.618611, -100.356977
        self.lats, self.lons = [25.618, 25.619, 25.620], [-100.3569, -100.3570, -100.3571]
        self.coordinates = np.array(
            [
                (25.6544201, -100.29693889),
                (25.6544201, -100.29601878),
                (25.6544201, -100.29509866),
                (25.6544201, -100.29417855),
                (25.6544201, -100.29325844),
            
            ])
        self.tec_lat, self.tec_lon = 25.651435, -100.290686 

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
        total = 0
        for i in range(50):
            start = time.perf_counter()
            slope = get_slope(self.lat, self.lon)
            # time = timeit.timeit(stmt="get_slope(self.lat, self.lon)", number=50)
            # print(f'In 50 iterations get_slope took {time} seconds')
            runtime = time.perf_counter() - start
            # print(f'Get slope function took: {runtime:.6f} seconds')
            total += runtime
        print(f'Total runtime: {total}')
        self.assertLessEqual(slope, 90.0)
        self.assertGreaterEqual(slope, 0.0)

    def test_get_weather_data(self):
        '''Check runtime of get_weather function'''
        total = 0 
        for i in range(50):
            start = time.perf_counter()
            weather_data = get_weather_data(self.lat, self.lon)
            # time = timeit.timeit(stmt="get_weather_data(self.lat, self.lon)", number=50)
            # print(f'In 50 iterations get_weather_data took {time} seconds')
            runtime = time.perf_counter() - start
            total += runtime
        print(f'Total runtime: {total}')
        self.assertIsInstance(weather_data, dict)

    def test_get_weather_data2(self):
        start = time.perf_counter()
        weather_data = get_weather_data2(self.coordinates)
        print(f'Get weather_data function took: {time.perf_counter() - start:.6f} seconds\n')
        print(weather_data)
        print(type(weather_data))
        print(weather_data.shape)
        # print(weather_data.shape)



if __name__ == "__main__":
    unittest.main()
