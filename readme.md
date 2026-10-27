# 🎮 OpenCV 2x2 World RPG Navigator

> Game petualangan RPG berbasis Python dan OpenCV dengan sistem navigasi interaktif berbasis *color tracking* dan kontrol zona gestur sarung tangan, dilengkapi fase kalibrasi warna dinamis, mekanik *seamless screen teleport*, serta sistem *quest* dan inventaris berbasis matriks dunia.

---

## 📌 Ringkasan / Deskripsi Proyek

**OpenCV 2x2 World RPG Navigator** adalah proyek game edukasi dan eksperimental yang menggabungkan pemrograman visi komputer (*computer vision*) dengan logika game RPG klasik. Proyek ini dibangun untuk mengeksplorasi bagaimana input visual dari *webcam* (menggunakan sarung tangan berwarna kontras) dapat diterjemahkan menjadi kendali arah navigasi secara *hands-free*. 

Pemain dapat melakukan kalibrasi warna sarung tangan secara mandiri di awal permainan, lalu mengontrol pergerakan karakter (Atas, Bawah, Kiri, Kanan) berdasarkan kuadran zona di layar kamera, menjelajahi peta grid 40x30 petak dalam ruang 2x2 layar, serta menyelesaikan berbagai misi NPC dan inventaris.

---

## ✨ Fitur Utama

- **🎨 Dynamic HSV Color Calibration**: Fitur kalibrasi awal di mana pemain dapat merekam warna sarung tangan secara akurat sesuai kondisi pencahayaan ruangan (*real-time sampling*).
- **🕹️ Screen Zone Motion Control**: Sistem kendali arah gerak karakter (Atas, Bawah, Kiri, Kanan) berdasarkan posisi koordinat sarung tangan di kuadran zona layar webcam.
- **🗺️ Seamless Screen Teleport**: Perpindahan antar ruangan secara mulus dan otomatis saat karakter mencapai batas tepi layar (*viewport* 20x15 per layar).
- **🎒 Quest & Inventory System**: Sistem quest berantai yang melibatkan pengambilan kunci (`B`), barang/item quest (`E`, `H`), interaksi NPC (`D`, `G`), dan pembukaan gerbang bersyarat (`A`, `C`, `F`).
- **🖼️ Sprite Texture Rendering**: Mendukung rendering aset gambar PNG kustom lengkap dengan manajemen transparansi (*alpha channel*) menggunakan penggabungan matriks NumPy dan OpenCV.

---

## 💻 Teknologi & Alat yang Digunakan

- **Bahasa Pemrograman**: Python 3.x
- **Computer Vision & GUI**: OpenCV (`cv2`)
- **Pengolahan Data & Matriks**: NumPy
- **Struktur Logika**: Collections (`deque`), Time
- **Tools / Environment**: Visual Studio Code (VS Code), Git / GitHub

---

## 📋 Prasyarat Sistem

Sebelum menjalankan aplikasi, pastikan perangkat Anda telah memenuhi prasyarat berikut:
- **Python**: Versi 3.8 atau yang lebih baru terinstal di sistem.
- **Webcam**: Perangkat keras kamera web yang berfungsi dengan baik.
- **Pencahayaan & Sarung Tangan**: Ruangan dengan pencahayaan yang memadai dan sarung tangan berwarna kontras untuk proses kalibrasi.

---

## ⚙️ Panduan Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini untuk mengatur dan menjalankan proyek secara lokal:

1. **Clone repository ini:**
*git clone https://github.com/abahaosra/openCV-dump.git

**Install opencv**
*pip install opencv-python numpy

3. **Persiapkan Aset Game:**
Pastikan file-file gambar aset berikut berukuran **32x32 piksel** dan tersimpan di dalam direktori yang sama dengan `intro.py`:
* `jalan.png` (Tile jalan / `0`)
* `tembok.png` (Tembok / `1`)
* `Boundaries.png` (Batas / `2`)
* `start.png` (Start / `3`)
* `finish.png` (Exit / `4`)
* `kunci.png` (Kunci B)
* `NPC.png` (NPC D & G)
* `gate.png` (Gate A, C, F)
* `barang.png` (Barang E & Item H)

