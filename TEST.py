import numpy as np
import matplotlib.pyplot as plt
import scope

myscope=scope.Scope("COM1",debug=True)

x,data1, data2=myscope.readScope("CH1CH2")

plt.plot(x,data1, "r-")
plt.plot(x,data2, "g-")
plt.show()