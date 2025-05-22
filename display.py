import cv2
import numpy as np
from scipy.ndimage import convolve

def NNI_kernel(matriz):
    kernel = np.ones((3, 3)) / 9  # Kernel de promedio 3x3
    return convolve(matriz, kernel, mode='nearest')

def colorear_celdas(imagen, matriz, fire_coordinates):
    """
    Divide la imagen en 16x9 celdas y colorea cada celda de acuerdo con el valor en la matriz.
    Verde: 0 - 0.3
    Amarillo: 0.31 - 0.7
    Rojo: 0.71 - 1
    Transparente para mantener visibilidad de la imagen base.

    Args:
        imagen (str or np.ndarray): Ruta a la imagen o la imagen como arreglo NumPy.
        matriz (np.ndarray): Matriz de 16x9 con valores entre 0 y 1.

    Returns:
        np.ndarray: Imagen con celdas coloreadas.
    """
    if isinstance(imagen, str):
        img = cv2.imread(imagen)
    else:
        img = imagen.copy()

    alto, ancho, _ = img.shape
    celda_h = alto // 9         # Valor en pixeles de altura
    celda_w = ancho // 16       # Valor en pixeles de anchura

    overlay = img.copy()

    # Iterar sobre cada celda
    for fila in range(9):
        for col in range(16):
            valor = matriz[fila][col]
            if valor <= 0.42:
                color = (170, 232, 238)  # Verde (BGR)
            elif valor <= 0.55:
                color = (71, 99, 255)  # Amarillo
            else:
                color = (21, 21, 155)  # Rojo

            x1, y1 = col * celda_w, fila * celda_h
            x2, y2 = x1 + celda_w, y1 + celda_h
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    
    for x, y in fire_coordinates:
        color = (161, 0, 102)  # Verde (BGR)
        center = (x,y)
        radio = 20
        cv2.circle(overlay, center, radio, color, -1)

    # Superponer con transparencia (alpha blending)
    alpha = 0.3  # Transparencia
    output = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    return output

'''
if __name__ == "__main__":

    # Tu matriz desnormalizada
    Temperature_matrix = np.array([
        [135, 100,  40,  40,  80, 135,  30,  30,  60, 120, 130, 130, 130,  90,  60,  25],
        [130, 100, 140,  60, 135,  75, 100,  30,  25,  25,  25,  25,  25, 130, 130,  70],
        [130, 120,  35, 130, 130, 100, 100,  30, 135, 135, 105,  25,  25,  25,  25,  25],
        [ 40,  70, 130,  70,  25, 100,  70, 130, 135,  85,  70,  25,  25,  25,  25,  25],
        [130,  25, 100, 130, 100, 100, 130, 135, 100,  25, 100, 100, 100,  25,  25,  25],
        [135, 120, 100,  25,  25, 100,  25, 100,  25,  25,  95, 100, 100,  85,  25,  25],
        [ 85, 110,  85, 115, 135,  25,  25,  25,  25,  25,  25, 100, 135, 130,  25,  25],
        [ 25,  25,  25, 115, 130,  25,  25,  25, 100, 120, 120,  90, 135,  90, 135,  30],
        [ 30,  30,  30,  30,  30,  30,  30,  30,  30,  30,  30,  30,  90, 130,  90,  30]
    ]) #Recibirla del ESP32

    # Crear el heatmap
    plt.figure(figsize=(14, 6))
    sns.heatmap(Temperature_matrix, annot=True, fmt="d", cmap="YlOrRd", cbar=True)
    plt.title("Mapa de Calor - Matriz de Riesgo")
    plt.xlabel("Columna")
    plt.ylabel("Fila")
    plt.tight_layout()
    plt.show()

    risk_matrix = np.array([
        [0.967, 0.933, 0.333, 0.333, 0.6, 0.967, 0.267, 0.267, 0.467, 0.867, 0.933, 0.933, 0.933, 0.667, 0.467, 0.233],
        [0.933, 0.933, 1.0, 0.467, 0.967, 0.667, 0.733, 0.267, 0.533, 0.533, 0.533, 0.333, 0.233, 0.933, 0.933, 0.533],
        [0.933, 0.967, 0.3, 0.933, 0.933, 0.733, 0.733, 0.267, 0.967, 0.967, 0.967, 0.533, 0.233, 0.233, 0.233, 0.233],
        [0.333, 0.633, 0.933, 0.633, 0.233, 0.733, 0.533, 0.933, 0.967, 0.7, 0.633, 0.533, 0.233, 0.233, 0.233, 0.233],
        [0.933, 0.233, 0.733, 0.933, 0.733, 0.733, 0.933, 0.967, 0.833, 0.233, 0.733, 0.733, 0.733, 0.233, 0.233, 0.233],
        [0.967, 0.867, 0.733, 0.233, 0.233, 0.733, 0.233, 0.833, 0.233, 0.233, 0.7, 0.733, 0.733, 0.633, 0.233, 0.233],
        [0.633, 0.8, 0.633, 0.833, 0.967, 0.233, 0.233, 0.233, 0.233, 0.233, 0.233, 0.733, 0.967, 0.933, 0.233, 0.233],
        [0.233, 0.233, 0.233, 0.833, 0.93, 0.233, 0.233, 0.233, 0.733, 0.867, 0.867, 0.667, 0.967, 0.667, 0.967, 0.267],
        [0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.267, 0.667, 0.933, 0.667, 0.267]
    ]) #necesito que me llegue esta matriz

    imagen_resultado = colorear_celdas(r"firetest11.jpg", risk_matrix) #ultima imagen adquitida de la camara optica
    cv2.imshow("Resultado", imagen_resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #segunda iteracion
    kernel_matrix = kernel(risk_matrix)
    kernel_resultado = colorear_celdas(r"firetest11.jpg", kernel_matrix)
    cv2.imshow("Resultado con Kernel", kernel_resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''