from pymavlink import mavutil
from config import COM_ANTENA
import numpy as np
import math

def get_coordinates():
    """
    Se conecta al dron vía MAVLink y retorna la latitud y longitud actuales.
    Retorna:
        (lat, lon, alt): coordenadas GPS en grados decimales
    """
    master = mavutil.mavlink_connection(COM_ANTENA,baud = 115200) #Cambiar el puerto en caso de ser necesario

    print("Esperando mensajes del dron...")
    try:
        while True:
            # Recibir cualquier mensaje
            msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if msg:
                # Extraer latitud, longitud y altura
                lat = msg.lat / 1e7        # Convertir de 10^7 grados a grados decimales
                lon = msg.lon / 1e7
                alt = msg.alt / 1000.0     # Convertir de milímetros a metros

                # Imprimir las coordenadas
                print(f"📍 Latitud: {lat:.6f}, Longitud: {lon:.6f}, Altura: {alt:.2f} m")
                return lat, lon, alt

    except KeyboardInterrupt:
        print("Conexión terminada.")

def pixel_to_gps(pixel_x, pixel_y, img_width, img_height, height_m, drone_lat, drone_lon, fov_x_deg = 157, fov_y_deg = 140):
    """
    Transforma coordenadas de píxeles a coordenadas GPS.

    Args:
        pixel_x (int): Coordenada x del píxel en la imagen.
        pixel_y (int): Coordenada y del píxel en la imagen.
        img_width (int): Ancho de la imagen en píxeles.
        img_height (int): Alto de la imagen en píxeles.
        height_m (float): Altura del dron sobre el suelo en metros.
        drone_lat (float): Latitud actual del dron en grados decimales.
        drone_lon (float): Longitud actual del dron en grados decimales.
        fov_x_deg (float): Campo de visión horizontal de la cámara en grados. Por defecto 157°.
        fov_y_deg (float): Campo de visión vertical de la cámara en grados. Por defecto 140°.

    Returns:
        (lat, lon): Tuple[float, float] con las coordenadas GPS calculadas en grados decimales.
    """
    # Convert FOV to radians
    fov_x = math.radians(fov_x_deg)
    fov_y = math.radians(fov_y_deg)

    # Calculate the real-world width and height covered by the image (meters)
    ground_width = 2 * height_m * math.tan(fov_x / 2)
    ground_height = 2 * height_m * math.tan(fov_y / 2)

    # Calculate meters per pixel
    meters_per_pixel_x = ground_width / img_width
    meters_per_pixel_y = ground_height / img_height

    # Pixel displacement from image center
    dx_pixels = pixel_x - img_width / 2
    dy_pixels = pixel_y - img_height / 2

    # Displacement in meters
    dx_meters = dx_pixels * meters_per_pixel_x
    dy_meters = dy_pixels * meters_per_pixel_y

    # Convert meters to degrees
    delta_lat = -dy_meters / 111111  # Latitude: negative because y increases downward
    delta_lon = dx_meters / (111111 * math.cos(math.radians(drone_lat)))

    # Final GPS coordinates
    new_lat = drone_lat + delta_lat
    new_lon = drone_lon + delta_lon

    # Rounds up to a precision of 5 decimal places (1.11 m)
    return round(new_lat, 6), round(new_lon, 6)


def pixel_to_gps_vectorized(y_pixels, x_pixels, img_width, img_height, d_height, d_lat, d_lon, fov_x_deg = 157, fov_y_deg = 140):
    """
    Converts y, x pixel coordinates arrays into GPS coordinates. 

    Input: 
        y_pixels -> y pixel coordinates (Numpy Array)
        x_pixels -> x pixel coordinates (Numpy Array)
        img_width -> image resolution / x axis (int)
        img_height -> image resolution / y axis (int)
        d_height -> Drone height (int)
        d_lat -> Drone latitute coordinate (float)
        d_lon -> Drone longitude coordinate (float)

    Output:
        Tuple of 2-D Numpy Arrays containing the (latitude, longitude) GPS coordinates
    """


    # Convert FOV to radians
    fov_x = np.radians(fov_x_deg)
    fov_y = np.radians(fov_y_deg)

    # Calculate the real-world width and height covered by the image (meters)
    ground_width = 2 * d_height * np.tan(fov_x / 2)
    ground_height = 2 * d_height * np.tan(fov_y / 2)

    # Calculate meters per pixel
    meters_per_pixel_x = ground_width / img_width
    meters_per_pixel_y = ground_height / img_height

    # Pixels displacement from image center
    dx_pixels = x_pixels - img_width / 2
    dy_pixels = y_pixels - img_height / 2

    # Displacement in meters
    dx_meters = dx_pixels * meters_per_pixel_x
    dy_meters = dy_pixels * meters_per_pixel_y

    # Convert meters to degrees
    delta_lats = -dy_meters / 111111  # Latitude: negative because y increases downward
    delta_lons = dx_meters / (111111 * np.cos(np.radians(d_lat)))

    # Final GPS coordinates / Rounded to 6 decimal places -> Precision of 1.11 m
    new_lats = np.round( (d_lat + delta_lats), 6)
    new_lons = np.round( (d_lon + delta_lons), 6)

    return new_lats, new_lons

def hotspot_en_area(hotspots, lat_sup_izq, lon_sup_izq, lat_inf_der, lon_inf_der):
    """
    Verifica si algún hotspot está dentro del rectángulo definido por dos esquinas GPS.
    """
    lat_min = min(lat_sup_izq, lat_inf_der)
    lat_max = max(lat_sup_izq, lat_inf_der)
    lon_min = min(lon_sup_izq, lon_inf_der)
    lon_max = max(lon_sup_izq, lon_inf_der)

    encontrados = []
    for i,(lat, lon) in enumerate (hotspots):
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            encontrados.append(i,(lat, lon))

    return encontrados  # Lista de hotspots que sí están dentro del área


