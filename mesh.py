import cv2
import numpy as np
from classes import meshCell
from coordinates import pixel_to_gps

# Camera resolution parameters (substitute for Walksnail Moonlight)
fov_x_deg, fov_y_deg = 157, 140

def mesh_segmentation(image, drone_lat, drone_lon, height_m, x_columns = 16, y_rows = 9):
    '''Generates a mesh of a specified cell number according to the chosen resolution, and 
     computes the parameters and risk score for each cell.
     
     Input: 
        image           -> frame captured by optical camera (NumPy Array)
        x_resolution    -> pixel resolution for the x axis
        y_resolution    -> pixel resolution for the y axis

    Output: 
        mesh            -> Array of arrays, where each element represents the cell risk score.
       '''
    
    img_height, img_width, channels = image.shape

    x_resolution, y_resolution = (img_width // x_columns), (img_height // y_rows)
    
    coord_list = []
    mesh = [[None for _ in range(x_columns)] for _ in range(y_rows)]
    print(f'Image shape: {img_height}x{img_width}')
    print(f'Cell shape: {y_resolution}x{x_resolution}')
    print(f'Number of cells: {y_rows}x{x_columns}')
    for row in range(y_rows):
        for col in range(x_columns):
            # Pixel position of the cell
            x_pixel, y_pixel =  col * x_resolution, row * y_resolution
            print(f'\nCell -> Row:[{row}]Col:[{col}]')
            # Convert pixel coordinates into GPS
            try: 
                lat, lon = pixel_to_gps(x_pixel, y_pixel, img_width, img_height, 
                                        height_m, drone_lat, drone_lon, fov_x_deg, fov_y_deg)
            except:
                print('Error converting pixel to GPS coordinates.')
                quit()
            print(f'\nCoordinates: {lat}, {lon}')
            # Creates object and calculates parameters/risk score
            cell = meshCell(lat, lon, row, col)
            try:
                # Computes parameters 
                cell.compute_indices()
                for index, val in cell.indices.items():
                    print(f'-> {index} value: {val}')
                # Compute risk score
                cell.compute_riskScore()
                print(f'Risk score: {cell.risk:.4f}')
            except Exception as e:
                print(f'There was an error computing the indexes: {e}')
                quit()
       
            # Insterts object into array
            mesh[row][col] = cell.risk
            coord_list.append( (cell.lat, cell.lon, cell.risk) )
    return mesh, coord_list





