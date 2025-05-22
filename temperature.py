import serial
from config import COM_ESP
import time
import numpy as np

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


def get_temp_matrix(puerto='COM3', baudios=115200, timeout=10):
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

    print("✅ <START> detectado. Leyendo datos hasta <END>...")

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
