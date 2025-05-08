import random as r 

temp_matrix = [ [r.randint(20, 130) for col in range(16)] for row in range(9) ]


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



"""
T = get_img(void)
Retorna una matriz de temperaturas de 160x120
Se conceta a la camara termica y obtiene la imagen

T_max = get_max_temp(T)
Retorna una matriz de temperaturas de 16 x 9
Junta pixeles de la camara termica, calcula el maximo de cada bloque y lo guarda en la matriz

Temp = get_temperature(row, column)
Retorna la temperatura de la matriz de temperaturas maximas en la posicion row,column
Se llama desde el mesh analysis para guardar la temperatura de cada celda
"""