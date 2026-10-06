import sys
from pathlib import Path

import cv2
import numpy as np


# ============================================================
# 1. RGB
# ============================================================

def bgr_to_rgb(image):
    """OpenCV membaca gambar sebagai BGR, jadi ubah ke RGB."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def rgb_to_bgr(image):
    """Mengubah RGB kembali menjadi BGR untuk cv2.imwrite()."""
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


# ============================================================
# 2. RGB -> CMYK
# ============================================================

def rgb_to_cmyk(rgb):
    """
    Konversi RGB ke CMYK.

    RGB dinormalisasi ke 0-1.
    Rumus:
        K = 1 - max(R,G,B)
        C = (1-R-K)/(1-K)
        M = (1-G-K)/(1-K)
        Y = (1-B-K)/(1-K)
    """
    rgb_float = rgb.astype(np.float32) / 255.0

    r = rgb_float[:, :, 0]
    g = rgb_float[:, :, 1]
    b = rgb_float[:, :, 2]

    k = 1 - np.maximum.reduce([r, g, b])

    # Hindari pembagian dengan nol pada piksel hitam.
    denominator = 1 - k

    c = np.zeros_like(k)
    m = np.zeros_like(k)
    y = np.zeros_like(k)

    mask = denominator > 1e-6

    c[mask] = (1 - r[mask] - k[mask]) / denominator[mask]
    m[mask] = (1 - g[mask] - k[mask]) / denominator[mask]
    y[mask] = (1 - b[mask] - k[mask]) / denominator[mask]

    cmyk = np.stack([c, m, y, k], axis=2)

    return (cmyk * 255).clip(0, 255).astype(np.uint8)


# ============================================================
# 3. RGB -> HSI
# ============================================================

def rgb_to_hsi(rgb):
    """
    Konversi RGB ke HSI.

    H = Hue
    S = Saturation
    I = Intensity

    H dalam derajat 0-360.
    S dan I dalam range 0-1.
    """
    rgb_float = rgb.astype(np.float32) / 255.0

    r = rgb_float[:, :, 0]
    g = rgb_float[:, :, 1]
    b = rgb_float[:, :, 2]

    # Intensity
    intensity = (r + g + b) / 3.0

    # Saturation
    min_rgb = np.minimum(np.minimum(r, g), b)
    sum_rgb = r + g + b

    saturation = np.zeros_like(intensity)
    nonzero = sum_rgb > 1e-6

    saturation[nonzero] = (
        1 - (3 * min_rgb[nonzero] / sum_rgb[nonzero])
    )

    # Hue
    numerator = 0.5 * ((r - g) + (r - b))
    denominator = np.sqrt(
        (r - g) ** 2 +
        (r - b) * (g - b)
    )

    theta = np.zeros_like(r)
    valid = denominator > 1e-6

    ratio = np.zeros_like(r)
    ratio[valid] = numerator[valid] / denominator[valid]
    ratio = np.clip(ratio, -1, 1)

    theta[valid] = np.arccos(ratio[valid])

    hue = theta.copy()
    hue[b > g] = 2 * np.pi - theta[b > g]
    hue = hue * 180 / np.pi

    # Gray pixels tidak memiliki hue yang bermakna.
    hue[saturation < 1e-6] = 0

    return hue, saturation, intensity


def hsi_to_display(hue, saturation, intensity):
    """
    Membuat visualisasi HSI:
    H -> 0-255
    S -> 0-255
    I -> 0-255
    """
    h = (hue / 360 * 255).clip(0, 255).astype(np.uint8)
    s = (saturation * 255).clip(0, 255).astype(np.uint8)
    i = (intensity * 255).clip(0, 255).astype(np.uint8)

    return h, s, i


# ============================================================
# 4. RGB -> HSV
# ============================================================

def rgb_to_hsv(rgb):
    """
    Konversi RGB ke HSV menggunakan OpenCV.

    OpenCV:
        H = 0-179
        S = 0-255
        V = 0-255
    """
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)


# ============================================================
# 5. RGB VS HSV
# ============================================================

def compare_rgb_hsv(rgb):
    """
    Menampilkan channel RGB dan HSV agar perbedaan
    representasi warna dapat diamati.
    """
    hsv = rgb_to_hsv(rgb)

    r, g, b = cv2.split(rgb)
    h, s, v = cv2.split(hsv)

    return r, g, b, h, s, v


# ============================================================
# 6. MASK WARNA
# ============================================================

def create_color_masks(rgb):
    """
    Membuat mask warna menggunakan HSV.

    Contoh:
    - merah
    - hijau
    - biru

    Mask bernilai:
        255 -> warna masuk range
        0   -> bukan warna target
    """
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

    # ----------------------------
    # Merah
    # ----------------------------
    # Merah berada di dua sisi hue HSV.
    lower_red_1 = np.array([0, 80, 50])
    upper_red_1 = np.array([10, 255, 255])

    lower_red_2 = np.array([170, 80, 50])
    upper_red_2 = np.array([179, 255, 255])

    red_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    red_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    red_mask = cv2.bitwise_or(red_1, red_2)

    # ----------------------------
    # Hijau
    # ----------------------------
    lower_green = np.array([35, 60, 40])
    upper_green = np.array([85, 255, 255])

    green_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    # ----------------------------
    # Biru
    # ----------------------------
    lower_blue = np.array([90, 60, 40])
    upper_blue = np.array([130, 255, 255])

    blue_mask = cv2.inRange(
        hsv,
        lower_blue,
        upper_blue
    )

    return red_mask, green_mask, blue_mask


def apply_mask(rgb, mask):
    """Mengambil hanya area yang termasuk mask."""
    return cv2.bitwise_and(rgb, rgb, mask=mask)


# ============================================================
# 7. ALPHA BLENDING
# ============================================================

def alpha_blend(image_a, image_b, alpha=0.5):
    """
    Alpha blending:

        output = alpha*A + (1-alpha)*B

    alpha = 1.0 -> hanya A
    alpha = 0.0 -> hanya B
    alpha = 0.5 -> campuran seimbang
    """
    image_a = image_a.astype(np.float32)
    image_b = image_b.astype(np.float32)

    result = (
        alpha * image_a +
        (1 - alpha) * image_b
    )

    return result.clip(0, 255).astype(np.uint8)


# ============================================================
# 8. HUE TAHAN TERHADAP PERUBAHAN CAHAYA
# ============================================================

def brightness_comparison(rgb):
    """
    Membuat versi gambar lebih gelap dan lebih terang.

    Tujuan:
    membandingkan RGB dan Hue ketika intensitas cahaya berubah.
    """
    dark = (rgb.astype(np.float32) * 0.5).clip(0, 255).astype(np.uint8)
    bright = (rgb.astype(np.float32) * 1.5).clip(0, 255).astype(np.uint8)

    hsv_original = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    hsv_dark = cv2.cvtColor(dark, cv2.COLOR_RGB2HSV)
    hsv_bright = cv2.cvtColor(bright, cv2.COLOR_RGB2HSV)

    return dark, bright, hsv_original[:, :, 0], hsv_dark[:, :, 0], hsv_bright[:, :, 0]


# ============================================================
# 9. MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Cari gambar berdasarkan lokasi script.
    # --------------------------------------------------------

    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
    else:
        image_path = Path(__file__).parent / "gambar.png"

    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        print(f"[ERROR] Gambar tidak ditemukan: {image_path}")
        print()
        print("Contoh:")
        print("python 4-model-warna.py gambar.png")
        return

    print("=" * 60)
    print("MODEL WARNA")
    print("=" * 60)
    print(f"Input : {image_path}")
    print(f"Size  : {image_bgr.shape[1]} x {image_bgr.shape[0]}")

    # --------------------------------------------------------
    # RGB
    # --------------------------------------------------------

    rgb = bgr_to_rgb(image_bgr)

    # --------------------------------------------------------
    # CMYK
    # --------------------------------------------------------

    cmyk = rgb_to_cmyk(rgb)
    c, m, y, k = cv2.split(cmyk)

    # --------------------------------------------------------
    # HSI
    # --------------------------------------------------------

    hsi_h, hsi_s, hsi_i = rgb_to_hsi(rgb)
    hsi_h_display, hsi_s_display, hsi_i_display = (
        hsi_to_display(hsi_h, hsi_s, hsi_i)
    )

    # --------------------------------------------------------
    # HSV
    # --------------------------------------------------------

    hsv = rgb_to_hsv(rgb)
    hsv_h, hsv_s, hsv_v = cv2.split(hsv)

    # --------------------------------------------------------
    # Mask warna
    # --------------------------------------------------------

    red_mask, green_mask, blue_mask = create_color_masks(rgb)

    red_object = apply_mask(rgb, red_mask)
    green_object = apply_mask(rgb, green_mask)
    blue_object = apply_mask(rgb, blue_mask)

    # --------------------------------------------------------
    # Alpha blending
    # --------------------------------------------------------

    # Buat gambar kedua yang diberi sedikit blur.
    blurred = cv2.GaussianBlur(rgb, (0, 0), 5)

    blend = alpha_blend(rgb, blurred, alpha=0.7)

    # --------------------------------------------------------
    # Perbandingan perubahan brightness
    # --------------------------------------------------------

    dark, bright, hue_original, hue_dark, hue_bright = (
        brightness_comparison(rgb)
    )

    # --------------------------------------------------------
    # Simpan hasil
    # --------------------------------------------------------

    results = {
        "01-rgb.jpg": rgb_to_bgr(rgb),

        # CMYK
        "02-cyan.jpg": c,
        "03-magenta.jpg": m,
        "04-yellow.jpg": y,
        "05-key-black.jpg": k,

        # HSI
        "06-hsi-hue.jpg": hsi_h_display,
        "07-hsi-saturation.jpg": hsi_s_display,
        "08-hsi-intensity.jpg": hsi_i_display,

        # HSV
        "09-hsv-hue.jpg": hsv_h,
        "10-hsv-saturation.jpg": hsv_s,
        "11-hsv-value.jpg": hsv_v,

        # Mask
        "12-mask-red.jpg": red_mask,
        "13-mask-green.jpg": green_mask,
        "14-mask-blue.jpg": blue_mask,

        # Hasil mask
        "15-red-object.jpg": rgb_to_bgr(red_object),
        "16-green-object.jpg": rgb_to_bgr(green_object),
        "17-blue-object.jpg": rgb_to_bgr(blue_object),

        # Alpha blending
        "18-alpha-blending.jpg": rgb_to_bgr(blend),

        # Brightness comparison
        "19-dark.jpg": rgb_to_bgr(dark),
        "20-bright.jpg": rgb_to_bgr(bright),
        "21-hue-original.jpg": hue_original,
        "22-hue-dark.jpg": hue_dark,
        "23-hue-bright.jpg": hue_bright,
    }

    for filename, result in results.items():
        cv2.imwrite(filename, result)

    print("\nHasil tersimpan:")
    for filename in results:
        print(" -", filename)

    # --------------------------------------------------------
    # Tampilkan hasil utama
    # --------------------------------------------------------

    cv2.imshow("Original RGB", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    cv2.imshow("HSV - Hue", hsv_h)
    cv2.imshow("HSV - Saturation", hsv_s)
    cv2.imshow("HSV - Value", hsv_v)

    cv2.imshow("Mask - Red", red_mask)
    cv2.imshow("Mask - Green", green_mask)
    cv2.imshow("Mask - Blue", blue_mask)

    cv2.imshow("Alpha Blending", cv2.cvtColor(blend, cv2.COLOR_RGB2BGR))

    print("\nTekan tombol apa saja pada window OpenCV untuk keluar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
