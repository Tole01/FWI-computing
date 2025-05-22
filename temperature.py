import serial
from config import COM_ESP
import time
import numpy as np
from scipy.ndimage import label, center_of_mass

def get_temperature(matrix, x, y):
    '''
    Obtiene la temperatura de una matriz de temperaturas en una posición específica.

    :param matrix: Lista de listas que representa la matriz de temperaturas.
    :param x: Coordenada x (columna) en la matriz.
    :param y: Coordenada y (fila) en la matriz.
    :return: Temperatura en la posición (x, y).
    '''
    matrix = normalize_temperature(matrix)

    if 0 <= y < len(matrix) and 0 <= x < len(matrix[0]):
        return matrix[y][x]
    else:
        raise IndexError("Coordenadas fuera de los límites de la matriz.")
    

def normalize_temperature(matrix):
    """
    Normaliza la temperatura de una matriz de temperaturas de -10 a 140

    :param matrix: Lista de listas que representa la matriz de temperaturas.
    :return: Matriz de temperaturas normalizada.
    """
    # Encuentra el valor mínimo y máximo en la matriz
    min_temp = -10  # Valor mínimo de temperatura de la camara
    max_temp = 140   # Valor máximo de temperatura de la camara

    # Normaliza la matriz
    normalized_matrix = [[(temp - min_temp) / (max_temp - min_temp) for temp in row] for row in matrix]
    
    return normalized_matrix


def get_temp_matrix(puerto=COM_ESP, baudios=115200, timeout=10):
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


def detectar_hotspots(matriz_temp, tamano_minimo=3):
    """
    Detecta hotspots en una matriz de temperaturas.

    Parámetros:
    - matriz_temp: np.ndarray de forma (60, 80), con temperaturas en °C.
    - margen: diferencia mínima en °C respecto a la temperatura ambiente para considerar un hotspot.
    - tamano_minimo: tamaño mínimo (en píxeles) para que un cluster sea considerado un hotspot.

    Retorna:
    - Lista de tuplas (fila, columna) que representan el centro de cada hotspot detectado.
    - temperatura ambiente calculada como la mediana de la matriz.
    """
    # Calcular la temperatura ambiente como la mediana de la matriz
    temp_ambiente = np.median(matriz_temp)

    margen = .25* temp_ambiente

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
