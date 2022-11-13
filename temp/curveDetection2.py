import numpy as np
from matplotlib import pyplot as plt
x = np.array([368, 368, 369, 369, 367, 354, 348, 336, 334, 328, 325, 324, 293, 272])
y = np.array([439, 409, 407, 406, 400, 381, 366, 337, 336, 326, 323, 321, 305, 294])
poly=np.poly1d(np.polyfit(x, y, 2))
plt.scatter(x,y) #narysowanie
sorted = np.sort(x) #sortowanie
print(sorted, poly(sorted))
plt.plot(sorted, poly(sorted))
plt.show()