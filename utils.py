import requests
import datetime

from sentinelhub import SHConfig, BBox, CRS, SentinelHubRequest, DataCollection, MimeType
import numpy as np

from PIL import Image
from io import BytesIO
import math
from multiprocessing import Pool
from datetime import datetime

# Credenciales para la API Sentinel Hub (NDVI)
config = SHConfig()
config.sh_client_id = 'fda7dccb-da21-4e14-9ee2-edbc46678486'
config.sh_client_secret = 'OV6hcplnH0GJlwfP2Cx6KwYxb01J93or'
config.instance_id = '0761f443-a1b1-44da-b274-b58436d5056d'

# Evalscript para NDVI
evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: {
      id: "default",
      bands: 1,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""

evalscript_ndvi2 = """
        //V=3
        function setup() {
            return {
                input: ["B04", "B08"],
                output: { bands: 1, sampleType: "FLOAT32" }
            };
        }
        function evaluatePixel(sample) {
            let ndvi = [(sample.B08 - sample.B04) / (sample.B08 + sample.B04)];
            return [ndvi]
        }
        """

def get_weather_data2(coordinates_row, size=16):
    '''
    Uses Open-Meteo Weather API to obtain the weather data for each of the mesh coordinates.

    Input: coordinates_row -> 2D Numpy array of shape (16, 2) containing (lat lon) pairs of coordiantes.

    Output: weather_Data -> 1D Numpy array (16, ) containing a weather dictionary

    '''
    # Open-Meteo doesn't require API key
    url = "https://api.open-meteo.com/v1/forecast"

    assert coordinates_row.shape == (size, 2), "Size of array isn't properly formatted"
    lats = coordinates_row[:, 0]
    lons = coordinates_row[:, 1]

    # Set request parameters
    params = {
        "latitude" :  [lat for lat in lats], # 144 elements
        "longitude" : [lon for lon in lons], # 144 elements
        "hourly" : "temperature_2m,relative_humidity_2m,wind_speed_80m,precipitation",
        "timezone" : "auto",
    }
    
    # Generate request 
    response = requests.get(url, params=params)

    # Obtain data
    try: 
        data = response.json()  # Retrieve data dictionary
    except Exception as e:
        print('There was en error retreiving data: {e}')

    # Generate array of dictionaries
    current_hour = datetime.now().hour
    
    weather_data = np.array(
         
            [ 
                {'t2m_C': data[i]["hourly"]["temperature_2m"][current_hour],
                 'humedad_relativa': data[i]["hourly"]["relative_humidity_2m"][current_hour],
                 'wind_speed_kmh': data[i]["hourly"]["wind_speed_80m"][current_hour],
                 'precipitation_mm': data[i]["hourly"]["precipitation"][current_hour],
                 'month': datetime.now().month} for i in range(len(lons))
            ]
        )
        

    assert weather_data.shape == (size, ), "Shape is incorrect"

    return weather_data


def get_weather_data(lat, lon):
    """
    Utiliza OpenWeatherMap para obtener datos del clima en una ubicación específica.
    Retorna:
        dict: Diccionario con datos del clima (temperatura, humedad, velocidad del viento, precipitación y mes actual).
    """
    api_key = 'd73f8f737d7728a9d2ea0ffcd8779ff2' #API OpenWeather
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    data = requests.get(url).json()

    temperatura = data['main']['temp']
    humedad = data['main']['humidity']
    viento_m_s = data['wind']['speed']
    precipitacion = data.get('rain', {}).get('1h', 0.0)
    viento_kmh = viento_m_s * 3.6
    mes = datetime.datetime.now().month

    return {
        't2m_C': temperatura,
        'humedad_relativa': humedad,
        'wind_speed_kmh': viento_kmh,
        'precipitation_mm': precipitacion,
        'month': mes
    }


def get_ndvi(lat, lon):
    """
    Utiliza Sentinel Hub para obtener el NDVI en una ubicación específica.
    Retorna:
        float: Valor del NDVI.
    """
    bbox = BBox(bbox=[lon - 0.00005, lat - 0.00005, lon + 0.00005, lat + 0.00005], crs=CRS.WGS84)
    time_interval = ('2024-12-01', '2025-04-01')

    request = SentinelHubRequest(
        evalscript=evalscript_ndvi,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order='mostRecent'
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF)
        ],
        bbox=bbox,
        size=(10, 10),
        config=config
    )

    response = request.get_data()
    ndvi_array = response[0]
    ndvi_mean = float(np.nanmean(ndvi_array))

    ndvi_normalized = (ndvi_mean + 1) / 2  # Normalizar NDVI entre 0 y 1

    return ndvi_normalized

def latlon_to_tilexy(lat, lon, zoom):
    """
    Convierte coordenadas de latitud y longitud a coordenadas de tile (x, y) para un nivel de zoom específico.
    Args:
        lat (float): Latitud en grados decimales.
        lon (float): Longitud en grados decimales.
        zoom (int): Nivel de zoom deseado.
    Returns:
        tuple: Coordenadas de tile (x, y).
    """
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(math.radians(lat)) +
                (1 / math.cos(math.radians(lat)))) / math.pi) / 2.0 * n)
    return x_tile, y_tile

def decode_elevation(r, g, b):
    """
    Decodifica la elevación a partir de los valores RGB.
    Args:
        r (int): Valor del canal rojo.
        g (int): Valor del canal verde.
        b (int): Valor del canal azul.
    Returns:
        float: Elevación en metros.
    """
    # Overflow management / Clamp values from 0-255
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))  
    # Cast to int32 to prevent overflow during multiplication
    r = np.int32(r)
    g = np.int32(g)
    b = np.int32(b)

    return -10000 + ((r * 255 * 255 + g * 255 + b) * 0.1)

def get_tile_image(x_tile, y_tile, zoom, MAPBOX_TOKEN):
    """
    Obtiene la imagen del tile de Mapbox para las coordenadas y el nivel de zoom especificados.
    Args:
        x_tile (int): Coordenada x del tile.
        y_tile (int): Coordenada y del tile.
        zoom (int): Nivel de zoom.
        MAPBOX_TOKEN (str): Token de acceso a la API de Mapbox.
    Returns:
        PIL.Image: Imagen del tile.
    """
    url = f"https://api.mapbox.com/v4/mapbox.terrain-rgb/{zoom}/{x_tile}/{y_tile}.pngraw?access_token={MAPBOX_TOKEN}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error al obtener tile: {response.status_code}")
    image = Image.open(BytesIO(response.content)).convert("RGB")
    return np.array(image, dtype=np.uint8)

def get_slope(lat, lon):
    """
    Calcula la pendiente del terreno en grados a partir de los valores RGB de un tile de Mapbox.
    Args:
        lat (float): Latitud en grados decimales.
        lon (float): Longitud en grados decimales.
        ZOOM (int): Nivel de zoom deseado.
        MAPBOX_TOKEN (str): Token de acceso a la API de Mapbox.
    Returns:
        float: Pendiente en grados.
    """
    MAPBOX_TOKEN = 'pk.eyJ1IjoiamFjb2JvMjciLCJhIjoiY204eW5maTdjMDMwODJqb293ZGd4cTNscSJ9.0_kcUB4XbYyrw3PPGT-QuQ'
    ZOOM = 17  # Quieres mayor o menor resolución
    x_tile, y_tile = latlon_to_tilexy(lat, lon, ZOOM)
    print(x_tile, y_tile)
    image = get_tile_image(x_tile, y_tile, ZOOM, MAPBOX_TOKEN)
    print(image)
    pixels = np.array(image)
    tile_size = pixels.shape[0]
    center = tile_size // 2

    Z = np.zeros((3, 3))
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            px = center + dx
            py = center + dy
            r, g, b = pixels[py, px][:3]
            # print(f'r: {r}, g: {g}, b: {b}')
            Z[dy + 1, dx + 1] = decode_elevation(r, g, b)

    dz_dx = ((Z[0,2] + 2*Z[1,2] + Z[2,2]) - (Z[0,0] + 2*Z[1,0] + Z[2,0])) / 8.0
    dz_dy = ((Z[2,0] + 2*Z[2,1] + Z[2,2]) - (Z[0,0] + 2*Z[0,1] + Z[0,2])) / 8.0

    slope_rad = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
    slope_deg = math.degrees(slope_rad)

    slope_normalized = slope_deg / 90.0  # Normalizar entre 0 y 1

    return slope_normalized

def get_slope2(coordinates_row, size=16):
    '''Computes the slope of a coordinate point by calculating with a gradient from its neighbors'
    
    Input: coordinates_row -> 2D Numpy Array of shape (16, 2)

    Output: slopes -> 1D Numpy array of shape (16, )

    '''
    assert coordinates_row.shape[1] == 2, "Coordinates must be in pairs"
    
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    # api_key = reemplazar por la API obtenida de Google Cloud.

    # Define request parameters
    params = {
                "locations": "|".join([f"{lat},{lon}" for lat, lon in coordinates_row]),
                "key": None
    }

    response = requests.get(url, params=params)

    try: 
        data = response.json()
        print(data)
    except Exception as e:
        print(f'There was an error fetching JSON data: {e}')

    return None

    


def get_ndvi_batch(coordinates, delta_lat=0.0008):
    """
    Fetch NDVI for multiple coordinates in one request.

    Input: coordinates -> 2D NumPy Array containing the [lat, lon] pairs of a batch.

    Output: ndvi -> Numpy 1D Array containing the NDVI value for each pair of the batch.

    """
    if isinstance(coordinates, np.ndarray):
        # Asserts last dimension is a pair of coordinates
        assert coordinates.shape[1] == 2, f"Numpy Array doesn't have correct dimensions: {coordinates.shape}"
        width, depth = coordinates.shape
    
    else:
        print("Input must be a python Iterable")
        return None

    # Flip array to ensure GeoJSON format (lon, lat)
    # print(coordinates)

    # Calcuta delta of polygons from lon variation of entire row
    upper_lat, upper_lon = coordinates[0]
    lower_lat, lower_lon = coordinates[-1]

    delta_lon = abs(upper_lon - coordinates[1, 1])
    # Update lat and lon to generate rectangle geometry (Negative as it decreases downward and increases to the right)
    lower_lat -= delta_lat
    lower_lon += delta_lon
    
    # Create bounding box of interest
    bbox = BBox(bbox=[upper_lon, upper_lat, lower_lon, lower_lat], crs=CRS.WGS84)

    # Make the request
    request = SentinelHubRequest(
        evalscript= evalscript_ndvi2,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=('2024-12-01', '2025-04-01'),
                mosaicking_order='mostRecent',
                maxcc=0.5
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF)
        ],
        bbox=bbox,
        size=(width, 1),
        # size=(width * 2, depth),
        config=config
    )
    try:
        response = request.get_data()
        ndvi_array = response[0][0]
        # Compute Average of Cells
       
        # Return array
        return ndvi_array
    
    except Exception as e:
        raise Exception(f"API request failed: {str(e)}")
     

def batch_average(batch, width, step=2):
    '''Compute the averag NDVI for each batch'''
    for i in range(0, width - 2, step):
        first_row = batch[i, i + step]
        second_row = batch[i, i + step]
    pass


# Assigned weight to parameters
weights = {'NDVI': 0.23, 'SLOPE': 0.03, 'THERMAL': 0.48, 'BUI': 0.26}

def calculate_risk_score(ndvi, slope, thermal, bui):
    """
    Calcula el riesgo de incendio utilizando el índice de humedad del combustible (BUI), NDVI y la pendiente del terreno.
    Donde:
    - BUI: Índice de humedad del combustible.
    - NDVI: Índice de vegetación de diferencia normalizada.
    - slope: Pendiente del terreno.
    - T_max: Temperatura máxima en °C.
    - risk_score: Puntuación de riesgo de incendio.
    Retorna:
        risk_score: Puntuación de riesgo de incendio.  
    """

    """
    >>> calculate_risk_score(0.4, 10, 25, 30)
    0.0
    >>> calculate_risk_score(0.6, 20, 35, 40)
    0.5 
    >>> calculate_risk_score(0.8, 30, 45, 50)
    1.0
    """
    values = {'NDVI': ndvi, 'SLOPE': slope, 'THERMAL': thermal, 'BUI': bui}
    
    risk_score = sum( [weights[param.upper()] * values[param] for param in values.keys()] )
    
    return risk_score

def normalizar(arr):
    """
    Normaliza un array 1D entre 0 y 1.
    
    Args:
        arr (numpy.ndarray): Array 1D a normalizar.
    
    Returns:
        numpy.ndarray: Array normalizado.
    """
    min_val = np.min(arr)
    max_val = np.max(arr)
    
    if max_val - min_val == 0:
        return np.zeros_like(arr)  # Evitar división por cero
    
    normalized_arr = (arr - min_val) / (max_val - min_val)
    
    return normalized_arr



