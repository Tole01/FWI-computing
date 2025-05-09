import unittest
import numpy as np
from coordinates import pixel_to_gps
from mesh import mesh_segmentation

class TestMeshAnalysis(unittest.TestCase):
    def setUp(self):
        # Create a dummy image (1080x1920 with 3 color channels)
        self.image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.gps = (25.650711, -100.289578, 150)

    def test_mesh_segmentation(self):
        # Test mesh_segmentation with the dummy image
        try:
            risk_scores = mesh_segmentation(self.image, self.gps[0], self.gps[1], self.gps[2])
        except Exception as e:
            self.fail(f"mesh_segmentation raised an exception: {e}")
        # print(risk_scores)

    def test_pixel_to_gps(self):
        # Test pixel_to_gps with mock data
        lat, lon = pixel_to_gps(960, 540, 1920, 1080, 35, 25.618611, -100.356977, 70, 50)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    def test_risk_score(self):
        # Test risk score calculation function
        pass 

if __name__ == "__main__":
    unittest.main()