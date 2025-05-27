from fire_detection import detect_fire
from mesh import mesh_segmentation2
from display import NNI_kernel, colorear_celdas, crop_optical_to_thermal
import cv2
from ultralytics import YOLO
from coordinates import pixel_to_gps
from geojson_gen import generar_geojson
from flask import Flask, render_template, send_from_directory
from coordinates import get_coordinates
import matplotlib.pyplot as plt
import numpy as np
import os
from config import FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL, FOV_TERMICA_HORIZONTAL, FOV_TERMICA_VERTICAL ,THERMAL_WIDTH, THERMAL_HEIGHT

# Inicialización del proceso de detección incendio a través de cámara óptica y térmica YOLOv8
model = YOLO(r"fire_s.pt")
fire_img, cx, cy, fire_coordinates,hotspots,t_amb,thermal_matrix = detect_fire(model) #imagen optica, centroides de incendios
#drone_lat,drone_lon,drone_height = get_coordinates() # Coordenadas del drone
drone_lat,drone_lon,drone_height = 34.19135792863, -118.13209036525, 50 # para el ejemplo

img_height, img_width = fire_img.shape[:2]
print(f"Imagen óptica capturada: {img_height}x{img_width} píxeles")

fire_location = []
for cy,cx in fire_coordinates:
    lat, lon = pixel_to_gps(cx, cy, img_height, img_width, drone_height, drone_lat, drone_lon, FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL)
    fire_location.append((lat, lon))
fire_location = np.array(fire_location)

cv2.imshow("Imagen Óptica Capturada", fire_img)
cv2.waitKey(5000)
cv2.destroyAllWindows() 

print('_______________________hotspots location_____________________________')
hotspot_location = []
for cy, cx in hotspots:
    lat,lon = pixel_to_gps(cx,cy,THERMAL_WIDTH,THERMAL_HEIGHT,drone_height,drone_lat,drone_lon,FOV_TERMICA_HORIZONTAL, FOV_TERMICA_VERTICAL)
    hotspot_location.append((lat,lon))
    print(f"Hotspot: Latitud: {lat}, Longitud: {lon}")
hotspot_location = np.array(hotspot_location)

# Coordenadas del incendio -> Input para EQUIPO 2
print('__________________Coordenadas EQUIPO 2_____________________________')
lat_fire, lon_fire = pixel_to_gps(cx,cy,img_height,img_width,drone_height,drone_lat,drone_lon, FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL)
print(f"🔥🔥Incendio: Latitud: {lat_fire}, Longitud: {lon_fire}")

# Análisis de Mallado
rsk, coord_list, fire_cells = mesh_segmentation2(fire_img, drone_lat, drone_lon, drone_height,hotspots,hotspot_location,t_amb, thermal_matrix, fire_location)

print(f'fire cells {fire_cells}')
height, width = rsk.shape

for cy, cx in fire_cells:
    # Centro
    rsk[cy, cx] = 1
    coord_list[cy, cx, 2] = 1
    # Arriba
    if 0 <= cy+1 < height and 0 <= cx < width:
        rsk[cy+1, cx] = 0.65
        coord_list[cy+1, cx, 2] = 0.65
    # Derecha
    if 0 <= cy < height and 0 <= cx+1 < width:
        rsk[cy, cx+1] = 0.65
        coord_list[cy, cx+1, 2] = 0.65
    # Abajo
    if 0 <= cy-1 < height and 0 <= cx < width:
        rsk[cy-1, cx] = 0.65
        coord_list[cy-1, cx, 2] = 0.65
    # Izquierda
    if 0 <= cy < height and 0 <= cx-1 < width:
        rsk[cy, cx-1] = 0.65
        coord_list[cy, cx-1, 2] = 0.65

rsk_image = colorear_celdas(fire_img, rsk,fire_coordinates)

cv2.imshow("Fire risk output", rsk_image)
cv2.waitKey(5000)
cv2.destroyAllWindows
# Nearest neighbor interpolation
rsk_interpolated = NNI_kernel(rsk)
# Visualización del Análisis de Riesgo
try: 
    rsk_image = colorear_celdas(fire_img, rsk_interpolated, fire_coordinates)
    cv2.imshow("Fire risk output kernel", rsk_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows
except Exception as e:
    print(f'Failed to generate 2D visualization: {e}')


# Mostrar heatmap
plt.figure(figsize=(10, 6))
plt.imshow(thermal_matrix, cmap='inferno')
plt.colorbar(label="Temperatura (°C)")
plt.title("Mapa de calor con hotspots")
# Marcar hotspots
for y, x in hotspots:
    plt.plot(x, y, 'bo', markersize=6, label="Hotspot")
plt.tight_layout()
plt.show()

# Archivo GeoJSON
generar_geojson(coord_list)

# Aplicación mostrando mapa 2D y 3D
app = Flask(__name__, template_folder='templates')

@app.route("/")
def leaflet():
    return render_template("leaflet.html")

@app.route("/3d")
def mapbox3d():
    return render_template("mapbox3d.html")

@app.route("/riesgo.geojson")
def geojson():
    print("🛰️ Sirviendo:", os.path.abspath("riesgo.geojson"))
    return send_from_directory(".", "riesgo.geojson")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)