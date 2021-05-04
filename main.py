import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal.windows
import pandas as pd

# Read data from file
all_data = pd.read_csv('data.dat', sep='\t', header=None)
data = all_data.values[:, 1]
samplerate = 1000.0

# Number of samplepoints
N = len(data)
window = scipy.signal.windows.blackman(N)
windowed_data = data * window

# sample spacing
T = 1.0 / samplerate

x = np.linspace(0.0, N * T, N)
y = np.sin(50.0 * 2.0 * np.pi * x) + 0.5 * np.sin(80.0 * 2.0 * np.pi * x) + 0.6

yf = scipy.fftpack.fft(data)
yf[0] /= 2
# xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
xf = scipy.fftpack.fftfreq(N, T)[:N // 2]

fig, axs = plt.subplots(2)
axs[0].plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
axs[1].plot(all_data.values[:, 0], data)
plt.grid()
plt.show()
