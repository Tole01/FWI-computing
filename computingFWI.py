import pandas as pd
import numpy as np
import math

class meshCell:
  '''
  Represents an individual cell from the total mesh analysis. Each cell has the following attributes:

    lat -> Actual GPS latitude of the cell centroid coordinate
    lon -> Actual GPS longitude of the cell centroid coordinate
    ndvi -> Normalized difference vegetation index
    slope -> Slope of terrain
    thermal -> Max temperature inside cell
    bui -> Build-up index
    risk -> Computed risk score for the cell
    classf -> Risk classification assigned from score 
    
  '''
  def __init__(self, lat, lon, row, col):
    self.row, self.col = row, col
    self.lat = lat
    self.lon = lon
    self.ndvi = None
    self.slope = None
    self.thermal = None
    self.bui = None
    self.risk = None
    self.classf = None
  
  # String representation
  def __str__(self):
    return f'Cell -> Row:[{self.row}] Col:[{self.col}]'
  

  
class FWICLASS:
  def __init__(self, temp, rhum, wind, prcp):
    self.t = temp  # temperatura en Celsius
    self.h = rhum  # humedad relativa
    self.w = wind  # velocidad del viento km/h
    self.p = prcp  # precipitación mm
    # print(temp, rhum, wind, prcp)

  def FFMCcalc(self, ffmc0):
    # Cálculo inicial de mo usando la entrada ffmc0
    mo = (147.2 * (101.0 - ffmc0)) / (59.5 + ffmc0)

    # Ajustar mo basado en la precipitación
    if self.p > 0.5:
      rf = self.p - 0.5
      if mo > 150.0:  # Verificado
        mo = (mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo))) * (1.0 - math.exp(-6.93 / rf)) + (
                .0015 * (mo - 150.0) ** 2) * math.sqrt(rf)
      elif mo <= 150.0:  # Verificado
        mo = (mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo))) * (1.0 - math.exp(-6.93 / rf))
      if (mo > 250.0):
        mo = 250.0
    # Calcular ed, el valor de mo cuando se considera la humedad y temperatura
    ed = 0.942 * (self.h ** 0.679) + (11.0 * math.exp((self.h - 100.0) / 10.0)) + 0.18 * (21.1 - self.t) * (
            1.0 - math.exp(-0.115 * self.h))

    # Ajustar mo basado en ed
    if mo < ed:  # Verificado
      ew = 0.618 * (self.h ** 0.753) + (10.0 * math.exp((self.h - 100.0) / 10.0)) + (
              0.18 * (21.1 - self.t) * (1.0 - math.exp(-0.115 * self.h)))
      if mo <= ew:
        kl = 0.424 * (1.0 - ((100.0 - self.h) / 100.0) ** 1.7) + (0.0694 * math.sqrt(self.w)) * (
                1.0 - ((100.0 - self.h) / 100.0) ** 8)
        kw = kl * (0.581 * math.exp(0.0365 * self.t))
        m = ew - (ew - mo) / (10.0 ** kw)
      else:
        m = mo
    elif (mo == ed):
      m = mo
    elif mo > ed:
      kl = 0.424 * (1.0 - (self.h / 100.0) ** 1.7) + (0.0694 * math.sqrt(self.w)) * (1.0 - (self.h / 100.0) ** 8)
      kw = kl * (0.581 * math.exp(0.0365 * self.t))
      m = ed + (mo - ed) / (10.0 ** kw)

    # Todo Verificado
    # Calcular el FFMC final usando el valor ajustado de m
    ffmc = (59.5 * (250.0 - m)) / (147.2 + m)
    # print(ffmc)
    if ffmc > 101.0:
      ffmc = 101.0
    elif ffmc <= 0.0:
      ffmc = 0.0
    # print('FFMC: ',ffmc)
    return ffmc

  # Todo FFMC verificado

  def DMCcalc(self, dmc0, mth):
    # Lista de valores de el correspondientes a cada mes
    el = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
    t = self.t
    # Asegurar que la temperatura no es menor que -1.1 grados Celsius
    if (t < -1.1):
      t = -1.1

    # Calcular rk, un factor que depende de la temperatura y la humedad
    rk = 1.894 * (t + 1.1) * (100.0 - self.h) * (el[mth - 1] * 0.0001)

    # Ajustar para condiciones de precipitación mayor a 1.5 mm
    if self.p > 1.5:
      ra = self.p
      rw = 0.92 * ra - 1.27
      wmi = 20.0 + 280.0 / math.exp(0.023 * dmc0)
      if dmc0 <= 33.0:
        b = 100.0 / (0.5 + 0.3 * dmc0)
      elif dmc0 > 33.0:
        if dmc0 <= 65.0:
          b = 14.0 + 1.3 * math.log(dmc0)
        elif dmc0 > 65.0:
          b = 6.2 * math.log(dmc0) - 17.2
      wmr = wmi + (1000 * rw) / (48.77 + (b * rw))
      pr = 43.43 * (5.6348 - math.log(wmr - 20.0))
    # Verificado
    # Ajustar para condiciones de precipitación menor o igual a 1.5 mm
    elif self.p <= 1.5:
      pr = dmc0

    # Ajustar pr si es negativo
    if pr < 0.0:
      pr = 0.0
    # Calcular el DMC final
    dmc = pr + rk

    if dmc <= 1.0:
      dmc = 1.0
    # print('DMC: ',dmc)
    return dmc

  # Verificado

  def DCcalc(self, dc0, mth):
    # Lista de factores de ajuste por mes
    fl = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]
    t = self.t

    # Asegurar que la temperatura no es menor que -2.8 grados Celsius
    if (t < -2.8):
      t = -2.8

    # Calcular el potencial de evaporación
    pe = (0.36 * (t + 2.8) + fl[mth - 1]) / 2
    if pe < 0.0:
      pe = 0.0

    # Ajustar para condiciones de precipitación mayor a 2.8 mm
    if self.p > 2.8:
      ra = self.p
      rw = 0.83 * ra - 1.27
      smi = 800.0 * math.exp(-dc0 / 400.0)
      dr = dc0 + 400.0 * math.log(1.0 + (3.937 * rw) / smi)
      if dr > 0.0:
        dc = dr + pe
    # Ajustar para condiciones de precipitación menor o igual a 2.8 mm
    elif self.p <= 2.8:
      dc = dc0 + pe
    # print('DC: ',dc)
    return dc

  # Verificado

  def ISIcalc(self, ffmc):
    # Calcular mo a partir del valor FFMC
    mo = 147.2 * (101.0 - ffmc) / (59.5 + ffmc)

    # Ajustar ff según la fórmula del ISI
    ff = 19.115 * math.exp(mo * -0.1386) * (1.0 + (mo ** 5.31) / 49300000.0)

    # Calcular el ISI
    isi = ff * math.exp(0.05039 * self.w)
    # print('ISI: ',isi)
    return isi

  # Verificado

  def BUIcalc(self, dmc, dc):
    # Calcular BUI según las condiciones de DMC y DC
    if dmc <= 0.4 * dc:
      bui = (0.8 * dc * dmc) / (dmc + (0.4 * dc))
    else:
      bui = dmc - (1.0 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + (0.0114 * dmc) ** 1.7)

    # Asegurar que BUI no sea negativo
    if bui < 0.0:
      bui = 0.0
    # print('BUI:', bui)
    normalized_bui = bui / 250  # Normalizar BUI a un rango de 0 a 1
    return normalized_bui

  # Verificado
  def FWIcalc(self, isi, bui):
    # Calcula el índice base bb usando isi y bui
    if bui <= 80.0:
      # Usa la fórmula para bui menor o igual a 80
      bb = 0.1 * isi * (0.626 * bui ** 0.809 + 2.0)
    else:
      # Usa la fórmula para bui mayor a 80
      bb = 0.1 * isi * (1000.0 / (25.0 + 108.64 / math.exp(0.023 * bui)))

    # Calcula el FWI final basado en el valor de bb
    if bb <= 1.0:
      # Si bb es menor o igual a 1, usa bb directamente como FWI
      fwi = bb
    else:
      # Si bb es mayor a 1, usa una transformación logarítmica para calcular FWI
      fwi = math.exp(2.72 * (0.434 * math.log(bb)) ** 0.647)

    return fwi


def calculate_fwi(row):
  fwi_system = FWICLASS(row['t2m_C'], row['humedad_relativa'], row['wind_speed_kmh'], row['precipitation_mm'])
  ffmc = fwi_system.FFMCcalc(85)  # Asumir FFMC inicial
  dmc = fwi_system.DMCcalc(6, row['month'])  # Asumir DMC inicial y mes
  dc = fwi_system.DCcalc(15, row['month'])  # Asumir DC inicial y mes
  isi = fwi_system.ISIcalc(ffmc)
  bui = fwi_system.BUIcalc(dmc, dc)
  fwi = fwi_system.FWIcalc(isi, bui)
  # Retornar todos los valores en un diccionario
  return {'FFMC': ffmc, 'DMC': dmc, 'DC': dc, 'ISI': isi, 'BUI': bui, 'FWI': fwi}


def calc_humedad_relativa(T, Td):
  T_c = T - 273.15  # Convertir de Kelvin a Celsius para la temperatura
  Td_c = Td - 273.15  # Convertir de Kelvin a Celsius para el punto de rocío
  eT = 6.112 * np.exp((17.67 * T_c) / (T_c + 243.5))
  eTd = 6.112 * np.exp((17.67 * Td_c) / (Td_c + 243.5))
  RH = 100 * (eTd / eT)
  return RH