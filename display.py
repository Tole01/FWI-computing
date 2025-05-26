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
        color = (161, 0, 102)  # (BGR)
        center = (x,y)
        radio = 20
        cv2.circle(overlay, center, radio, color, -1)

    # Superponer con transparencia (alpha blending)
    alpha = 0.3  # Transparencia
    output = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    return output

import cv2
import numpy as np

def crop_optical_to_thermal(
    optical_img,
    optical_width_px, optical_height_px,
    optical_fov_h, optical_fov_v,
    drone_height_m,
    thermal_width_px, thermal_height_px,
    thermal_fov_h, thermal_fov_v
):
    """
    Recorta la imagen óptica para que coincida con el área visible de la cámara térmica.

    Parámetros:
    - optical_img: imagen RGB (np.array)
    - optical_width_px: ancho en píxeles de la imagen óptica
    - optical_height_px: alto en píxeles de la imagen óptica
    - optical_fov_h: FOV horizontal óptico en grados
    - optical_fov_v: FOV vertical óptico en grados
    - drone_height_m: altura del dron en metros
    - thermal_width_px: resolución horizontal de la imagen térmica
    - thermal_height_px: resolución vertical de la imagen térmica
    - thermal_fov_h: FOV horizontal térmico en grados
    - thermal_fov_v: FOV vertical térmico en grados

    Retorna:
    - Imagen óptica recortada y redimensionada al tamaño de la imagen térmica.
    """

    # Calcular el tamaño del área cubierta por la cámara óptica y térmica en metros
    optical_width_m = 2 * drone_height_m * np.tan(np.radians(optical_fov_h / 2))
    optical_height_m = 2 * drone_height_m * np.tan(np.radians(optical_fov_v / 2))

    thermal_width_m = 2 * drone_height_m * np.tan(np.radians(thermal_fov_h / 2))
    thermal_height_m = 2 * drone_height_m * np.tan(np.radians(thermal_fov_v / 2))

    # Calcular cuántos metros cubre cada píxel de la imagen óptica
    optical_m_per_px_x = optical_width_m / optical_width_px
    optical_m_per_px_y = optical_height_m / optical_height_px

    # Calcular tamaño del recorte en píxeles (equivalente al área térmica)
    crop_width_px = int(thermal_width_m / optical_m_per_px_x)
    crop_height_px = int(thermal_height_m / optical_m_per_px_y)

    # Centro del recorte
    x_center = optical_width_px // 2
    y_center = optical_height_px // 2

    x_start = max(x_center - crop_width_px // 2, 0)
    y_start = max(y_center - crop_height_px // 2, 0)

    x_end = min(x_start + crop_width_px, optical_width_px)
    y_end = min(y_start + crop_height_px, optical_height_px)

    cropped_img = optical_img[y_start:y_end, x_start:x_end]

    # Verificación y redimensionamiento
    if cropped_img.size == 0:
        raise ValueError("Error: recorte vacío. Verifica los parámetros de entrada.")
    
    resized_img = cv2.resize(cropped_img, (thermal_width_px, thermal_height_px))
    return resized_img