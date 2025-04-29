import unittest
import numpy as np
from mesh_analysis import mesh_segmentation
from coordinates import pixel_to_gps

class TestMeshAnalysis(unittest.TestCase):
    def setUp(self):
        # Create a dummy image (1080x1920 with 3 color channels)
        self.image = np.zeros((1080, 1920, 3), dtype=np.uint8)

    def test_mesh_segmentation(self):
        # Test mesh_segmentation with the dummy image
        try:
            mesh_segmentation(self.image, resolution=120)
        except Exception as e:
            self.fail(f"mesh_segmentation raised an exception: {e}")

    def test_pixel_to_gps(self):
        # Test pixel_to_gps with mock data
        lat, lon = pixel_to_gps(960, 540, 1920, 1080, 35, 25.618611, -100.356977, 70, 50)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

if __name__ == "__main__":
    unittest.main()