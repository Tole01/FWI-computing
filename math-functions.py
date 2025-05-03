import numpy
import math

def risk_score(ndvi,slope,thermal):

    ndviWeight = 0.3
    slopeWeight = 0.4
    thermalWeight = 0.5

    #Conversión a °C en caso de ser necesario
    thermal = (thermal*0.2) - 273.15

    score = (ndvi*ndviWeight) + (slope*slopeWeight) + (thermal*thermalWeight)
    return score

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