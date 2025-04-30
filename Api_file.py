import requests
import datetime

from sentinelhub import SHConfig, BBox, CRS, SentinelHubRequest, DataCollection, MimeType
import numpy as np

from PIL import Image
from io import BytesIO
import math

# Credenciales para la API Sentinel Hub (NDVI)
config = SHConfig()
config.sh_client_id = 'c48dbe29-c5dc-4365-92c7-2e6d12099699'
config.sh_client_secret = 'PkWmBXXsAZx7ROITjhHoYHgPbH5vfHG2'
config.instance_id = '098c8ff2-731c-4b1c-9581-a69041518609'

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
    ZOOM = 15  # Quieres mayor o menor resolución
    x_tile, y_tile = latlon_to_tilexy(lat, lon, ZOOM)
    image = get_tile_image(x_tile, y_tile, ZOOM, MAPBOX_TOKEN)
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
