import geojson

def calcular_step(matriz):
    if len(matriz) < 2:
        return 0.005  # valor por defecto

    # Ordenar por latitud y longitud para encontrar diferencias consistentes
    matriz_ordenada = sorted(matriz)

    # Buscar diferencia mínima entre latitudes y longitudes
    dif_lat = None
    dif_lon = None

    for i in range(1, len(matriz_ordenada)):
        lat1, lon1, _ = matriz_ordenada[i - 1]
        lat2, lon2, _ = matriz_ordenada[i]
        dlat = abs(lat2 - lat1)
        dlon = abs(lon2 - lon1)

        if dlat != 0:
            dif_lat = dlat if dif_lat is None else min(dif_lat, dlat)
        if dlon != 0:
            dif_lon = dlon if dif_lon is None else min(dif_lon, dlon)

    # Elegimos el menor paso detectado como el size del cuadro
    return min(filter(None, [dif_lat, dif_lon])) or 0.005


def generar_geojson(coord_list, rsk):
    
    # Matriz ejemplo (latitud, longitud, nivel de riesgo [0–1])
    matriz = [
        (34.05, -118.25, 0.2),
        (34.06, -118.25, 0.6),
        (34.07, -118.25, 0.9)
    ]

    #for coord_pair in coord_list:
    #    for i in range(len(rsk)):
    #        for j in range(len(rsk[i])):
    #            coord_pair = (coord_pair[0] ,coord_pair[1], rsk[i][j])

    matriz = coord_list
    print(matriz)
    matriz = [
    (34.000, -118.300, 0.10), (34.000, -118.295, 0.15), (34.000, -118.290, 0.30), (34.000, -118.285, 0.60), (34.000, -118.280, 0.85),
    (34.005, -118.300, 0.20), (34.005, -118.295, 0.25), (34.005, -118.290, 0.45), (34.005, -118.285, 0.65), (34.005, -118.280, 0.90),
    (34.010, -118.300, 0.35), (34.010, -118.295, 0.40), (34.010, -118.290, 0.55), (34.010, -118.285, 0.70), (34.010, -118.280, 0.95),
    (34.015, -118.300, 0.50), (34.015, -118.295, 0.60), (34.015, -118.290, 0.75), (34.015, -118.285, 0.80), (34.015, -118.280, 0.98),
    (34.020, -118.300, 0.65), (34.020, -118.295, 0.70), (34.020, -118.290, 0.85), (34.020, -118.285, 0.90), (34.020, -118.280, 1.00)
]
    
    step = 0.01  # tamaño del cuadrado en grados/coordenadas geográficas (1 grado = 111 km aprox)
    step = 0.000196
    step = calcular_step(matriz)
    step = 0.005

    
    features = []

    for lat, lon, riesgo in matriz:
        coords = [[
            [lon, lat],
            [lon + step, lat],
            [lon + step, lat + step],
            [lon, lat + step],
            [lon, lat]
        ]]
        feature = geojson.Feature(
            geometry=geojson.Polygon(coords),
            properties={"riesgo": riesgo}
        )
        features.append(feature)

    geojson_obj = geojson.FeatureCollection(features)

    with open("riesgo.geojson", "w") as f:
        geojson.dump(geojson_obj, f)