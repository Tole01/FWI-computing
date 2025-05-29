import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
temp_array = np.random.uniform(20,25, size=(120, 160))
temp_array[0:10, 0:10] = 127
temp_array[50:60, 0:10] = 120
temp_array[100:110, 0:10] = 115
temp_array[0:10, 50:60] = 100
temp_array[50:60, 50:60] = 115
temp_array[100:110, 50:60] = 110
temp_array[0:10, 110:120] = 97
temp_array[50:60, 110:120] = 98
temp_array[100:110, 110:120] = 100
temp_array[0:10, 150:160] = 95
temp_array[50:60, 150:160] = 99
temp_array[100:110, 150:160] = 115
temp_matrix = temp_array

# Mostrar heatmap
plt.figure(figsize=(10, 6))
plt.imshow(temp_matrix, cmap='inferno')
plt.colorbar(label="Temperatura (°C)")
plt.title("Mapa de calor")
plt.tight_layout()
plt.show()