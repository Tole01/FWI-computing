import numpy
import math
import ee
import geemap
import webbrowser
import datetime

def risk_score(ndvi,slope,thermal):

    #Para sacar el peso individual de cada variable se sumaron sus IV's resultantes del análisis con el script de woe-data2.py
    # IV de NDVI = 3.8987
    # IV de Temperatura = 2.3786
    # IV de Pendiente = 1.3073
    # 3.8987 + 2.3786 + 1.3073 = 7.5846
    # De ahí, se sacó su peso relativo dividiendo cada IV entre el IV resultante 
    # ndviWeight = 3.8987/7.5846
    # slopeWeight = 1.3073/7.5846
    # thermalWeight = 2.3786/7.5846
    # Teniendo así los siguientes pesos   
    ndviWeight = 0.5142
    slopeWeight = 0.1722
    thermalWeight = 0.3136

    #Conversión a °C en caso de ser necesario
    thermal = (thermal*0.2) - 273.15

    score = (ndvi*ndviWeight) + (slope*slopeWeight) + (thermal*thermalWeight)
    return score

def visualizar_riesgo(ndvi,slope,lst_image):
    ndviWeight = 0.5142
    slopeWeight = 0.1722
    thermalWeight = 0.3136
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
#Rancho en Montemorelos
#lat = float(24.878499)
#long = float(-99.740625)

#Pasadena, Los Ángeles
#lat = float(34.156113)
#long = float(-118.131943)

#Pasadena, California
lat = float(34.21113114902449) 
long = float(-118.1138591514406)

#Creación de punto geométrico
punto = ee.Geometry.Point([long,lat])
area = punto.buffer(10000)

#Definición de fecha
hoy = datetime.date.today()
#Debido a que algunas bases de datos tienen retraso de unas semanas, se van a usar las siguientes fechas
inicio = '2024-01-1'
fin = '2024-01-31'

#Importar datos de NDVI
# MODIS/061/MOD13Q1 --> Base de datos de NDVI con cadencia de 16 días
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate(inicio, fin).select('NDVI').sort('system:time_start',False).mean().clip(area)

#Importar datos de Temperatura de Superficie Terrestre
#MODIS/061/MOD11A1 --> Base de dasos de Temperatura de Superficie Terrestre con cadencia de 8 días
modis = ee.ImageCollection("MODIS/061/MOD11A1") \
    .filterBounds(punto) \
    .filterDate(inicio, fin) \
    .sort('system:time_start', False) \
    .first()
#Promedio de lst y conversión a °C
lst_image = modis.select('LST_Day_1km').multiply(0.02).subtract(273.15).rename('Temperatura_C').clip(area)

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

#Importar datos de Incendios Históricos o de Áreas quemadas
burnDateStart = '2025-01-01'
burnDateEnd = '2025-01-31'
burntZones = ee.ImageCollection("MODIS/061/MCD64A1").filterDate(burnDateStart,burnDateEnd).select("BurnDate")

#Combinamos en una sola imagen
imagen_completa = ndvi.rename('NDVI').addBands(lst_image).addBands(wind_speed).addBands(slope)

#Muestreo de datos dentro del Buffer
# (Después de crear imagen_completa)
muestreo = imagen_completa.sample(region=area, scale=100, numPixels=100, geometries=True)
datos = muestreo.getInfo()

# Validamos si hay datos antes de continuar
if not datos['features']:
    print("No se encontraron datos para las coordenadas y fechas especificadas.")
    riesgo_mapa = None
else:
    riesgo_mapa = visualizar_riesgo(ndvi, slope, lst_image)
    for feature in datos['features']:
        props = feature['properties']
        coords = feature['geometry']['coordinates']

        valor_ndvi = props['NDVI']
        valor_wind = props['WindSpeed_m/s']
        valor_temp = props['Temperatura_C']
        valor_pendiente = props['Pendiente_Angulo']

        valor_pendiente_rad = math.radians(valor_pendiente)

        riesgo_estimado = risk_score(valor_ndvi, valor_pendiente_rad, valor_temp)

        if riesgo_estimado <= 1000:
            nivel = "Muy Bajo"
        elif riesgo_estimado <= 1800:
            nivel = "Bajo"
        elif riesgo_estimado <= 2200:
            nivel = "Moderado"
        elif riesgo_estimado <= 2600:
            nivel = "Alto"
        elif riesgo_estimado <= 3000:
            nivel = "Muy Alto"
        else:
            nivel = "Extremo"

        print(f"Índice de riesgo: {riesgo_estimado:.2f} ({nivel})")
        print(f"Coordenadas: {coords}")
        print(f"NDVI: {valor_ndvi}, Temp: {valor_temp} °C, Viento: {valor_wind} m/s, Pendiente: {valor_pendiente}°")
        print(f"Índice de riesgo: {riesgo_estimado:.2f}")

#Se usó Geemap para crear el mapa y luego agregar los puntos 
#en base a su puntuación calculada de riesgo
mapa_de_calor = geemap.Map(center=[lat,long], zoom = 10)

#Agregamos el riesgo estimado al mapa recién creado
riesgo_vis = {'min': 900,'max': 3300,'palette': ['00ff00', '66ff00', '99ff00', 'ccff00','ffff00','ffcc00','ff9900','ff6600','ff3300','ff0000']}  # Verde -> Rojo
burnVis = {'min': 30.0, 'max': 341.0, 'palette': ['4e0400', '951003', 'c61503', 'ff1901']}

mapa_de_calor.addLayer(riesgo_mapa,riesgo_vis, "Índice de Riesgo de Incendio", opacity=1.0)
mapa_de_calor.addLayer(burntZones,burnVis,"Áreas Quemadas por Incendios previos")
# mapa_de_calor.addLayer(area, {},'Área analizada')
mapa_de_calor.addLayer(punto,{'color':'blue'},'Punto central del incendio')

mapa_de_calor.to_html('fwi-heatmap.html')
webbrowser.open('fwi-heatmap.html')


# Save the map as HTML
html_file = "fwi-heatmap.html"

# Define the color bar HTML
colorbar_html = """
<style>
    .colorbar-container {
        position: absolute;
        bottom: 10px;
        right: 10px;
        width: 400px;
        padding: 5px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid black;
        z-index: 1000;
        font-family: Arial, sans-serif;
    }
    .colorbar {
        width: 100%;
        height: 30px;
        background: linear-gradient(to right,
            #00ff00,
            #66ff00,
            #99ff00,
            #ccff00,
            #ffff00,
            #ffcc00,
            #ff9900,
            #ff6600,
            #ff3300,
            #ff0000
        );
    }
    .labels {
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        margin-top: 4px;
    }
</style>
<div class="colorbar-container">
    <div class="colorbar"></div>
    <div class="labels">
        <span>Muy bajo</span>
        <span> </span>
        <span>Bajo</span>
        <span> </span>
        <span>Moderado</span>
        <span> </span>
        <span>Alto</span>
        <span> </span>
        <span>Muy Alto</span>
        <span> </span>
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
#webbrowser.open(html_file)

print(f"Color bar added to {html_file}")