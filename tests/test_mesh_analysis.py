import unittest
import time
import numpy as np
from coordinates import pixel_to_gps
from mesh import mesh_segmentation2, generate_coordinates, compute_indices, compute_riskscore
import random as r 

class TestMeshAnalysis(unittest.TestCase):
    def setUp(self):
        # Create a dummy image (1080x1920 with 3 color channels)
        self.image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.gps = (25.650711, -100.289578, 150)
        self.coords = np.array([
                                [ [r.uniform(25.650711, 26.650711), r.uniform(-100.289578, -101.289578)] for col in range(16)]
                                    
                                for row in range(9)
                                    
                                ])
        self.indices =  np.array([
                                [ [r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 1)] for col in range(16)]
                                    
                                for row in range(9)
                                    
                                ])

    def test_mesh_segmentation(self):
        # Test mesh_segmentation with the dummy image
        try:
            start = time.perf_counter()
            risk_scores = mesh_segmentation2(self.image, self.gps[0], self.gps[1], self.gps[2])
            end = time.perf_counter()
            print(f'Total runtime for mesh: {(end - start):.6f}')
        except Exception as e:
            self.fail(f"mesh_segmentation raised an exception: {e}")
        # print(risk_scores)

    def test_pixel_to_gps(self):
        # Test pixel_to_gps with mock data
        start = time.perf_counter()
        lat, lon = pixel_to_gps(960, 540, 1920, 1080, 35, 25.618611, -100.356977, 70, 50)
        end = time.perf_counter()
        print(f'Pixel to GPS function runtime: {(end - start):.6f}')
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    def test_generate_coordinates(self):
        # Test generate coordiantes function runtime
        start = time.perf_counter()
        coords_mesh =  generate_coordinates(self.image, 16, 9, self.gps[0], self.gps[1], self.gps[2])
        print(f'Generate coordinates took: {(time.perf_counter() - start):.4f} seconds')
        print(coords_mesh)
        # Assert output datatype and size of array
        self.assertIsInstance(coords_mesh, np.ndarray)
        self.assertEqual(coords_mesh.shape, (9, 16, 2))
        self.assertEqual(coords_mesh.size, 288)
        
    def test_compute_indices(self):
        start = time.perf_counter()
        indices = compute_indices(self.coords)
        print(f'Computing the indices took: {(time.perf_counter() - start):.6f} seconds')
        self.assertEqual(indices.shape, (9, 16, 3))

    def test_compute_riskscore(self):
        start = time.perf_counter()
        risk = compute_riskscore(self.indices)
        print(f'Computing the indices took: {(time.perf_counter() - start):.6f} seconds')
        self.assertEqual(risk.shape, (9, 16))
        

if __name__ == "__main__":
    unittest.main()