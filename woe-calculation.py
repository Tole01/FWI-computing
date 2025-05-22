import pandas as pd
import scorecardpy as sc

# Cargar el archivo con datos
df = pd.read_csv('incendios_los_angeles.csv')

# Verificar que la variable objetivo es binaria
print("Valores únicos de riesgo:", df['riesgo'].unique())

# Eliminar columnas que no serán usadas como predictoras
df_modelo = df.drop(columns=['lat', 'lon', 'fecha'])

# Imputar valores nulos con la media
df_modelo.fillna(df_modelo.mean(), inplace=True)

# Definir variables predictoras
y = 'riesgo'
x = [col for col in df_modelo.columns if col != y]

# Generar los bins WoE
bins = sc.woebin(df_modelo, y=y)

# Transformar los datos usando WoE
df_woe = sc.woebin_ply(df_modelo, bins)

# Extraer IV desde los bins
iv_values = {var: bins[var]['total_iv'].values[0] for var in bins}
iv_df = pd.DataFrame(list(iv_values.items()), columns=['Variable', 'IV'])

print("\nInformation Value por variable:")
print(iv_df)

# Guardar los datos transformados en un CSV
df_woe.to_csv('incendios_los_angeles_woe.csv', index=False)
print("Archivo WoE exportado como 'incendios_los_angeles_woe.csv'")
