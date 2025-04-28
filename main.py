from Api_file import get_weather_data
from Api_file import get_ndvi
from Api_file import get_slope
from computingFWI import calculate_fwi
from coordinates import get_coordinates
from coordinates import pixel_to_gps
from risk_score import calculate_risk_score
from deteccion_incendio import detect_fire
#from mesh_analysis import mesh_segmentation as seg
import cv2


fire = 0 # Variable para indicar si hay fuego o no
fire_img,cx,cy = detect_fire(fire) # Loop que busca fuego en las dos camaras, guarda la imagen optica con fuego
#seg(fire_img)
# cv2.imshow("Imagen Óptica Capturada", fire_img)
# Generar análisis de malla a partir de imagen

# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Coordenadas que se obtendran de ardupilot
drone_lat,drone_lon,drone_height = 25.618611, -100.356977,35 #get_coordinates()
# Coordenadas de la imagen transformadas a GPS
lat, lon = pixel_to_gps(cx,cy,1920,1080,drone_height,drone_lat,drone_lon,160,90)

#calorimetria
T = 30 # Temperatura de la coordenada a evaluar
T_norm = (T+10)/(140+10) # Normalización de la temperatura máxima

# Obtener datos del clima
row = get_weather_data(lat, lon)

# Calcular FWI
indices = calculate_fwi(row)

#Calcular NDVI
ndvi = get_ndvi(lat,lon)

#Calcular slope
slope = get_slope(lat, lon)

# Mostrar resultados
print("\n📊 Resultados FWI:")
for key, value in indices.items():
    print(f"{key}: {value:.2f}")

print("\n NDVI:")
print("\n",ndvi)

print("\n Slope:")
print("\n",slope)

print("\nlat: ", lat)
print("\nlon: ", lon)

#calcular riesgo de incendio
risk = calculate_risk_score(indices, ndvi, slope, T_norm)
print(f"\n🔥 Risk Score: {risk:.2f}")