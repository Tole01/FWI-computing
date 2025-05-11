from deteccion_incendio import detect_fire
from mesh import mesh_segmentation
from display import NNI_kernel, colorear_celdas
import cv2
from coordinates import pixel_to_gps
from geojson_gen import generar_geojson
from flask import Flask, render_template, send_from_directory
from coordinates import get_coordinates

fire = 0 # Variable para indicar si hay fuego o no
fire_img,cx,cy,fire_coordinates = detect_fire(fire) # Loop que busca fuego en las dos camaras, guarda la imagen optica con fuego
print(fire_coordinates)
cv2.imshow("Imagen Óptica Capturada", fire_img)
cv2.waitKey(5000)
cv2.destroyAllWindows()

# Coordenadas que se obtendran de ardupilot
drone_lat,drone_lon,drone_height = get_coordinates() #el de verdad
drone_lat,drone_lon,drone_height = 34.191763, -118.133088, 30 #para el ejemplo

# Coordenadas del incendio -> Input para EQUIPO 2
lat_fire, lon_fire = pixel_to_gps(cx,cy,1920,1080,drone_height,drone_lat,drone_lon,157.1,140.4)

# Obtener temperatura de cada coordenada (en pixel) / Sustituir por termografía de FLIR Lepton
#thermal_matrix = get_thermal_image()
           
# Análisis de Mallado
rsk, coord_list = mesh_segmentation(fire_img, drone_lat, drone_lon, drone_height)
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

# Archivo GeoJSON
generar_geojson(coord_list, rsk)

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