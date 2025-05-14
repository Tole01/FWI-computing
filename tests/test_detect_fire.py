import unittest, time
from ultralytics import YOLO
import numpy as np
from fire_detection import detect_fire


class Test_FireDetectionModel(unittest.TestCase):
    def setUp(self):
        self.model = YOLO(r"fire_s.pt")

    def test_detect_fire(self):
        # Verifies runtime and performs validation of outputs
        total_runtime = 0 
        for test in range(5):
            start = time.perf_counter()
            img_optica, cx, cy, fire_coordinates = detect_fire(self.model)
            end = time.perf_counter()
            self.assertIsInstance(img_optica, np.ndarray)
            self.assertGreater(len(fire_coordinates), 0)

            runtime = (end - start)
            print(f'Iteration [{test}] took: {runtime:.6f} seconds')

            total_runtime += runtime

        avg_runtime = total_runtime / 5
        print(f'\nAverage runtime per iteration: {avg_runtime:.6f}')

if __name__ == "__main__":
    unittest.main()     
