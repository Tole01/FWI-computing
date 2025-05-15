from fire_detection import detect_fire
from mesh import mesh_segmentation
from display import NNI_kernel, colorear_celdas
import cv2
from ultralytics import YOLO
from coordinates import pixel_to_gps
from geojson_gen import generar_geojson
from flask import Flask, render_template, send_from_directory
from coordinates import get_coordinates
from temperature import get_temp_matrix, normalize_temperature
import seaborn as sns
import matplotlib.pyplot as plt
from config import FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL, FOV_TERMICA_HORIZONTAL, FOV_TERMICA_VERTICAL

# Inicialización del proceso de detección incendio a través de cámara óptica y térmica YOLOv8
model = YOLO(r"fire_s.pt")
fire_img, cx, cy, fire_coordinates = detect_fire(model) 
print(fire_coordinates)

thermal_matrix = get_temp_matrix() # Obtener temperatura de cada coordenada (en pixel)
normalized_matrix = normalize_temperature(thermal_matrix) # Normalizar la matriz de temperatura
print(normalized_matrix)

cv2.imshow("Imagen Óptica Capturada", fire_img)
cv2.waitKey(5000)
cv2.destroyAllWindows()

# Coordenadas que se obtendran de ardupilot
drone_lat,drone_lon,drone_height = get_coordinates() #el de verdad
#drone_lat,drone_lon,drone_height = 25.64933, -100.28890, 30 #para el ejemplo

# Coordenadas del incendio -> Input para EQUIPO 2
lat_fire, lon_fire = pixel_to_gps(cx,cy,1920,1080,drone_height,drone_lat,drone_lon, FOV_OPTICA_HORIZONTAL, FOV_OPTICA_VERTICAL)

# Análisis de Mallado
rsk, coord_list = mesh_segmentation(fire_img, thermal_matrix, drone_lat, drone_lon, drone_height)
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


plt.figure(figsize=(14, 6))
sns.heatmap(thermal_matrix, annot=True, fmt="d", cmap="YlOrRd", cbar=True)
plt.title("Mapa de Calor - Matriz de Riesgo")
plt.xlabel("Columna")
plt.ylabel("Fila")
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