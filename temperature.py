import serial
"""
temp_matrix = [
    [135, 100,  40,  60,  80, 135,  30,  30,  60, 125, 130, 130, 130,  90,  60,  25],
    [130, 115, 140,  65, 135,  75, 110,  30,  25,  65,  25,  25,  25, 130, 130,  70],
    [130, 125,  35, 130, 130, 130, 115,  30, 135, 135, 105,  25,  25,  35,  35,  25],
    [ 40,  80, 130,  87,  25, 131,  75, 130, 135,  85,  70,  25,  25,  25,  25,  25],
    [130,  25, 120, 130, 130, 132, 130, 135, 100,  25, 100, 100, 115,  25,  25,  25],
    [135, 120, 125,  25,  25, 130,  25, 100,  25,  25,  95, 100, 107,  85,  25,  25],
    [ 85, 110,  85, 115, 135,  25,  25,  25,  25,  25,  25, 100, 135, 130,  45,  25],
    [ 25,  25,  25, 115, 130,  25,  25,  25, 100, 120, 120,  90, 135,  90, 135,  30],
    [ 30,  30,  30,  30,  30,  30,  30,  35,  40,  35,  60,  35,  90, 130,  95,  30]
]
"""
def get_thermal_image(): # Necesita completarse
    #conectarme al puerto serial para obtener la matriz del ESP32
    pass

def get_temperature(matrix, x, y):
    """
    Obtiene la temperatura de una matriz de temperaturas en una posición específica.

    :param matrix: Lista de listas que representa la matriz de temperaturas.
    :param x: Coordenada x (columna) en la matriz.
    :param y: Coordenada y (fila) en la matriz.
    :return: Temperatura en la posición (x, y).
    """
    matrix = normalize_temperature(matrix)

    if 0 <= y < len(matrix) and 0 <= x < len(matrix[0]):
        return matrix[y][x]
    else:
        raise IndexError("Coordenadas fuera de los límites de la matriz.")
    

def normalize_temperature(matrix):
    """
    Normaliza la temperatura de una matriz de temperaturas.

    :param matrix: Lista de listas que representa la matriz de temperaturas.
    :return: Matriz de temperaturas normalizada.
    """
    # Encuentra el valor mínimo y máximo en la matriz
    min_temp = -100  # Valor mínimo de temperatura de la camara
    max_temp = 140   # Valor máximo de temperatura de la camara

    # Normaliza la matriz
    normalized_matrix = [[(temp - min_temp) / (max_temp - min_temp) for temp in row] for row in matrix]
    
    return normalized_matrix

def get_temp_matrix():
    """
    Lee el puerto serial del esp32 y recibe la matriz 16x9 de temperatura de la camara termica

    param: None

    :return: temp_matrix (matriz) 16x9 de temperatura 
    """
    ser = serial.Serial('COM7', 115200, timeout=1)

    temp_matrix = []
    leyendo = False
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line == "<START>":
            leyendo = True
            temp_matrix = []
            continue
        elif line == "<END>":
            break
        elif leyendo:
            try:
                fila = [int(x) for x in line.split(",")]
                if len(fila) == 16:
                    temp_matrix.append(fila)
            except ValueError:
                continue  # Ignora líneas corruptas

    return temp_matrix
