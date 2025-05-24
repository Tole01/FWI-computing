import serial
from config import COM_ESP
import time
import numpy as np
from scipy.ndimage import label, center_of_mass
from coordinates import hotspot_en_area

def get_temperature(coordinates, hotspots,hotspot_location,t_amb,thermal_matrix):

    temp_array = np.empty((coordinates.shape[0], coordinates.shape[1]), dtype=np.float32)
    dx = coordinates[0][1][0] - coordinates[0][0][0] 
    dy = coordinates[1][0][1] - coordinates[0][0][1]

    for col in range(coordinates.shape[1]):
        for row in range(coordinates.shape[0]):
            lat, lon = coordinates[row][col]
            lat2, lon2 = lat + dx, lon + dy
            dentro = hotspot_en_area(hotspot_location,lat,lon,lat2,lon2)

            hotspot_temp = None
            if dentro:
                # Si el hotspot está dentro de la celda, asignar la temperatura del hotspot
                for idx, (lat, lon) in dentro:
                    cx, cy = hotspots[idx]
                    hotspot_temp = thermal_matrix[cx][cy]
                
                temp_array[row][col] = (hotspot_temp +10) / 150 #normalizar entre 0 y 1
            else:
                # Si no está dentro de un hotspot, asignar la temperatura ambiente
                temp_array[row][col] = (t_amb +10) / 150 #normalizar entre 0 y 1
    
    return temp_array

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

    return hotspots, temp_ambiente
