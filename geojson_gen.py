import geojson

def calcular_step(matriz):
    if len(matriz) < 2:
        return 0.005  # valor por defecto

    # Ordenar por latitud y longitud para encontrar diferencias consistentes
    #matriz_ordenada = sorted(matriz)
    matriz_ordenada = matriz

    # Buscar diferencia mínima entre latitudes y longitudes
    dif_lat = None
    dif_lon = None

    for i in range(1, len(matriz_ordenada)):
        lat1, lon1, _ = matriz_ordenada[i - 1][i-1]  
        lat2, lon2, _ = matriz_ordenada[i][i]
        dlat = abs(lat2 - lat1)
        dlon = abs(lon2 - lon1)

        if dlat != 0:
            dif_lat = dlat if dif_lat is None else min(dif_lat, dlat)
        if dlon != 0:
            dif_lon = dlon if dif_lon is None else min(dif_lon, dlon)

    # Elegimos el menor paso detectado como el size del cuadro
    return min(filter(None, [dif_lat, dif_lon])) or 0.005


def generar_geojson(coord_list):
    
    # Matriz con coordenadas y riesgo reales
    matriz = coord_list
    #print(matriz)

    step = calcular_step(matriz)
    #print(f"Step calculado: {step}")

    #print(matriz.shape)
    features = []
    
    for row in matriz:
        for lat, lon, riesgo in row:
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