# 🎮 OpenCV 2x2 World RPG Navigator

> Game petualangan RPG berbasis Python dan OpenCV dengan sistem navigasi interaktif berbasis *color tracking* (deteksi warna via sarung tangan/objek), mekanik *seamless screen teleport*, serta sistem *quest* dan inventaris berbasis matriks dunia.

---

## 📌 Ringkasan / Deskripsi Proyek

**OpenCV 2x2 World RPG Navigator** adalah proyek game edukasi dan eksperimental yang menggabungkan pemrograman visi komputer (*computer vision*) dengan logika game RPG klasik. Proyek ini dibangun untuk mengeksplorasi bagaimana input visual dari *webcam* (seperti gerakan sarung tangan berwarna kontras) dapat diterjemahkan menjadi kendali kursor di layar, dipadukan dengan algoritma *pathfinding* BFS (*Breadth-First Search*) untuk navigasi karakter secara otomatis di dalam dunia grid berukuran 40x30 petak (dibagi dalam ruang 2x2 layar).

Proyek ini mengatasi tantangan interaksi non-konvensional dengan memanfaatkan pemrosesan citra *real-time*, memungkinkan pemain untuk bernavigasi, mengambil inventaris, menyelesaikan misi NPC, dan membuka gerbang penutup tanpa memerlukan kendali tetikus atau papan ketik tradisional.

---

## ✨ Fitur Utama

* **🎯 Color Tracking Input**: Memanfaatkan *webcam* dan ruang warna HSV untuk mendeteksi objek berwarna khusus (misalnya menggunakan sarung tangan berwarna kontras) sebagai kursor interaktif di layar.
* **🗺️ Seamless Screen Teleport**: Perpindahan antar ruangan secara mulus dan otomatis saat karakter mencapai batas tepi layar (*viewport* 20x15 per layar).
* **🤖 Automated Pathfinding (BFS)**: Karakter dapat menentukan dan melangkah secara otomatis menuju petak tujuan yang diklik menggunakan algoritma *Breadth-First Search*.
* **🎒 Quest & Inventory System**: Sistem quest berantai yang melibatkan pengambilan kunci (`B`), barang/item quest (`E`, `H`), interaksi NPC (`D`, `G`), dan pembukaan gerbang bersyarat (`A`, `C`, `F`).
* **🖼️ Sprite Texture Rendering**: Mendukung rendering aset gambar PNG kustom lengkap dengan manajemen transparansi (*alpha channel*) menggunakan penggabungan matriks NumPy dan OpenCV.

---

## 💻 Teknologi & Alat yang Digunakan

* **Bahasa Pemrograman**: Python 3.x
* **Computer Vision & GUI**: OpenCV (`cv2`)
* **Pengolahan Data & Matriks**: NumPy
* **Struktur Logika**: Collections (`deque`)
* **Tools / Environment**: Visual Studio Code (VS Code), Git / GitHub

---

## 📋 Prasyarat Sistem

Sebelum menjalankan aplikasi, pastikan perangkat Anda telah memenuhi prasyarat berikut:
* **Python**: Versi 3.8 atau yang lebih baru terinstal di sistem.
* **Webcam**: Perangkat keras kamera web yang berfungsi dengan baik.
* **Pencahayaan & Sarung Tangan/Objek**: Ruangan dengan pencahayaan yang memadai untuk mendeteksi warna sarung tangan atau objek pelacak secara akurat.

---

## ⚙️ Panduan Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini untuk mengatur dan menjalankan proyek secara lokal:

1. **Clone repository ini:**
git clone https://github.com/abahaosra/openCV-dump.git

**Install opencv**
pip install opencv-python numpy

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

## 📂 Struktur Direktori

📦 C:\Users\gante\OneDrive\Documents\PCV\
 ┣ 📜 intro.py            # Skrip utama permainan & logika OpenCV
 ┣ 🖼️ jalan.png           # Aset sprite jalan
 ┣ 🖼️ tembok.png          # Aset sprite tembok
 ┣ 🖼️ Boundaries.png      # Aset sprite batas map
 ┣ 🖼️ start.png           # Aset sprite zona awal
 ┣ 🖼️ finish.png          # Aset sprite zona akhir / exit
 ┣ 🖼️ kunci.png           # Aset sprite kunci (B)
 ┣ 🖼️ NPC.png             # Aset sprite NPC (D & G)
 ┣ 🖼️ gate.png            # Aset sprite gerbang (A, C, F)
 ┣ 🖼️ barang.png          # Aset sprite barang/item (E & H)
 ┗ 📖 README.md           # Dokumentasi proyek