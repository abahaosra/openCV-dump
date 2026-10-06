

import sys
import cv2
import numpy as np


# ============================================================
# 1. KONVOLUSI VS KORELASI
# ============================================================

def correlation(image, kernel):
    """
    Korelasi 2D manual.
    Kernel TIDAK dibalik.
    """
    kernel = np.asarray(kernel, dtype=np.float32)
    kh, kw = kernel.shape

    pad_y, pad_x = kh // 2, kw // 2
    padded = cv2.copyMakeBorder(
        image, pad_y, pad_y, pad_x, pad_x,
        borderType=cv2.BORDER_REFLECT
    )

    result = np.zeros_like(image, dtype=np.float32)

    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            region = padded[y:y + kh, x:x + kw]
            result[y, x] = np.sum(region * kernel)

    return result


def convolution(image, kernel):
    """
    Konvolusi 2D manual.
    Kernel DIBALIK 180 derajat terlebih dahulu.
    """
    flipped_kernel = np.flip(kernel)
    return correlation(image, flipped_kernel)


# ============================================================
# 2. FILTER SPASIAL
# ============================================================

def mean_filter(image, kernel_size=5):
    """Mean/Average filter."""
    return cv2.blur(
        image,
        (kernel_size, kernel_size),
        borderType=cv2.BORDER_REFLECT
    )


def gaussian_filter(image, kernel_size=5, sigma=0):
    """Gaussian smoothing."""
    return cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        sigmaX=sigma,
        borderType=cv2.BORDER_REFLECT
    )


def median_filter(image, kernel_size=5):
    """Median filter."""
    return cv2.medianBlur(image, kernel_size)


# ============================================================
# 3. EDGE DETECTION
# ============================================================

def sobel_filter(image):
    """
    Sobel X dan Y, kemudian magnitude gradien.
    """
    sobel_x = cv2.Sobel(
        image, cv2.CV_64F, 1, 0,
        ksize=3,
        borderType=cv2.BORDER_REFLECT
    )

    sobel_y = cv2.Sobel(
        image, cv2.CV_64F, 0, 1,
        ksize=3,
        borderType=cv2.BORDER_REFLECT
    )

    magnitude = cv2.magnitude(
        sobel_x.astype(np.float32),
        sobel_y.astype(np.float32)
    )

    magnitude = cv2.normalize(
        magnitude, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)

    return magnitude


def laplacian_filter(image):
    """Laplacian edge detection."""
    lap = cv2.Laplacian(
        image,
        cv2.CV_64F,
        ksize=3,
        borderType=cv2.BORDER_REFLECT
    )

    lap = np.absolute(lap)
    lap = cv2.normalize(
        lap, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)

    return lap


# ============================================================
# 4. UNSHARP MASKING
# ============================================================

def unsharp_mask(image, amount=1.5, sigma=1.0):
    """
    Sharpening dengan Unsharp Masking.

    1. Blur gambar
    2. Hitung mask = gambar - blur
    3. Tambahkan mask ke gambar
    """
    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=sigma
    )

    sharpened = cv2.addWeighted(
        image, 1 + amount,
        blurred, -amount,
        0
    )

    return sharpened


# ============================================================
# 5. DEMO PADDING
# ============================================================

def show_padding_demo(image):
    """
    Menampilkan beberapa jenis padding pada citra.
    """
    h, w = image.shape

    pad = 30

    constant = cv2.copyMakeBorder(
        image, pad, pad, pad, pad,
        cv2.BORDER_CONSTANT,
        value=0
    )

    replicate = cv2.copyMakeBorder(
        image, pad, pad, pad, pad,
        cv2.BORDER_REPLICATE
    )

    reflect = cv2.copyMakeBorder(
        image, pad, pad, pad, pad,
        cv2.BORDER_REFLECT
    )

    reflect101 = cv2.copyMakeBorder(
        image, pad, pad, pad, pad,
        cv2.BORDER_REFLECT_101
    )

    return constant, replicate, reflect, reflect101


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

def main():

    # --------------------------------------------------------
    # Baca gambar
    # --------------------------------------------------------

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "gambar.png"

    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print(f"[ERROR] Gambar '{filename}' tidak ditemukan.")
        return

    print("=" * 60)
    print("FILTER SPASIAL")
    print("=" * 60)
    print(f"Input : {filename}")
    print(f"Size  : {image.shape[1]} x {image.shape[0]}")

    # --------------------------------------------------------
    # Konvolusi vs Korelasi
    # --------------------------------------------------------

    kernel = np.array([
        [1,  2,  1],
        [0,  0,  0],
        [-1, -2, -1]
    ], dtype=np.float32)

    correlation_result = correlation(image, kernel)
    convolution_result = convolution(image, kernel)

    # Normalisasi agar bisa ditampilkan
    correlation_display = cv2.normalize(
        np.abs(correlation_result),
        None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)

    convolution_display = cv2.normalize(
        np.abs(convolution_result),
        None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)

    # --------------------------------------------------------
    # Smoothing
    # --------------------------------------------------------

    mean = mean_filter(image, 5)
    gaussian = gaussian_filter(image, 5, 1.0)
    median = median_filter(image, 5)

    # --------------------------------------------------------
    # Edge detection
    # --------------------------------------------------------

    sobel = sobel_filter(image)
    laplacian = laplacian_filter(image)

    # --------------------------------------------------------
    # Sharpening
    # --------------------------------------------------------

    unsharp = unsharp_mask(image, amount=1.5, sigma=1.0)

    # --------------------------------------------------------
    # Padding
    # --------------------------------------------------------

    constant, replicate, reflect, reflect101 = show_padding_demo(image)

    # --------------------------------------------------------
    # Simpan hasil
    # --------------------------------------------------------

    results = {
        "01_original.jpg": image,
        "02_correlation.jpg": correlation_display,
        "03_convolution.jpg": convolution_display,
        "04_mean.jpg": mean,
        "05_gaussian.jpg": gaussian,
        "06_median.jpg": median,
        "07_sobel.jpg": sobel,
        "08_laplacian.jpg": laplacian,
        "09_unsharp.jpg": unsharp,
        "10_padding_constant.jpg": constant,
        "11_padding_replicate.jpg": replicate,
        "12_padding_reflect.jpg": reflect,
        "13_padding_reflect101.jpg": reflect101,
    }

    for filename, result in results.items():
        cv2.imwrite(filename, result)

    print("\nHasil tersimpan:")
    for filename in results:
        print(" -", filename)

    # --------------------------------------------------------
    # Tampilkan hasil
    # --------------------------------------------------------

    cv2.imshow("Original", image)
    cv2.imshow("Mean Filter", mean)
    cv2.imshow("Gaussian Filter", gaussian)
    cv2.imshow("Median Filter", median)
    cv2.imshow("Sobel", sobel)
    cv2.imshow("Laplacian", laplacian)
    cv2.imshow("Unsharp Mask", unsharp)

    print("\nTekan tombol apa saja pada window OpenCV untuk keluar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
