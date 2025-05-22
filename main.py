from fire_detection import detect_fire
from mesh import mesh_segmentation2
from display import NNI_kernel, colorear_celdas
import cv2
import numpy as np
from ultralytics import YOLO
from coordinates import pixel_to_gps
from geojson_gen import generar_geojson
from flask import Flask, render_template, send_from_directory
from coordinates import get_coordinates
from temperature import get_temp_matrix, detectar_hotspots
import seaborn as sns
import matplotlib.pyplot as plt
from config import FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL, FOV_TERMICA_HORIZONTAL, FOV_TERMICA_VERTICAL

# Inicialización del proceso de detección incendio a través de cámara óptica y térmica YOLOv8
model = YOLO(r"fire_s.pt")
fire_img, cx, cy, fire_coordinates = detect_fire(model) #imagen optica, centroides de incendios
thermal_matrix = get_temp_matrix() # Obtener temperatura 120X160
drone_lat,drone_lon,drone_height = get_coordinates() # Coordenadas del drone

print(fire_coordinates)

cv2.imshow("Imagen Óptica Capturada", fire_img)
cv2.waitKey(5000)
cv2.destroyAllWindows()

#drone_lat,drone_lon,drone_height = 25.64933, -100.28890, 30 #para el ejemplo

hotspots, t_amb = detectar_hotspots(thermal_matrix)
hotspot_location = []
for cx, cy in hotspots:
    lat,lon = pixel_to_gps(cx,cy,160,120,drone_height,drone_lat,drone_lon,FOV_TERMICA_HORIZONTAL, FOV_TERMICA_VERTICAL)
    hotspot_location.append((lat,lon))
    print(f"Hotspot: Latitud: {lat}, Longitud: {lon}")

# Coordenadas del incendio -> Input para EQUIPO 2
lat_fire, lon_fire = pixel_to_gps(cx,cy,1920,1080,drone_height,drone_lat,drone_lon, FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL)

# Análisis de Mallado
rsk, coord_list = mesh_segmentation2(fire_img, drone_lat, drone_lon, drone_height,hotspots,hotspot_location,t_amb)
rsk_image = colorear_celdas(fire_img, rsk,fire_coordinates)
cv2.imshow("Fire risk output", rsk_image)
cv2.waitKey(0)
cv2.destroyAllWindows
# Nearest neighbor interpolation
rsk_interpolated = NNI_kernel(rsk)
# Visualización del Análisis de Riesgo
try: 
    rsk_image = colorear_celdas(fire_img, rsk_interpolated)
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
    return send_from_directory(".", "riesgo.geojson")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)