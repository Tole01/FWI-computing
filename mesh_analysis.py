import cv2
import numpy as np
from computingFWI import meshCell
from coordinates import pixel_to_gps

# Camera resolution parameters (substitute for Walksnail Moonlight)
img_width, img_height, fov_x_deg, fov_y_deg = 3840, 2160, 157, 140
# Drone Coordinates (substitue for real-time flight)
drone_lat, drone_lon, height_m = 25.61861, -100.35697, 50


def mesh_segmentation(image, x_resolution = 240, y_resolution = 360):
    '''Generates a mesh of a specified cell number according to the chosen resolution, and 
     computes the parameters and risk score for each cell.
     
     Input: 
        image           -> frame captured by optical camera
        x_resolution    -> pixel resolution for the x axis
        y_resolution    -> pixel resolution for the y axis

    Output: 
        mesh            -> Array of arrays, where each element represents a cell object.
       '''
    x_columns, y_rows = (1920 // x_resolution), (1080 // y_resolution)
    
    mesh = [[None for _ in range(x_columns + 1)] for _ in range(y_rows + 1)]

    for row in range(1, y_rows + 1):
        for col in range(1, x_columns + 1):
            # Pixel position of the cell
            x_pixel, y_pixel = col * x_resolution, row * y_resolution
            # Convert pixel coordinates into GPS
            lat, lon = pixel_to_gps(x_pixel, y_pixel, img_width, img_height, 
                                    height_m, drone_lat, drone_lon, fov_x_deg, fov_y_deg)
            print(f'\n{lat}, {lon}')
            # Creates object and calculates parameters/risk score
            cell = meshCell(lat, lon, row, col)
            try:
                # Computes parameters and risk score
                cell.compute_indices()
                for index, val in cell.indices.items():
                    print(f'-> {index} value: {val}')

                cell.compute_riskScore()
                print(f'{cell.risk:.2f}')
            except Exception as e:
                print(f'There was an error computing the indexes: {e}')
                quit()
       
            # Insterts object into array
            mesh[row][col] = cell

    print(mesh[2][3].risk)

    return mesh






