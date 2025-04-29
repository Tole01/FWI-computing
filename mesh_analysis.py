import cv2
import numpy as np
from computingFWI import meshCell
from coordinates import pixel_to_gps

def mesh_segmentation(image, resolution=120):
    
    print("Dimensions:", image.shape)
    
    x_columns, y_rows = (1920 // resolution), (1080 // resolution)
    x_pixel, y_pixel = resolution, resolution

    mesh = [[None for _ in range(x_columns)] for _ in range(y_rows)]

    for row in range(0, y_rows):
        for col in range(0, x_columns):
            # Convert pixel coordinates into GPS
            lat, lon = pixel_to_gps(x_pixel, y_pixel, 1920, 1080, 35, 25.618611, -100.356977, 160, 90)

            # Creates object and inserts into array
            cell = meshCell(lat, lon, row, col)
            # Calculates paramemeters and risk score
            mesh[row][col] = cell
            # Updates x,y cell pixels
            x_pixel += resolution; y_pixel += resolution

    #print(mesh)
    print(mesh[2][3].lat)






