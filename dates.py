import numpy as np
import math
import ee
import geemap
import webbrowser
import datetime


def risk_score(ndvi, slope, thermal):
    # Para sacar el peso individual de cada variable se sumaron sus IV's resultantes del análisis con el script de woe-data2.py
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

    # Conversión a °C en caso de ser necesario
    thermal = (thermal * 0.2) - 273.15

    score = (ndvi * ndviWeight) + (slope * slopeWeight) + \
        (thermal * thermalWeight)
    return score


def risk_level(score):
    if score <= 1000:
        return "Muy Bajo"
    elif score <= 1800:
        return "Bajo"
    elif score <= 2200:
        return "Moderado"
    elif score <= 2600:
        return "Alto"
    elif score <= 3000:
        return "Muy Alto"
    else:
        return "Extremo"


def visualizar_riesgo(ndvi, slope, lst_image):
    ndviWeight = 0.5142
    slopeWeight = 0.1722
    thermalWeight = 0.3136
    riesgo_img = ndvi.multiply(ndviWeight).add(slope.multiply(slopeWeight)).add(
        lst_image.multiply(thermalWeight)).rename("Riesgo")
    return riesgo_img


def spread_rate(deltaH, windSpeed, slopeAng, ignitionHeat):
    # Asegurarse de que las variables estén en las siguientes unidades:
    # Calor liberado por unidad -> deltaH -> kJ/m^2
    # Velocidad del viento -> windSpeed -> m/s
    # Ángulo de la pendiente -> slopeAng -> radianes
    # Calor requerido para encender la sig. unidad -> ignitionHeat -> kJ/m^2

    rate = (deltaH * windSpeed * math.cos(slopeAng)) / ignitionHeat
    return rate


# === Autenticación e inicialización  ===
ee.Authenticate()
ee.Initialize(project='light-sunup-288723')

# Coordenadas de interés (Pasadena, California)
lat = 34.21113114902449
long = -118.1138591514406

punto = ee.Geometry.Point([long, lat])
area = punto.buffer(10000)

# === Definición de fecha  ===
hoy = datetime.date.today()
gap = 29
delay = 28
fin_str = (hoy - datetime.timedelta(days=delay)).isoformat()
inicio_str = (hoy - datetime.timedelta(days=delay + gap)).isoformat()
print(f"Fechas de análisis: {inicio_str} a {fin_str}")
inicio = ee.Date(inicio_str)
fin = ee.Date(fin_str)

# NDVI - MODIS/061/MOD13Q1
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate(inicio, fin).select(
    'NDVI').sort('system:time_start', False).mean().clip(area)

# Temperatura de Superficie Terrestre - MODIS/061/MOD11A1
lst_image = ee.ImageCollection("MODIS/061/MOD11A1").filterBounds(punto).filterDate(
    inicio, fin).sort('system:time_start', False).first().select(
    'LST_Day_1km').multiply(0.02).subtract(273.15).rename('Temperatura_C').clip(area)

# Velocidad del Viento - NOAA/GFS0P25
wind_collection = ee.ImageCollection('NOAA/GFS0P25').filterDate(
    inicio, fin).sort('system:time_start', False).select(
    ['u_component_of_wind_10m_above_ground', 'v_component_of_wind_10m_above_ground'])

meanU = wind_collection.select('u_component_of_wind_10m_above_ground').mean()
meanV = wind_collection.select('v_component_of_wind_10m_above_ground').mean()
wind_speed = meanU.hypot(meanV).rename('WindSpeed_m/s').clip(area)
wind_dir = meanU.atan2(meanV).rename('WindDirection_rad').clip(
    area)  # Dirección del viento en radianes

# Pendiente - USGS/SRTMGL1_003
slope = ee.Terrain.slope(ee.Image('USGS/SRTMGL1_003')
                         ).rename('Pendiente_Angulo').clip(area)

# Imagen compuesta
imagen_completa = ndvi.rename('NDVI') \
    .addBands(lst_image) \
    .addBands(wind_speed) \
    .addBands(wind_dir) \
    .addBands(slope)

# Muestreo
muestreo = imagen_completa.sample(
    region=area, scale=100, numPixels=100, geometries=True)
datos = muestreo.getInfo()

# Evaluación del riesgo
riesgo_mapa = None
if not datos['features']:
    print("No se encontraron datos para las coordenadas y fechas especificadas.")
else:
    riesgo_mapa = visualizar_riesgo(ndvi, slope, lst_image)
    for feature in datos['features']:
        props = feature['properties']
        coords = feature['geometry']['coordinates']

        valor_ndvi = props['NDVI']
        valor_wind = props['WindSpeed_m/s']
        dir_wind = props['WindDirection_rad']
        valor_temp = props['Temperatura_C']
        valor_pendiente = props['Pendiente_Angulo']
        valor_pendiente_rad = math.radians(valor_pendiente)

        riesgo_estimado = risk_score(
            valor_ndvi, valor_pendiente_rad, valor_temp)

        nivel = risk_level(riesgo_estimado)

        print(f"Índice de riesgo: {riesgo_estimado:.2f} ({nivel})")
        print(f"Coordenadas: {coords}")
        print(
            f"NDVI: {valor_ndvi}, Temp: {valor_temp} °C, Viento: {valor_wind} m/s, Pendiente: {valor_pendiente}°")
        print(f"Índice de riesgo: {riesgo_estimado:.2f}")

# Mapa con Geemap
mapa_de_calor = geemap.Map(center=[lat, long], zoom=10)
riesgo_vis = {'min': 900, 'max': 3300, 'palette': [
    '00ff00', '66ff00', '99ff00', 'ccff00', 'ffff00',
    'ffcc00', 'ff9900', 'ff6600', 'ff3300', 'ff0000']}

if riesgo_mapa:
    mapa_de_calor.addLayer(riesgo_mapa, riesgo_vis,
                           "Índice de Riesgo de Incendio", opacity=0.85)
mapa_de_calor.addLayer(area, {}, 'Área analizada')
mapa_de_calor.addLayer(punto, {'color': 'blue'}, 'Punto central del incendio')

html_file = "fwi-heatmap.html"
mapa_de_calor.to_html(html_file)
webbrowser.open(html_file)

# Barra de colores
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
        #00ff00, #66ff00, #99ff00, #ccff00, #ffff00,
        #ffcc00, #ff9900, #ff6600, #ff3300, #ff0000);
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
        <span>Muy bajo</span><span></span><span>Bajo</span><span></span>
        <span>Moderado</span><span></span><span>Alto</span><span></span>
        <span>Muy Alto</span><span></span>
    </div>
</div>
"""

# Agregar barra de color al HTML generado
with open(html_file, "r+", encoding="utf-8") as file:
    content = file.read()
    if "</body>" in content:
        content = content.replace("</body>", colorbar_html + "</body>")
        file.seek(0)
        file.write(content)
