import numpy as np
import pandas as pd

# Assigned weight to parameters
weights = {'NDVI': 0.15, 'Slope': 0.20, 'Thermal': 0.30, 'BUI': 0.35}

def normalize(value, min_value, max_value):
    """Normalize a value to the range [0, 1].
    >>> normalize(35, 25, 45)
    0.5
    """
    return (value - min_value) / (max_value - min_value)

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
    # Normalize parameters
    df_normalized = normalize_parameters(df)
  
    risk_score = sum([weights[column] * column for column in df_normalized.columns])
    
    return risk_score

def generate_dataFrame(ndvi, slope, thermal, bui):
    '''Generates a Pandas Dataframe storing sequential parameters'''
    df = pd.DataFrame({'NDVI': ndvi,
                       'Slope': slope,
                       'Thermal': thermal,
                       'BUI': bui
                        })
    return df

def normalize_parameters(df):
    """Normalize parameters for each row"""
    for column in df.columns:
        min_val, max_val = df[column].min(), df[column].max()
        df[column] = normalize(column, min_val, max_val)

    return df



