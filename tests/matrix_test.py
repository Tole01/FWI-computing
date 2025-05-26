import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
temp_array = np.random.uniform(20,25, size=(120, 160))
temp_array[0:7, 0:7] = 127
temp_array[0:7, 80:85] = 100
temp_array[0:7, 153:160] = 80
temp_array[50:55, 0:7] = 80
temp_array[50:55, 80:85] = 85
temp_matrix = temp_array

# Mostrar heatmap
plt.figure(figsize=(10, 6))
plt.imshow(temp_matrix, cmap='inferno')
plt.colorbar(label="Temperatura (°C)")
plt.title("Mapa de calor")
plt.tight_layout()
plt.show()