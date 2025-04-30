import numpy as np
import pandas as pd

# Assigned weight to parameters
weights = {'NDVI': 0.15, 'Slope': 0.20, 'Thermal': 0.30, 'BUI': 0.35}

def calculate_risk_score(ndvi, slope, thermal, bui):
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

    """
    >>> calculate_risk_score(0.4, 10, 25, 30)
    0.0
    >>> calculate_risk_score(0.6, 20, 35, 40)
    0.5 
    >>> calculate_risk_score(0.8, 30, 45, 50)
    1.0
    """
    # Generate Data Frame
    df = generate_dataFrame(ndvi, slope, thermal, bui)
  
    risk_score = sum([weights[column] * df[column].iloc[0] for column in df.columns])
    
    return risk_score

def generate_dataFrame(ndvi, slope, thermal, bui):
    '''Generates a Pandas Dataframe storing sequential parameters'''
    df = pd.DataFrame({'NDVI': ndvi,
                       'Slope': slope,
                       'Thermal': thermal,
                       'BUI': bui
                        }, index=[0])
    return df



