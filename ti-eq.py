import cv2
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "gambar.png")

img_bgr = cv2.imread(image_path)

if img_bgr is None:
    raise FileNotFoundError(f"File {image_path} tidak ditemukan!")

# Resize input image to keep outputs within the window boundary
img_bgr = cv2.resize(img_bgr, (320, 240))

b = img_bgr[:, :, 0].astype(np.float32)
g = img_bgr[:, :, 1].astype(np.float32)
r = img_bgr[:, :, 2].astype(np.float32)
gray = (0.114 * b + 0.587 * g + 0.299 * r).astype(np.uint8)

h, w = gray.shape
total_pixels = h * w

# 1. Transformasi Intensitas Manual
img_negative = 255 - gray

c_log = 255.0 / np.log(1.0 + 255.0)
lut_log = np.array([round(c_log * np.log(1.0 + float(i))) for i in range(256)], dtype=np.uint8)
img_log = lut_log[gray]

gamma = 0.5
c_gamma = 255.0 / (255.0 ** gamma)
lut_gamma = np.array([round(c_gamma * (float(i) ** gamma)) for i in range(256)], dtype=np.uint8)
img_gamma = lut_gamma[gray]

# 2. Ekualisasi Histogram Manual
hist = np.zeros(256, dtype=int)
flat_gray = gray.reshape(-1)
for val in flat_gray:
    hist[val] += 1

cdf = np.zeros(256, dtype=float)
cumulative = 0
for i in range(256):
    cumulative += hist[i]
    cdf[i] = cumulative

cdf_min = 0
for i in range(256):
    if cdf[i] > 0:
        cdf_min = cdf[i]
        break

lut_eq = np.zeros(256, dtype=np.uint8)
denom = total_pixels - cdf_min
for i in range(256):
    if denom > 0:
        lut_eq[i] = round(((cdf[i] - cdf_min) / denom) * 255)
    else:
        lut_eq[i] = i

img_equalized = lut_eq[gray]

# Layout & Text Labels
row1 = np.hstack((gray, img_negative, img_equalized))
row2 = np.hstack((gray, img_log, img_gamma))

cv2.putText(row1, "Grayscale", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
cv2.putText(row1, "Negative", (w + 15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
cv2.putText(row1, "Equalized", (2 * w + 15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)

cv2.putText(row2, "Grayscale", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
cv2.putText(row2, "Log Transform", (w + 15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
cv2.putText(row2, "Gamma Transform", (2 * w + 15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)

display = np.vstack((row1, row2))

window_name = "Tugas 2 - Intensitas & Ekualisasi Histogram (Manual)"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 960, 480)

cv2.imshow(window_name, display)

cv2.waitKey(0)
cv2.destroyAllWindows()