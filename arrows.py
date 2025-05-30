import numpy
import math
import ee
import leafmap
import leafmap.foliumap as leafmap
import webbrowser
import datetime
import folium


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
    thermal = (thermal*0.2) - 273.15

    score = (ndvi*ndviWeight) + (slope*slopeWeight) + (thermal*thermalWeight)
    return score


def visualizar_riesgo(ndvi, slope, lst_image):
    ndviWeight = 0.5142
    slopeWeight = 0.1722
    thermalWeight = 0.3136
    # Cálculo del índice de riesgo como imagen en EE
    riesgo_img = ndvi.multiply(ndviWeight).add(slope.multiply(slopeWeight)).add(
        lst_image.multiply(thermalWeight)).rename("Riesgo")
    return riesgo_img


def spread_rate(deltaH, windSpeed, slopeAng, ignitionHeat):

    # Asegurarse de que las variables estén en las siguientes unidades:
    # Calor liberado por unidad -> deltaH -> kJ/m^2
    # Velocidad del viento -> windSpeed -> m/s
    # Ángulo de la pendiente -> slopeAng -> radianes
    # Calor requerido para encender la sig. unidad -> ignitionHeat -> kJ/m^2

    # Fórmula de tasa de expansión
    # R = dH*W*cos(theta)/Q
    rate = (deltaH * windSpeed * math.cos(slopeAng))/ignitionHeat
    return rate


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)


folium.Map.add_ee_layer = add_ee_layer


#  === Autenticación e inicialización  ===
ee.Authenticate()
ee.Initialize(project='light-sunup-288723')  # Usa tu ID si es diferente

# Selección de coordenadas de interés
lat = float(34.21113114902449)
long = float(-118.1138591514406)

# Creación de punto geométrico
punto = ee.Geometry.Point([long, lat])
area = punto.buffer(10000)

#  === Definición de fecha  ===
hoy = datetime.date.today()
gap = 29  # Días entre inicio y fin
delay = 29  # Días de retraso en la base de datos
fin_str = (hoy - datetime.timedelta(days=delay)).isoformat()
inicio_str = (hoy - datetime.timedelta(days=delay+gap)).isoformat()
print(f"Fechas de análisis: {inicio_str} a {fin_str}")
inicio = ee.Date(inicio_str)
fin = ee.Date(fin_str)

# == viento
url = "https://github.com/opengeos/datasets/releases/download/raster/wind_global.nc"
filename = "wind_global.nc"
leafmap.download_file(url, output=filename, overwrite=True)
data = leafmap.read_netcdf(filename)
print(data)

tif = "wind_global.tif"
leafmap.netcdf_to_tif(filename, tif, variables=[
                      "u_wind", "v_wind"], shift_lon=True)
geojson = (
    "https://github.com/opengeos/leafmap/raw/master/examples/data/countries.geojson")


# Importar datos de NDVI
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate(inicio, fin).select(
    'NDVI').sort('system:time_start', False).mean().clip(area)

# Importar datos de Temperatura de Superficie Terrestre
modis = ee.ImageCollection("MODIS/061/MOD11A1") \
    .filterBounds(punto) \
    .filterDate(inicio, fin) \
    .sort('system:time_start', False) \
    .first()

lst_image = modis.select('LST_Day_1km').multiply(
    0.02).subtract(273.15).rename('Temperatura_C').clip(area)

# Importar datos de Velocidad del Viento
wind_collection = ee.ImageCollection('NOAA/GFS0P25').filterDate(inicio, fin)\
    .sort('system:time_start', False).select(['u_component_of_wind_10m_above_ground', 'v_component_of_wind_10m_above_ground'])

meanU = wind_collection.select('u_component_of_wind_10m_above_ground').mean()
meanV = wind_collection.select('v_component_of_wind_10m_above_ground').mean()

wind_speed = meanU.hypot(meanV).rename('WindSpeed_m/s').clip(area)

# Importar datos de Pendiente
dem = ee.Image('USGS/SRTMGL1_003')
slope = ee.Terrain.slope(dem).rename('Pendiente_Angulo').clip(area)

imagen_completa = ndvi.rename('NDVI').addBands(
    lst_image).addBands(wind_speed).addBands(slope)

muestreo = imagen_completa.sample(
    region=area, scale=100, numPixels=100, geometries=True)
datos = muestreo.getInfo()

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

        riesgo_estimado = risk_score(
            valor_ndvi, valor_pendiente_rad, valor_temp)

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
        print(
            f"NDVI: {valor_ndvi}, Temp: {valor_temp} °C, Viento: {valor_wind} m/s, Pendiente: {valor_pendiente}°")
        print(f"Índice de riesgo: {riesgo_estimado:.2f}")

# Crear mapa
mapa_de_calor = folium.Map(location=[lat, long], zoom_start=10)


# Añadir la capa de riesgo si existe
if riesgo_mapa is not None:
    riesgo_vis = {
        'min': 900,
        'max': 3300,
        'palette': ['00ff00', '66ff00', '99ff00', 'ccff00', 'ffff00', 'ffcc00', 'ff9900', 'ff6600', 'ff3300', 'ff0000']
    }
    mapa_de_calor.add_ee_layer(
        riesgo_mapa, riesgo_vis, "Índice de Riesgo de Incendio")


# Añadir el área y punto (puedes usar folium directamente)
# Añadir el área como una capa de GeoJson y darle nombre para control
area_layer = folium.FeatureGroup(name="Área Seleccionada")
folium.GeoJson(data=area.getInfo()).add_to(area_layer)
area_layer.add_to(mapa_de_calor)

# Añadir el punto central como otra capa y darle nombre para control
punto_layer = folium.FeatureGroup(name="Punto Central")
folium.Marker(
    location=[lat, long],
    popup="Punto Central",
    icon=folium.Icon(color='blue')
).add_to(punto_layer)
punto_layer.add_to(mapa_de_calor)

# Agregar control de capas para poder activar/desactivar
folium.LayerControl().add_to(mapa_de_calor)

# Guardar mapa en HTML
html_file = 'fwi-heatmap.html'
mapa_de_calor.save(html_file)
webbrowser.open(html_file)

# Añadir barra de colores y slider con edición HTML (igual que antes)
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
        // Esperar a que el mapa esté listo (leaflet)
        if (typeof window.map === 'undefined') {
            setTimeout(waitForMap, 200);
        } else {
            map = window.map;

            // Añadir slider
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = 1000;
            slider.max = 10000;
            slider.step = 1000;
            slider.value = 10000;
            slider.style.position = 'absolute';
            slider.style.top = '10px';
            slider.style.left = '10px';
            slider.style.zIndex = 1000;
            slider.title = "Cambiar radio del área de análisis";

            slider.oninput = function () {
                let radius = parseInt(this.value);
                if (bufferCircle) {
                    map.removeLayer(bufferCircle);
                }
                bufferCircle = L.circle([%(lat)f, %(lon)f], {
                    color: 'red',
                    fillColor: '#f03',
                    fillOpacity: 0.1,
                    radius: radius
                }).addTo(map);
            };

            map.getContainer().appendChild(slider);

            // Añadir círculo inicial
            bufferCircle = L.circle([%(lat)f, %(lon)f], {
                color: 'red',
                fillColor: '#f03',
                fillOpacity: 0.1,
                radius: 10000
            }).addTo(map);
        }
    }

    waitForMap();
</script>
""" % {'lat': lat, 'lon': long}

with open(html_file, "r+", encoding="utf-8") as file:
    content = file.read()
    content = content.replace("</body>", slider_html + "</body>")
    file.seek(0)
    file.write(content)
