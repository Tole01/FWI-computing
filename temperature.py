
def get_temperature(matrix, x, y):
    """
    Obtiene la temperatura de una matriz de temperaturas en una posición específica.

    :param matrix: Lista de listas que representa la matriz de temperaturas.
    :param x: Coordenada x (fila) en la matriz.
    :param y: Coordenada y (columna) en la matriz.
    :return: Temperatura en la posición (x, y).
    """
    matrix = normalize_temperature(matrix)

    if 0 <= x < len(matrix) and 0 <= y < len(matrix[0]):
        return matrix[x][y]
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