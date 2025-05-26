import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
temp_array = np.random.uniform(20,25, size=(60, 80))
temp_array[30:38, 30:40] += 35
temp_array[30:40, 0:20] += 10
temp_array[13:18, 28:33] = 80
temp_array[12:15, 47:52] = 77
temp_array[38:43, 58:63] = 77
temp_array[8:13, 8:13] = 65
temp_array[0:5, 0:5] = 90
temp_array[50:55, 50:55] = 70
temp_array[40:45,20:24] = 83
temp_matrix = temp_array

# Mostrar heatmap
plt.figure(figsize=(10, 6))
plt.imshow(temp_matrix, cmap='inferno')
plt.colorbar(label="Temperatura (°C)")
plt.title("Mapa de calor")
plt.tight_layout()
plt.show()