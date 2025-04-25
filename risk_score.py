import numpy as np
import pandas as pd

def normalize(value, min_value, max_value):
    """Normalize a value to the range [0, 1]."""
    return (value - min_value) / (max_value - min_value)

def calculate_risk_score(ndvi, slope, thermal, bui, weights):
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
    return (weights['ndvi'] * ndvi +
            weights['slope'] * slope +
            weights['thermal'] * thermal +
            weights['bui'] * bui)


def normalize_parameters(df):
    '''Generate a normalized data frame from the cell parameters
    
    Input: 
        df: pandas dataframe containing the parameters used for the risk score calculation
    
    Output:
        df: normalized DataFrame for each parameter'''

    for column in df.columns:
        df[f'{column}_normalized'] = normalize(df[column], df[column].min(), df[column].max())
    
    return df

# Set initial equal weights
weights = {'ndvi': 0.15, 'slope': 0.20, 'thermal': 0.30, 'bui': 0.35}

# Example input data
df = pd.DataFrame({
    'NDVI': [0.4, 0.6, 0.8],
    'Slope': [10, 20, 30],
    'Thermal': [25, 35, 45],
    'BUI': [30, 40, 50]
})

# Normalize DataFrame
df = normalize_parameters(df)
df['Risk_Score'] = df.apply(lambda row: calculate_risk_score(
    row['NDVI_normalized'],
    row['Slope_normalized'],
    row['Thermal_normalized'],
    row['BUI_normalized'],
    weights
), axis=1)

print(df[['NDVI', 'Slope', 'Thermal', 'BUI', 'Risk_Score']])