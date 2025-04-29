import cv2
import numpy as np
from computingFWI import meshCell
from coordinates import pixel_to_gps

def mesh_segmentation(image, resolution=120):
    # print(image)
    print("Dimensiones:", image.shape)
    
    x_columns, y_rows = (1920 // resolution), (1080 // resolution)
    x_pixel, y_pixel = resolution, resolution

    for row in range(0, y_rows+1):
        for col in range(0, x_columns+1):
            # Convert pixel coordinates into GPS
            coordinates = pixel_to_gps(x_pixel, y_pixel, 1920, 1080, 35, 25.618611, -100.356977, 160, 90)
            lat, lon = coordinates[0], coordinates[1]
            # Creates object
            cell = meshCell(lat, lon, row, col)





