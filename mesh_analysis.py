import cv2
import numpy as np
from computingFWI import meshCell
from coordinates import pixel_to_gps

def mesh_segmentation(image, resolution=120):
    
    print("Dimensions:", image.shape)
    
    x_columns, y_rows = (1920 // resolution), (1080 // resolution)
    
    mesh = [[None for _ in range(x_columns + 1)] for _ in range(y_rows + 1)]

    img_width, img_height, fov_x_deg, fov_y_deg = 1920, 1080, 160, 90


    for row in range(1, y_rows):
        for col in range(1, x_columns):
            # Pixel position of the cell
            x_pixel, y_pixel = col * resolution, row * resolution
            # Convert pixel coordinates into GPS
            lat, lon = pixel_to_gps(x_pixel, y_pixel, img_width, img_height, 
                                    35, 25.618611, -100.356977, fov_x_deg, fov_y_deg)
            # Creates object and calculates parameters/risk score
            cell = meshCell(lat, lon, row, col)
            cell.compute_indices()
            print(f'I have computed the cell indices -> NDVI:{cell.ndvi}, Slope:{cell.slope},\
                  Thermal:{cell.thermal}, BUI:{cell.bui}')
            # cell.compute_riskScore()
            # Calculates paramemeters and risk score
            mesh[row][col] = cell

    #print(mesh)
    print(mesh[2][3].risk)






