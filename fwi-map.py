import numpy
import math
import ee
import geemap
import webbrowser
import datetime

def risk_score(ndvi,slope,thermal):

    ndviWeight = 0.6
    slopeWeight = 0.4
    thermalWeight = 0.1

    #Conversión a °C en caso de ser necesario
    thermal = (thermal*0.2) - 273.15

    score = (ndvi*ndviWeight) + (slope*slopeWeight) + (thermal*thermalWeight)
    return score

def visualizar_riesgo(ndvi,slope,lst_image):
    ndviWeight = 0.3
    slopeWeight = 0.4
    thermalWeight = 0.5

    #Cálculo del índice de riesgo como imagen en EE
    riesgo_img = ndvi.multiply(ndviWeight).add(slope.multiply(slopeWeight)).add(lst_image.multiply(thermalWeight)).rename("Riesgo")
    return riesgo_img

def spread_rate(deltaH, windSpeed, slopeAng, ignitionHeat):

    #Asegurarse de que las variables estén en las siguientes unidades:
    # Calor liberado por unidad -> deltaH -> kJ/m^2
    # Velocidad del viento -> windSpeed -> m/s
    # Ángulo de la pendiente -> slopeAng -> radianes
    # Calor requerido para encender la sig. unidad -> ignitionHeat -> kJ/m^2

    #Fórmula de tasa de expansión
    # R = dH*W*cos(theta)/Q
    rate = (deltaH * windSpeed * math.cos(slopeAng))/ignitionHeat   
    return rate

# Autenticación e inicialización
ee.Authenticate()
ee.Initialize(project='light-sunup-288723')  # Usa tu ID si es diferente

#Selección de coordenadas de interés
# lat = float(input("COORDENADAS DE LATITUD: "))
# long = float(input("COORDENADAS DE LONGITUD: "))

lat = float(24.878499)
long = float(-99.740625)

#Creación de punto geométrico
punto = ee.Geometry.Point([long,lat])
area = punto.buffer(5000)

#Definición de fecha
hoy = datetime.date.today()
#inicio = ee.Date(str(hoy - datetime.timedelta(days=7)))
#fin = ee.Date(str(hoy))
#Debido a que algunas bases de datos tienen retraso de unas semanas, se van a usar las siguientes fechas
inicio = '2025-03-15'
fin = '2025-04-15'

#Importar datos de NDVI
# MODIS/061/MOD13Q1 --> Base de datos de NDVI con cadencia de 16 días
#ndvi = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(punto) \
#    .filterDate('2024-01-01', '2025-12-31') \
#    .select('NDVI') \
#    .sort('system:time_start', False) \
#    .first().clip(area)
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate('2024-01-01', '2025-12-31').select('NDVI').sort('system:time_start',False)\
.mean().clip(area)

#Importar datos de Temperatura de Superficie Terrestre

modis = ee.ImageCollection("MODIS/061/MOD11A1") \
    .filterBounds(punto) \
    .filterDate('2024-01-01', '2025-12-31') \
    .sort('system:time_start', False) \
    .first()
lst_image = modis.select('LST_Day_1km').multiply(0.02).subtract(273.15).rename('Temperatura_C').clip(area)

#MODIS/061/MOD11A2 --> Base de dasos de Temperatura de Superficie Terrestre con cadencia de 8 días
#lst_collection = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(inicio,fin).select('LST_Day_1km')

#print('Número de imágenes LST:', lst_collection.size().getInfo())
#Promedio de lst y conversión a °C
#lst_image = lst_collection.mean().multiply(0.02).subtract(273.15).rename('Temperatura_C').clip(area)

#Importar datos de Velocidad del Viento

#NOAA/GFS0P25 --> GFS: Global Forecast System Predicted Atmosphere Data con cadencia de 6 horas
wind_collection = ee.ImageCollection('NOAA/GFS0P25').filterDate(inicio,fin)\
    .sort('system:time_start',False).select(['u_component_of_wind_10m_above_ground','v_component_of_wind_10m_above_ground'])

#Media de componentes U & V
meanU = wind_collection.select('u_component_of_wind_10m_above_ground').mean()
meanV = wind_collection.select('v_component_of_wind_10m_above_ground').mean()

#Cálculo de magnitud del viendo y renombre de variable
wind_speed = meanU.hypot(meanV).rename('WindSpeed_m/s').clip(area)

#Importar datos de Pendiente
dem = ee.Image('USGS/SRTMGL1_003')
slope = ee.Terrain.slope(dem).rename('Pendiente_Angulo').clip(area)

#Combinamos en una sola imagen
imagen_completa = ndvi.rename('NDVI').addBands(lst_image).addBands(wind_speed).addBands(slope)

#Muestreo de datos dentro del Buffer
muestreo = imagen_completa.sample(region=area,scale=100,numPixels=100,geometries=True)

#Lo Convertimos a un diccionario
datos = muestreo.getInfo()

for feature in datos['features']:
    props = feature['properties']
    coords = feature['geometry']['coordinates']

    valor_ndvi = props['NDVI']
    valor_wind = props['WindSpeed_m/s']
    valor_temp = props['Temperatura_C']
    valor_pendiente = props['Pendiente_Angulo']

    #Conversión a radianes del valor de la pendiente
    valor_pendiente_rad = math.radians(valor_pendiente)

    #Cálculo de índice de riesgo
    riesgo_estimado = risk_score(valor_ndvi,valor_pendiente_rad,valor_temp)
    riesgo_mapa = visualizar_riesgo(ndvi,slope,lst_image)
    print(f"Coordenadas: {coords}")
    print(f"NDVI: {valor_ndvi}, Temp: {valor_temp} °C, Viento: {valor_wind} m/s, Pendiente: {valor_pendiente}°")
    print(f"Índice de riesgo: {riesgo_estimado:.2f}")

#Se usó Geemap para crear el mapa y luego agregar los puntos 
#en base a su puntuación calculada de riesgo
mapa_de_calor = geemap.Map(center=[lat,long], zoom = 15)

#Agregamos el riesgo estimado al mapa recién creado
riesgo_vis = {'min': 0,'max': 5000,'palette': ['00ff00', 'ffff00', 'ff9900', 'ff0000']}  # Verde -> Rojo

mapa_de_calor.addLayer(riesgo_mapa,riesgo_vis, "Índice de Riesgo de Incendio", opacity=0.85)
mapa_de_calor.addLayer(area, {},'Área analizada')
mapa_de_calor.addLayer(punto,{'color':'blue'},'Punto central del incendio')

mapa_de_calor.to_html('fwi-heatmap.html')
webbrowser.open('fwi-heatmap.html')
#mapa_de_calor.add_colorbar(vis_params=riesgo_vis, label='Índice de Riesgo')



# Save the map as HTML
html_file = "fwi-heatmap.html"
mapa_de_calor.to_html(html_file)



# Define the color bar HTML
colorbar_html = """
<style>
    .colorbar-container {
        position: absolute;
        bottom: 10px;
        right: 10px;
        width: 300px;
        padding: 5px;
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid black;
        z-index: 1000;
    }
    .colorbar {
        width: 100%;
        height: 30px;
        background: linear-gradient(to right, #00ff00, #ffff00, #ff9900, #ff0000);
    }
    .labels {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-top: 3px;
    }
</style>
<div class="colorbar-container">
    <div class="colorbar"></div>
    <div class="labels">
        <span>Low Risk</span>
        <span>Medium</span>
        <span>High</span>
        <span>Extreme</span>
    </div>
</div>
"""



# Append color bar to the generated HTML file
with open(html_file, "r+", encoding="utf-8") as file:
    content = file.read()
    if "</body>" in content:
        content = content.replace("</body>", colorbar_html + "</body>")
    file.seek(0)
    file.write(content)

slider_html = """
<script>
    let map;  // Referencia global
    let bufferCircle;

    function waitForMap() {
        // Esperar a que se cargue el objeto "map_0" que usa geemap
        if (typeof window.map_0 !== 'undefined') {
            map = window.map_0;

            // Punto central
            const lat = %f;
            const lng = %f;

            // Crear círculo inicial
            bufferCircle = L.circle([lat, lng], {radius: 300, color: 'blue'}).addTo(map);

            // Crear slider
            const container = document.createElement('div');
            container.innerHTML = `
                <div style="position: absolute; top: 10px; left: 10px; z-index: 1000; background: white; padding: 10px; border: 1px solid black;">
                    <label>Radio área analizada (m): <span id="radius-val">300</span></label><br>
                    <input type="range" min="100" max="500" value="300" id="radius-slider" />
                </div>
            `;
            document.body.appendChild(container);

            // Listener del slider
            document.getElementById('radius-slider').addEventListener('input', function(e) {
                const newRadius = parseInt(e.target.value);
                document.getElementById('radius-val').textContent = newRadius;

                if (bufferCircle) {
                    bufferCircle.setRadius(newRadius);
                }
            });
        } else {
            // Esperar y volver a intentar
            setTimeout(waitForMap, 500);
        }
    }

    waitForMap();
</script>
""" % (lat, long)



# Insertarlo al HTML exportado
with open(html_file, "r+", encoding="utf-8") as file:
    content = file.read()
    if "</body>" in content:
        content = content.replace("</body>", slider_html + "</body>")
    file.seek(0)
    file.write(content)

print("Slider de control dinámico de radio añadido.")


# Open the modified HTML file
webbrowser.open(html_file)

print(f"Color bar added to {html_file}")