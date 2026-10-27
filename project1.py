import cv2
import numpy as np
import os
from collections import deque
import time

# Ambil direktori absolut tempat file skrip ini berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ukuran viewport per layar game (20x15 tiles = 640x480 piksel)
VIEW_COLS = 20
VIEW_ROWS = 15
TILE_SIZE = 32
WIDTH = VIEW_COLS * TILE_SIZE  # 640
HEIGHT = VIEW_ROWS * TILE_SIZE # 480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# --- LOAD ASSET SPRITE OTOMATIS ---
def load_sprite(filename, default_color):
    full_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(full_path):
        img = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            return cv2.resize(img, (TILE_SIZE, TILE_SIZE))
    fallback = np.full((TILE_SIZE, TILE_SIZE, 3), default_color, dtype=np.uint8)
    return fallback

SPRITES = {
    '0': load_sprite("jalan.png", (220, 240, 220)),
    '1': load_sprite("tembok.png", (30, 100, 30)),
    '2': load_sprite("Boundaries.png", (60, 60, 60)),
    '3': load_sprite("start.png", (255, 200, 100)),
    '4': load_sprite("finish.png", (0, 0, 255)),
    'B': load_sprite("kunci.png", (0, 215, 255)),
    'D': load_sprite("NPC.png", (255, 150, 0)),
    'G': load_sprite("NPC.png", (255, 120, 50)),
    'A': load_sprite("gate.png", (100, 50, 0)),
    'C': load_sprite("gate.png", (100, 50, 0)),
    'F': load_sprite("gate.png", (100, 50, 0)),
    'E': load_sprite("barang.png", (255, 0, 255)),
    'H': load_sprite("barang.png", (255, 0, 255))
}

def draw_tile(canvas, x1, y1, sprite):
    if len(sprite.shape) == 3 and sprite.shape[2] == 4:
        b, g, r, a = cv2.split(sprite)
        overlay = cv2.merge((b, g, r))
        mask = cv2.bitwise_not(a)
        roi = canvas[y1:y1+TILE_SIZE, x1:x1+TILE_SIZE]
        result_bg = cv2.bitwise_and(roi, roi, mask=mask)
        result_fg = cv2.bitwise_and(overlay, overlay, mask=a)
        canvas[y1:y1+TILE_SIZE, x1:x1+TILE_SIZE] = cv2.add(result_bg, result_fg)
    else:
        canvas[y1:y1+TILE_SIZE, x1:x1+TILE_SIZE] = sprite[:, :, :3]

# Raw map string (40 Kolom x 30 Baris)
raw_map_string = """
2222222222222222222222222222222222222222
2300000000000000000000111111111111111112
2000000000000000000000111111111111111112
2111100111111111110000000000000000G01112
2100F00111111111110000000000000000001112
2100111111100000011111111111110011111112
2100111111100000011111111111110011111112
21000011111000H0011111111111110011111112
2111001111100000011111111111110011111112
2111001111100000011111111111110011111112
2111001111100000000000000000000011111112
2100000111100000000000000000000011111112
2100000111111111111110011111110011111112
2100000111111111111110011111110011111112
2100000111111111111110011111110011111112
2100000111111111111110011111110011111112
2100000111111111111110011111110011111112
2100000000000001111110011111110011111112
21D0000000000001111110011111110011111112
2111111111111101111110011111110011111112
2111111111111101111110011111110011111112
2111111111111101111110011111110011111112
2110000011111101111110011111110011111112
211000B011111101111110011111110011111112
2110000011111101111110011111110000000002
21100111111111011111100111111111111111A2
2110011111111101111110011111111111111102
2110000000000C01111110000000000000E01102
2111111111111111111110000000000000001142
2222222222222222222222222222222222222222"""

lines = [line.strip() for line in raw_map_string.strip().split("\n") if line.strip()]
fixed_lines = [line.ljust(40, '0')[:40] for line in lines] 
world_grid = np.array([[char for char in line] for line in fixed_lines], dtype=str)
TOTAL_ROWS, TOTAL_COLS = world_grid.shape 

if TOTAL_ROWS > 4 and TOTAL_COLS > 4:
    world_grid[4, 4] = 'F'
if TOTAL_ROWS > 13 and TOTAL_COLS > 27:
    world_grid[13, 27] = 'C'
if TOTAL_ROWS > 25 and TOTAL_COLS > 38:
    world_grid[25, 38] = 'A'

inventory = {"B": False, "E": False, "H": False}
quest_status = {"D_done": False, "G_done": False}
dialogue_text = "Arahkan sarung tangan ke area ATAS/BAWAH/KIRI/KANAN!"

char_global_pos = [1, 1]

def check_item_pickup():
    global dialogue_text
    gr, gc = char_global_pos[0], char_global_pos[1]
    current_tile = world_grid[gr, gc]
    
    if current_tile == 'B':
        if not inventory["B"]:
            inventory["B"] = True
            world_grid[gr, gc] = '0'
            dialogue_text = "Berhasil mengambil Kunci [B]!"
    elif current_tile == 'E':
        if not inventory["E"]:
            inventory["E"] = True
            world_grid[gr, gc] = '0'
            dialogue_text = "Barang [E] berhasil didapatkan!"
    elif current_tile == 'H':
        if not inventory["H"]:
            inventory["H"] = True
            world_grid[gr, gc] = '0'
            dialogue_text = "Item [H] berhasil didapatkan untuk NPC [G]!"
    elif current_tile == '4':
        dialogue_text = "VICTORY! Game selesai!"

def is_walkable(r, c):
    if 0 <= r < TOTAL_ROWS and 0 <= c < TOTAL_COLS:
        tile = world_grid[r, c]
        solid_ids = {'1', '2', 'A', 'C', 'F'}
        return tile not in solid_ids
    return False

# ==========================================
# FASE 1: KALIBRASI WARNA DI AWAL
# ==========================================
calibrated_lower = None
calibrated_upper = None
is_calibrating = True

print("=== MASUK FASE KALIBRASI WARNA SARUNG TANGAN ===")
print("Arahkan sarung tangan ke kotak hijau di tengah, lalu tekan tombol 'C' untuk merekam warna.")

while cap.isOpened() and is_calibrating:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    
    h, w, _ = frame.shape
    box_size = 60
    x1, y1 = w // 2 - box_size // 2, h // 2 - box_size // 2
    x2, y2 = x1 + box_size, y1 + box_size
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame, "ARAHKAN SARUNG TANGAN KE KOTAK", (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "Tekan 'C' untuk Kalibrasi & Mulai Game", (45, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    cv2.imshow("Kalibrasi Warna Sarung Tangan", frame)
    
    key = cv2.waitKey(30) & 0xFF
    if key == ord('c') or key == ord('C'):
        roi = frame[y1:y2, x1:x2]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        mean_hsv = np.mean(hsv_roi, axis=(0, 1))
        h_val, s_val, v_val = int(mean_hsv[0]), int(mean_hsv[1]), int(mean_hsv[2])
        
        h_margin = 15
        s_margin = 60
        v_margin = 60
        
        calibrated_lower = np.array([max(0, h_val - h_margin), max(50, s_val - s_margin), max(50, v_val - v_margin)], dtype=np.uint8)
        calibrated_upper = np.array([min(180, h_val + h_margin), 255, 255], dtype=np.uint8)
        
        print(f"[KALIBRASI SUKSES] HSV Terdeteksi -> Lower: {calibrated_lower}, Upper: {calibrated_upper}")
        is_calibrating = False
        cv2.destroyWindow("Kalibrasi Warna Sarung Tangan")
    elif key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        exit()

# ==========================================
# FASE 2: GAMEPLAY UTAMA (GRID ZONA NAVIGASI)
# ==========================================
print("Game RPG 2x2 World Active - Kontrol Zona Layar Aktif!")
last_move_time = time.time()
move_delay = 0.3  # Jeda waktu antar langkah

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, calibrated_lower, calibrated_upper)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Visualisasi Garis Pembagi Zona di Layar Webcam (Atas, Bawah, Kiri, Kanan)
    h_s, w_s, _ = frame.shape
    mid_x, mid_y = w_s // 2, h_s // 2
    cv2.line(frame, (mid_x, 0), (mid_x, h_s), (255, 255, 0), 1)
    cv2.line(frame, (0, mid_y), (w_s, mid_y), (255, 255, 0), 1)
    
    hand_direction = "DIAM"
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        c_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c_cnt) > 200:
            M = cv2.moments(c_cnt)
            if M["m00"] > 0:
                px = int(M["m10"] / M["m00"])
                py = int(M["m01"] / M["m00"])
                cv2.circle(frame, (px, py), 12, (0, 0, 255), -1)
                
                # Tentukan arah berdasarkan letak koordinat tangan di kuadran layar
                # Atas: y < mid_y - 40
                # Bawah: y > mid_y + 40
                # Kiri: x < mid_x - 40
                # Kanan: x > mid_x + 40
                threshold = 40
                if py < mid_y - threshold and abs(px - mid_x) < 150:
                    hand_direction = "ATAS"
                elif py > mid_y + threshold and abs(px - mid_x) < 150:
                    hand_direction = "BAWAH"
                elif px < mid_x - threshold and abs(py - mid_y) < 150:
                    hand_direction = "KIRI"
                elif px > mid_x + threshold and abs(py - mid_y) < 150:
                    hand_direction = "KANAN"

    # Eksekusi Gerakan Berdasarkan Zona
    current_time = time.time()
    if current_time - last_move_time > move_delay:
        r, c = char_global_pos[0], char_global_pos[1]
        moved = False
        
        if hand_direction == "ATAS" and is_walkable(r - 1, c):
            char_global_pos[0] -= 1
            moved = True
        elif hand_direction == "BAWAH" and is_walkable(r + 1, c):
            char_global_pos[0] += 1
            moved = True
        elif hand_direction == "KIRI" and is_walkable(r, c - 1):
            char_global_pos[1] -= 1
            moved = True
        elif hand_direction == "KANAN" and is_walkable(r, c + 1):
            char_global_pos[1] += 1
            moved = True
            
        if moved:
            last_move_time = current_time

    check_item_pickup()

    # Interaksi Spasi (untuk NPC / Gate)
    key = cv2.waitKey(30) & 0xFF
    if key == ord(' '):
        gr, gc = char_global_pos[0], char_global_pos[1]
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = gr + dr, gc + dc
            if 0 <= nr < TOTAL_ROWS and 0 <= nc < TOTAL_COLS:
                clicked_tile = world_grid[nr, nc]
                if clicked_tile == 'D':
                    if inventory["E"]:
                        quest_status["D_done"] = True
                        dialogue_text = "NPC D: Misi selesai! Gate C terbuka."
                    else:
                        dialogue_text = "NPC D: Tolong ambil barang E dulu!"
                elif clicked_tile == 'G':
                    if inventory["H"]:
                        quest_status["G_done"] = True
                        dialogue_text = "NPC G: Terimakasih! Gate F terbuka."
                    else:
                        dialogue_text = "NPC G: Tolong ambil item H dulu!"
                elif clicked_tile == 'A' and inventory["B"]:
                    world_grid[nr, nc] = '0'
                    dialogue_text = "Gate A terbuka berkat Kunci B!"
                elif clicked_tile == 'C' and quest_status["D_done"]:
                    world_grid[nr, nc] = '0'
                    dialogue_text = "Gate C terbuka karena NPC D selesai!"
                elif clicked_tile == 'F' and quest_status["G_done"]:
                    world_grid[nr, nc] = '0'
                    dialogue_text = "Gate F terbuka karena NPC G selesai!"

    # Seamless Screen Teleport Logic
    local_c = char_global_pos[1] % VIEW_COLS
    local_r = char_global_pos[0] % VIEW_ROWS
    room_x = char_global_pos[1] // VIEW_COLS
    room_y = char_global_pos[0] // VIEW_ROWS
    
    if local_c == VIEW_COLS - 1 and room_x == 0:
        char_global_pos[1] += 2
    elif local_c == 0 and room_x == 1:
        char_global_pos[1] -= 2
        
    if local_r == VIEW_ROWS - 1 and room_y == 0:
        char_global_pos[0] += 2
    elif local_r == 0 and room_y == 1:
        char_global_pos[0] -= 2

    room_x = char_global_pos[1] // VIEW_COLS
    room_y = char_global_pos[0] // VIEW_ROWS
    start_col = room_x * VIEW_COLS
    start_row = room_y * VIEW_ROWS
    
    game_display = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    for r in range(VIEW_ROWS):
        for c in range(VIEW_COLS):
            g_r = start_row + r
            g_c = start_col + c
            tile_char = world_grid[g_r, g_c]
            x1, y1 = c * TILE_SIZE, r * TILE_SIZE
            sprite = SPRITES.get(tile_char, SPRITES['0'])
            draw_tile(game_display, x1, y1, sprite)

    cv2.putText(frame, f"ZONA: {hand_direction}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    char_local_c = char_global_pos[1] - start_col
    char_local_r = char_global_pos[0] - start_row
    
    if 0 <= char_local_c < VIEW_COLS and 0 <= char_local_r < VIEW_ROWS:
        cx = char_local_c * TILE_SIZE + TILE_SIZE // 2
        cy = char_local_r * TILE_SIZE + TILE_SIZE // 2
        cv2.circle(game_display, (cx, cy), 10, (255, 0, 0), -1) 
        cv2.circle(game_display, (cx, cy), 12, (0, 0, 0), 2)

    cv2.putText(game_display, dialogue_text, (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 3) 
    cv2.putText(game_display, dialogue_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1) 

    combined_view = np.hstack((frame, game_display))
    cv2.imshow("RPG 2x2 World Navigator (Zone Control)", combined_view)
    
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()