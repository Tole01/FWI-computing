def get_risk_score(fwi_indices, ndvi, slope, T_max):
    """
    Calcula el riesgo de incendio utilizando el índice de humedad del combustible (BUI), NDVI y la pendiente del terreno.
    Donde:
    - BUI: Índice de humedad del combustible.
    - NDVI: Índice de vegetación de diferencia normalizada.
    - slope: Pendiente del terreno.
    - T_max: Temperatura máxima en °C.
    - risk_score: Puntuación de riesgo de incendio.
    Retorna:
        risk_score: Puntuación de riesgo de incendio.    
    """
    # normalize values

    # Calculate the fire risk score using the given formula
    risk_score = 0.35 * fwi_indices['BUI'] + 0.15 * ndvi + 0.2 * slope + 0.3* T_max
    return risk_score