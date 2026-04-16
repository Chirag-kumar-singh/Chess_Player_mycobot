import cv2
import numpy as np
from stockfish import Stockfish
import time

# ---------------- CONFIG ----------------
SIZE = 800
CELL = SIZE // 8
DETECT_SIZE = int(CELL * 0.6)
OFFSET = (CELL - DETECT_SIZE) // 2

FRAMES = 10
THRESHOLD = 6
# ----------------------------------------

H = np.load("H.npy")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BRIGHTNESS, -40.0)

engine = Stockfish(path="/usr/games/stockfish")

# 🔥 MOVE HISTORY (IMPORTANT)
moves = []


# ---------------- DETECTION ----------------
def detect_grid(warped):
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
    value_channel = hsv[:, :, 2]

    grid = np.zeros((8, 8), dtype=int)

    for r in range(8):
        for c in range(8):

            x_start = c * CELL + OFFSET
            y_start = r * CELL + OFFSET

            square = hsv[
                y_start:y_start + DETECT_SIZE,
                x_start:x_start + DETECT_SIZE
            ]

            mask = cv2.inRange(
                square,
                np.array([35, 40, 40]),
                np.array([85, 255, 255])
            )

            not_green = cv2.bitwise_not(mask)

            piece_pixels = cv2.countNonZero(not_green)
            total_pixels = square.shape[0] * square.shape[1]

            if piece_pixels / total_pixels > 0.3:

                value_square = value_channel[
                    y_start:y_start + DETECT_SIZE,
                    x_start:x_start + DETECT_SIZE
                ]

                piece_mask = not_green > 0

                if np.any(piece_mask):
                    mean_val = np.mean(value_square[piece_mask])

                    if mean_val > 100:
                        grid[r][c] = 1  # white
                    else:
                        grid[r][c] = 2  # black

    return grid


# ---------------- STABLE GRID ----------------
def stable_grid_detection():
    grids = []

    print("Capturing frames...")

    for _ in range(FRAMES):
        ret, frame = cap.read()
        if not ret:
            continue

        warped = cv2.warpPerspective(frame, H, (SIZE, SIZE))
        grid = detect_grid(warped)

        grids.append(grid)
        time.sleep(0.1)

    grids = np.array(grids)

    final_grid = np.zeros((8, 8), dtype=int)

    for r in range(8):
        for c in range(8):

            values, counts = np.unique(grids[:, r, c], return_counts=True)

            if len(counts) > 0:
                max_idx = np.argmax(counts)

                if counts[max_idx] >= THRESHOLD:
                    final_grid[r][c] = values[max_idx]

    return np.flipud(final_grid)


# ---------------- MOVE LOGIC ----------------
def index_to_chess(r, c):
    return chr(ord('a') + c) + str(8 - r)


def detect_move(prev, curr):
    from_sq = None
    to_sq = None

    for r in range(8):
        for c in range(8):

            if prev[r][c] != curr[r][c]:

                if prev[r][c] != 0 and curr[r][c] == 0:
                    from_sq = (r, c)

                elif curr[r][c] != 0:
                    to_sq = (r, c)

    if from_sq and to_sq:
        return index_to_chess(*from_sq) + index_to_chess(*to_sq)

    return None


# ---------------- MAIN LOOP ----------------
previous_grid = None

print("\n🎮 Chess Vision System (Move-based)")
print("Press 'n' → capture move")
print("Press 'q' → quit\n")

while True:
    key = input("Command: ")

    if key == 'q':
        break

    if key == 'n':

        print("\n⏳ Wait... remove your hand")
        time.sleep(2)

        current_grid = stable_grid_detection()

        print("\n📊 Grid:\n", current_grid)

        # FIRST FRAME (INITIALIZE)
        if previous_grid is None:
            print("\n✅ Initial board captured")
            previous_grid = current_grid
            continue

        # DETECT MOVE
        move = detect_move(previous_grid, current_grid)

        if move:
            print("\n♟️ Detected Move:", move)

            moves.append(move)

            # 🔥 SEND MOVES (NOT FEN)
            engine.set_position(moves)

            best_move = engine.get_best_move()

            print("🤖 Stockfish Move:", best_move)

        else:
            print("\n⚠️ No valid move detected")

        previous_grid = current_grid

cap.release()