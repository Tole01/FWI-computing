import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
temp_array = np.random.uniform(20,25, size=(120, 160))
temp_array[60:76, 60:80] += 35
temp_array[40:46, 40:46] += 60
temp_array[40:46, 50:56] += 55
temp_array[50:56, 50:56] += 50
temp_array[30:40, 26:34] = 110
temp_array[60:80, 0:40] += 10
temp_array[26:36, 56:66] = 80
temp_array[24:30, 96:104] = 120
temp_array[36:52, 4:12] = 115
temp_array[60:72, 4:14] = 107
temp_array[94:102, 26:34] = 105
temp_array[76:86, 116:126] = 98
temp_array[16:26, 16:26] = 100
temp_array[0:10, 0:10] = 90
temp_array[8:16, 110:124] = 95
temp_array[58:66, 136:146] = 99
temp_array[100:110, 100:110] = 102
temp_array[80:90, 40:48] = 83
temp_array[25:32, 130:142] = 88
temp_array[18:26, 38:52] = 127
temp_matrix = temp_array

# Mostrar heatmap
plt.figure(figsize=(10, 6))
plt.imshow(temp_matrix, cmap='inferno')
plt.colorbar(label="Temperatura (°C)")
plt.title("Mapa de calor")
plt.tight_layout()
plt.show()