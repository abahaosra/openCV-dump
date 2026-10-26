import cv2
import numpy as np
import os
from collections import deque

# Ambil direktori absolut tempat file intro.py ini berada
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
            print(f"[SUCCESS] Berhasil meload asset: {filename}")
            return cv2.resize(img, (TILE_SIZE, TILE_SIZE))
        else:
            print(f"[WARNING] Gagal membaca file gambar {filename}.")
    else:
        print(f"[MISSING] File '{filename}' tidak ditemukan. Memakai warna cadangan.")
        
    fallback = np.full((TILE_SIZE, TILE_SIZE, 3), default_color, dtype=np.uint8)
    return fallback

# Mapping nama file asset berdasarkan permintaanmu
SPRITES = {
    '0': load_sprite("jalan.png", (220, 240, 220)),      # Walkable
    '1': load_sprite("tembok.png", (30, 100, 30)),       # Tembok
    '2': load_sprite("Boundaries.png", (60, 60, 60)),    # Boundary
    '3': load_sprite("start.png", (255, 200, 100)),      # Start
    '4': load_sprite("finish.png", (0, 0, 255)),         # Exit / Finish
    'B': load_sprite("kunci.png", (0, 215, 255)),        # Kunci B
    'D': load_sprite("NPC.png", (255, 150, 0)),          # NPC D
    'G': load_sprite("NPC.png", (255, 120, 50)),         # NPC G (Shared)
    'A': load_sprite("gate.png", (100, 50, 0)),          # Gate A
    'C': load_sprite("gate.png", (100, 50, 0)),          # Gate C (Shared)
    'F': load_sprite("gate.png", (100, 50, 0)),          # Gate F (Shared)
    'E': load_sprite("barang.png", (255, 0, 255)),       # Barang E
    'H': load_sprite("barang.png", (255, 0, 255))        # Item H (Shared)
}

# Fungsi untuk menempelkan sprite ke layar game (mendukung transparansi PNG alpha channel)
def draw_tile(canvas, x1, y1, sprite):
    if len(sprite.shape) == 3 and sprite.shape[2] == 4: # Jika PNG memiliki Alpha Channel
        b, g, r, a = cv2.split(sprite)
        overlay = cv2.merge((b, g, r))
        mask = cv2.bitwise_not(a)
        
        roi = canvas[y1:y1+TILE_SIZE, x1:x1+TILE_SIZE]
        result_bg = cv2.bitwise_and(roi, roi, mask=mask)
        result_fg = cv2.bitwise_and(overlay, overlay, mask=a)
        canvas[y1:y1+TILE_SIZE, x1:x1+TILE_SIZE] = cv2.add(result_bg, result_fg)
    else: # Jika gambar biasa tanpa alpha atau fallback warna
        canvas[y1:y1+TILE_SIZE, x1:x1+TILE_SIZE] = sprite[:, :, :3]

# Raw map string (40 Kolom x 30 Baris)
raw_map_string = """
2222222222222222222222222222222222222222
2300000000000000000000111111111111111112
20000000000000000000G0111111111111111112
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
2100000001111111111110011111110011111112
2100000000011111111110011111110011111112
2100000000000001111110011111110011111112
21D0000000000001111110011111110011111112
2100000000011101111110011111110011111112
2111111111111101111110011111110011111112
2111111111111101111110011111110011111112
2110000011111101111110011111110011111112
211000B011111101111110011111110011111112
2110000011111101111110011111110000000002
21100111111111011111100111111111111111A2
2110011111111101111110011111111111111102
2110000000000001111110000000000000E01102
2111111111111111111110000000000000001142
2222222222222222222222222222222222222222"""

# Auto-Formatting Map
lines = [line.strip() for line in raw_map_string.strip().split("\n") if line.strip()]
fixed_lines = [line.ljust(40, '0')[:40] for line in lines] 

full_map_data = [[char for char in line] for line in fixed_lines]
world_grid = np.array(full_map_data, dtype=str)
TOTAL_ROWS, TOTAL_COLS = world_grid.shape 

if TOTAL_ROWS > 4 and TOTAL_COLS > 4:
    world_grid[4, 4] = 'F'
if TOTAL_ROWS > 13 and TOTAL_COLS > 27:
    world_grid[13, 27] = 'C'
if TOTAL_ROWS > 25 and TOTAL_COLS > 38:
    world_grid[25, 38] = 'A'

inventory = {"B": False, "E": False, "H": False}
quest_status = {"D_done": False, "G_done": False}
dialogue_text = "Full Sprite Textures Loaded!"

char_global_pos = [1, 1]
current_path = []

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

def bfs_path(start, goal, grid):
    sr, sc = start
    gr, gc = goal
    solid_ids = {'1', '2', 'A', 'C', 'F'}
    if grid[gr, gc] in solid_ids:
        return []
    queue = deque([(sr, sc)])
    parent = {(sr, sc): None}
    while queue:
        r, c = queue.popleft()
        if (r, c) == (gr, gc):
            path = []
            curr = (gr, gc)
            while curr:
                path.append(curr)
                curr = parent[curr]
            return path[::-1]
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < TOTAL_ROWS and 0 <= nc < TOTAL_COLS:
                if grid[nr, nc] not in solid_ids and (nr, nc) not in parent:
                    parent[(nr, nc)] = (r, c)
                    queue.append((nr, nc))
    return []

space_pressed_last_frame = False

print("Game RPG 2x2 World Active - Full Sprite Mode!")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    lower_red1, upper_red1 = np.array([0, 100, 100]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([170, 100, 100]), np.array([180, 255, 255])
    mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    local_c = char_global_pos[1] % VIEW_COLS
    local_r = char_global_pos[0] % VIEW_ROWS
    room_x = char_global_pos[1] // VIEW_COLS
    room_y = char_global_pos[0] // VIEW_ROWS
    
    if local_c == VIEW_COLS - 1 and room_x == 0:
        char_global_pos[1] += 2
        current_path.clear()
    elif local_c == 0 and room_x == 1:
        char_global_pos[1] -= 2
        current_path.clear()
        
    if local_r == VIEW_ROWS - 1 and room_y == 0:
        char_global_pos[0] += 2
        current_path.clear()
    elif local_r == 0 and room_y == 1:
        char_global_pos[0] -= 2
        current_path.clear()

    room_x = char_global_pos[1] // VIEW_COLS
    room_y = char_global_pos[0] // VIEW_ROWS
    start_col = room_x * VIEW_COLS
    start_row = room_y * VIEW_ROWS
    
    game_display = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    # Render Viewport Room 20x15 menggunakan Sprite PNG
    for r in range(VIEW_ROWS):
        for c in range(VIEW_COLS):
            g_r = start_row + r
            g_c = start_col + c
            tile_char = world_grid[g_r, g_c]
            
            x1, y1 = c * TILE_SIZE, r * TILE_SIZE
            
            # Ambil sprite yang sesuai dari dictionary SPRITES, jika tidak ada pakai '0'
            sprite = SPRITES.get(tile_char, SPRITES['0'])
            draw_tile(game_display, x1, y1, sprite)

    pointer_global_r, pointer_global_c = -1, -1
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c_cnt) > 150:
            M = cv2.moments(c_cnt)
            if M["m00"] > 0:
                px = int(M["m10"] / M["m00"])
                py = int(M["m01"] / M["m00"])
                cv2.circle(frame, (px, py), 8, (0, 0, 255), -1)
                view_c = px // TILE_SIZE
                view_r = py // TILE_SIZE
                pointer_global_c = start_col + view_c
                pointer_global_r = start_row + view_r
                hx1, hy1 = view_c * TILE_SIZE, view_r * TILE_SIZE
                cv2.rectangle(game_display, (hx1, hy1), (hx1 + TILE_SIZE, hy1 + TILE_SIZE), (0, 255, 255), 2)

    if current_path and len(current_path) > 1:
        next_step = current_path[1]
        char_global_pos[0], char_global_pos[1] = next_step
        current_path.pop(0)
        
    check_item_pickup()

    key = cv2.waitKey(30) & 0xFF
    space_is_down = (key == ord(' '))
    
    if space_is_down and not space_pressed_last_frame:
        if 0 <= pointer_global_r < TOTAL_ROWS and 0 <= pointer_global_c < TOTAL_COLS:
            pr, pc = pointer_global_r, pointer_global_c
            clicked_tile = world_grid[pr, pc]
            
            if clicked_tile == 'D':
                if inventory["E"]:
                    quest_status["D_done"] = True
                    dialogue_text = "NPC D: Misi selesai! Gate C terbuka."
                else:
                    dialogue_text = "NPC D: Tolong ambil barang E di [34,27] dulu!"
            elif clicked_tile == 'G':
                if inventory["H"]:
                    quest_status["G_done"] = True
                    dialogue_text = "NPC G: Terimakasih! Gate F terbuka."
                else:
                    dialogue_text = "NPC G: Tolong ambil item H di [14,7] dulu!"
            elif clicked_tile in ['A', 'C', 'F']:
                if clicked_tile == 'A':
                    if inventory["B"]:
                        world_grid[pr, pc] = '0'
                        dialogue_text = "Gate A terbuka berkat Kunci B!"
                    else:
                        dialogue_text = "Terkunci! Butuh Kunci B dari [6,23]."
                elif clicked_tile == 'C':
                    if quest_status["D_done"]:
                        world_grid[pr, pc] = '0'
                        dialogue_text = "Gate C terbuka karena NPC D selesai!"
                    else:
                        dialogue_text = "Terkunci! Selesaikan misi NPC D dulu."
                elif clicked_tile == 'F':
                    if quest_status["G_done"]:
                        world_grid[pr, pc] = '0'
                        dialogue_text = "Gate F terbuka karena NPC G selesai!"
                    else:
                        dialogue_text = "Terkunci! Selesaikan misi NPC G dulu."
            else:
                new_path = bfs_path(tuple(char_global_pos), (pr, pc), world_grid)
                if new_path:
                    current_path = new_path
                    
    space_pressed_last_frame = space_is_down

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
    cv2.imshow("RPG 2x2 World Navigator (Webcam | Game Board)", combined_view)
    
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()