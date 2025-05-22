import cv2
import numpy as np
from classes import meshCell
from coordinates import pixel_to_gps, pixel_to_gps_vectorized
from utils import get_weather_data, get_ndvi, get_slope, calculate_risk_score
from classes import calculate_fwi
from temperature import get_temperature

weights = {}

# Camera resolution parameters (substitute for Walksnail Moonlight)
fov_x_deg, fov_y_deg = 157, 140

def mesh_segmentation(image, drone_lat, drone_lon, height_m, hotspots,hotspot_location,t_amb,x_columns = 16, y_rows = 9):
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

    print(f'Image Dimensions: {img_width}x{img_height}')
    print(f'Mesh Dimensions: {x_columns}x{y_rows}')

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
                continue 
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
                continue
       
            # Insterts object into array
            mesh[row][col] = cell.risk
            coord_list.append( (cell.lat, cell.lon, cell.risk) )
            
    return mesh, coord_list


def mesh_segmentation2(image, d_lat, d_lon, d_height,hotspots,hotspot_location,t_amb, x_columns = 16, y_rows = 9):
    '''
    Generates the mesh analysis from the image taken by the optical camera. 

    Input:


    Output:


    '''
    # Generate GPS coordinates mesh
    coords = generate_coordinates(image, x_columns, y_rows, d_lat, d_lon, d_height)
    # Compute Indices
    indices = compute_indices(coords, hotspots,hotspot_location,t_amb)
    # Computes risk score
    risk = compute_riskscore(indices)

    return risk 


    # Compute indices / Call API's from coords



def generate_coordinates(image, x_columns, y_rows, d_lat, d_lon, d_height):
    '''
    Generates a Coordinates Mesh where each element in the mesh represent a (lat, lon) pair.

    Input: image     -> Optical image taken from the sensor (Numpy Array)
           x_columns -> Number of mesh columns (integer)
           y_rows    -> Number of mesh rows    (integer)

    Output: 3-D Numpy array of size (height x width x 2) 
            where each element is a 1-D Numpy array containing (lat, lon) pairs.
    '''
    # Display image attributes
    img_height, img_width, channels = image.shape
    print(f'Image Resolution: ({img_height} x {img_width}) pixels')

    x_res, y_res = (img_width / x_columns), (img_height / y_rows)

    # Generate custom mesh with corresponding resolution
    y_pixels, x_pixels = np.mgrid[0:img_height:y_res, 
                                  0:img_width:x_res]
    
    # Apply pixel_to_gps function to bothp y, x pixel arrays
    lats, lons = pixel_to_gps_vectorized(y_pixels, x_pixels, img_width, 
                                       img_height, d_height, d_lat, d_lon)
   
    # Stack both arrays to generate a 3-D array with (lat, lon) pairs as items
    coords = np.stack((lats, lons), axis=-1)

    return coords

def compute_indices(coordinates, hotspots,hotspot_location,t_amb):
    '''
    Generates an indices array containing (ndvi, slope, thermal, bui) values.

    Input: 
        coordinates -> 3D Numpy array containing (lat, lon) pairs of each cell.

    Output:
        indices -> 3D Numpy array of shape (height x width x 4) containing (ndvi, slope thermal, bui) 
        values stored as 1D arrays.
    '''
    assert coordinates.shape == (9, 16, 2), "Input array dimensions are incorrect"
    # Access lat, lon arrays
    lat = coordinates[:, :, 0]
    lon = coordinates[:, :, 1]
    
    # Vectorize all of the functions
    get_ndvi_vectorized = np.vectorize(get_ndvi)
    get_slope_vectorized = np.vectorize(get_slope)
    get_thermal_vectorized = np.vectorize(get_temperature)
    get_weather_data_vectorized = np.vectorize(get_weather_data)
    get_fwi_vectorized = np.vectorize(calculate_fwi)


    # Call API's on the input arrays
    try:
        print('Starting to compute APIs...')
        temp = get_thermal_vectorized(coordinates, hotspots,hotspot_location,t_amb)
        ndvi = get_ndvi_vectorized(lat, lon)
        slopes = get_slope_vectorized(lat, lon)
        weather = get_weather_data_vectorized(lat, lon)
        fwi = get_fwi_vectorized = (weather)
        bui = np.vectorize(lambda array: array['BUI'], otypes=[float])(fwi)

    except Exception as e:
        print(f'There was an error calling the APIs: {e}')
        raise


    # Combine parameters into a single array
    indices = np.stack((ndvi, slopes, temp, bui), axis=-1)

    return indices 

weights = {'NDVI': 0.23, 'SLOPE': 0.03, 'THERMAL': 0.48, 'BUI': 0.26}

def compute_riskscore(indices):
    '''
    Computes the risk score for each mesh cell through vectorization.

    Input:
            indices -> 3D Numpy array containing as items the indices (ndvi, slope, thermal, bui) as 1D arrays
    Output:
            risk_score -> 2D Numpy array containing as items the risk score for each row

            0th item in array -> NDVI
            1st -> SLOPE
            2nd -> THERMAL
            3rd -> BUI
    ''' 
    assert isinstance(indices, np.ndarray), "Indices must be a Numpy Array"
    assert indices.shape == (9, 16, 3), "Array doesn't have correct dimensions"
     
    NDVI = indices[:, :, 0]  # All NDVI values (9 x 16) shape
    SLOPE = indices[:, :, 1] # All Slope values
    THERMAL = indices[:, :, 2]  # All Thermal values / Modify implementation
    BUI = indices[:, :, 3]   # All BUI values

    return NDVI * weights['NDVI'] + SLOPE * weights['SLOPE'] + BUI * weights['BUI']
     







def vectorize_function(functions):
    '''
    Vectorizes a given function as input. 
    '''
    pass





