import serial
from config import COM_ESP
import time
import numpy as np
from scipy.ndimage import label, center_of_mass
from coordinates import hotspot_en_area

np.random.seed(42)
temp_array = np.random.uniform(20,25, size=(120, 160))
temp_array[0:10, 0:10] = 135
temp_array[50:60, 0:10] = 95
temp_array[100:110, 0:10] = 83

temp_array[0:10, 50:60] = 129
temp_array[50:60, 50:60] = 92

temp_matrix = temp_array

def get_temperature(coordinates, hotspots,hotspot_location,t_amb,thermal_matrix, fire_location):

    temp_array = np.empty((coordinates.shape[0], coordinates.shape[1]), dtype=np.float32)
    dif_lat = None
    dif_lon = None

    fire_cells_loc = []
    fire_cells = []

    for i in range(1, len(coordinates)):
        lat1, lon1 = coordinates[i - 1][i-1]  
        lat2, lon2 = coordinates[i][i]
        dlat = (lat2 - lat1)
        dlon = (lon2 - lon1)

        if dlat != 0:
            dif_lat = dlat if dif_lat is None else min(dif_lat, dlat)
        if dlon != 0:
            dif_lon = dlon if dif_lon is None else min(dif_lon, dlon)

    for row in range(coordinates.shape[0]):
        for col in range(coordinates.shape[1]):
            lat, lon = coordinates[row][col]
            lat2, lon2 = lat + dif_lat, lon + dif_lon
            dentro = hotspot_en_area(hotspot_location,lat,lon,lat2,lon2)
            fire_cells_loc = hotspot_en_area(fire_location,lat,lon,lat2,lon2)

            hotspot_temp = None
            if dentro:
                # Si el hotspot está dentro de la celda, asignar la temperatura del hotspot
                for idx, (lat, lon) in dentro:
                    cx, cy = hotspots[idx]
                    hotspot_temp = thermal_matrix[cx,cy]
                
                temp_array[row][col] = (hotspot_temp +10) / 150 #normalizar entre 0 y 1
            else:
                # Si no está dentro de un hotspot, asignar la temperatura ambiente
                temp_array[row][col] = (t_amb +10) / 150 #normalizar entre 0 y 1

            if fire_cells_loc:
                cx, cy = col, row
                fire_cells.append((cy, cx))
    
    fire_cells = np.array(fire_cells)
    return temp_array,fire_cells

def get_temp_matrix(puerto=COM_ESP, baudios=115200, timeout=20):
    try:
        ser = serial.Serial(puerto, baudios, timeout=1)
    except serial.SerialException as e:
        print(f"Error al abrir el puerto serial: {e}")
        return None

    print("Esperando <START>...")
    start_time = time.time()
    buffer = ""

    # Esperar hasta encontrar <START>
    while True:
        if time.time() - start_time > timeout:
            print("Tiempo máximo de espera alcanzado.")
            ser.close()
            return None

        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += chunk
            if "<START>" in buffer:
                buffer = buffer.split("<START>")[1]
                break

    print("<START> detectado. Leyendo datos hasta <END>...")

    # Leer hasta <END>
    while "<END>" not in buffer:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += chunk
        else:
            time.sleep(0.01)

    ser.close()
    datos_brutos = buffer.split("<END>")[0].strip()
    filas = datos_brutos.strip().splitlines()

    try:
        matriz = [list(map(float, fila.strip().split(','))) for fila in filas]
        return np.array(matriz, dtype=np.float32)
    except Exception as e:
        print(f"Error al convertir a matriz: {e}")
        return None


def detectar_hotspots(matriz_temp, tamano_minimo=5):
    """
    Detecta hotspots en una matriz de temperaturas.

    Parámetros:
    - matriz_temp: np.ndarray de forma (60, 80), con temperaturas en °C.
    - tamano_minimo: tamaño mínimo (en píxeles) para que un cluster sea considerado un hotspot.

    Retorna:
    - Lista de tuplas (fila, columna) que representan el centro de cada hotspot detectado.
    - temperatura ambiente calculada como la mediana de la matriz.
    """
    # Calcular la temperatura ambiente como la mediana de la matriz
    temp_ambiente = np.median(matriz_temp)

    margen = .8* temp_ambiente

    # Crear una máscara binaria donde las temperaturas superan el umbral
    mascara = matriz_temp > (temp_ambiente + margen)

    # Etiquetar las regiones conectadas en la máscara
    estructura = np.ones((3, 3), dtype=int)  # Conectividad de 8 vecinos
    etiquetas, num_etiquetas = label(mascara, structure=estructura)

    # Calcular el centro de masa de cada región etiquetada
    centros = center_of_mass(mascara, etiquetas, range(1, num_etiquetas + 1))

    # Filtrar los hotspots por tamaño mínimo
    hotspots = []
    for i, centro in enumerate(centros):
        if np.sum(etiquetas == (i + 1)) >= tamano_minimo:
            fila, columna = centro
            hotspots.append((int(round(fila)), int(round(columna))))
    hotspots = np.array(hotspots)
    return hotspots, temp_ambiente
