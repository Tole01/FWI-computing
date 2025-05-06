from Api_file import get_weather_data
from Api_file import get_ndvi
from Api_file import get_slope
from computingFWI import calculate_fwi
from coordinates import get_coordinates
from coordinates import pixel_to_gps
from risk_score import calculate_risk_score
from deteccion_incendio import detect_fire
import cv2

fire = 0 # Variable para indicar si hay fuego o no
fire_img,cx,cy = detect_fire(fire) # Loop que busca fuego en las dos camaras, guarda la imagen optica con fuego

cv2.imshow("Imagen Óptica Capturada", fire_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Coordenadas que se obtendran de ardupilot
drone_lat,drone_lon,drone_height = 34.191763, -118.133088, 30 #get_coordinates()

# Coordenadas del centroide del fuego detectado 
lat, lon = pixel_to_gps(cx,cy,1920,1080,drone_height,drone_lat,drone_lon,157.1,140.4)

# Coordenadas del incendio -> Input para EQUIPO 2
lat_fire, lon_fire = pixel_to_gps(cx,cy,1920,1080,drone_height,drone_lat,drone_lon,157.1,140.4)

#obtener temperatura de cada coordenada (en pixel)
temperature_matrix = [[100,80,40,40,80,60,30,30,30,95,90,100,100,25,25,25],
                      [130,100,140,60,120,30,30,30,25,25,25,25,25,80,60,25],
                      [100,120,35,100,80,80,30,30,90,30,80,25,25,25,25,25],
                      [40,25,130,25,25,25,25,25,90,80,25,25,25,25,25,25],
                      [100,25,25,130,25,25,100,25,25,25,95,80,25,25,25,25],
                      [90,25,70,25,25,25,25,100,25,25,95,25,25,25,25,25],
                      [25,110,25,25,60,25,25,25,25,25,25,100,90,25,25,25],
                      [25,25,25,70,80,25,25,25,100,30,30,90,30,30,30,30],
                      [30,30,30,30,30,30,30,30,30,30,30,30,30,70,30,30],             
] # Matriz de temperaturas de ejemplo

# Análisis de Mallado

# Visualización del Análisis de Riesgo

# Comunicación con la nube / Aplicación WEB
