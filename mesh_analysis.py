import cv2
import numpy as np

def mesh_segmentation(image, res=120):
    # print(image)
    print("Dimensiones:", image.shape)
    
    for y in range(res, 1080+1, res):
        for x in range(res, 1920+1, res):
            # Generates cell object
            





