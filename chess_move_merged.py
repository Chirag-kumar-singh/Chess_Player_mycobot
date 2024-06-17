from pymycobot.mycobot import MyCobot
import cv2
import numpy as np
from stockfish import Stockfish
import time
import sys
import os

# ============================================================
#  CONFIG
# ============================================================
PORT = "/dev/ttyTHS1"
BAUD = 1000000
SPEED = 10
STEP = 1

GRIP_OPEN = 30  # open (resting / releasing)
GRIP_OPEN_ZERO = 40  # open wide (ready to grip piece)
GRIP_CLOSE = 0  # closed (gripping piece)
GRIP_SPEED = 50

# Vision
CAM_SIZE = 800
CELL = CAM_SIZE // 8
DETECT_SIZE = int(CELL * 0.6)
OFFSET = (CELL - DETECT_SIZE) // 2
FRAMES = 10
THRESHOLD = 6

# Save path for debug images / logs
DEBUG_DIR = "chess_debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

# ============================================================
#  JOINT LIMITS
# ============================================================
LIMITS = [
    (-168, 168),
    (-140, 140),
    (-150, 150),
    (-150, 150),
    (-155, 160),
    (-180, 180),
]


def clamp(angles):
    return [max(min(a, mx), mn) for a, (mn, mx) in zip(angles, LIMITS)]


# ============================================================
#  POSITION MAP
#  Key format: "<col><row>"  col: a=1...h=8, row: rank8=1...rank1=8
#  "11" = a8 (top-left from white's perspective)
#  "88" = h1 (bottom-right from white's perspective)
# ============================================================
position_map = {
    "11": [-4, -71, -8, -1, -1, 40],
    "21": [3, -67, -14, -2, -1, 49],  # wrong
    "31": [6.279999999999999, -66.59, -11.82, -3.0, 1.7000000000000002, 48.92],  # wrong
    "41": [4.279999999999999, -69.59, -12.82, 1.0, 7.699999999999999, 53.92],
    "51": [9.28, -65.59, -20.82, 5.0, 7.699999999999999, 47.92],
    "61": [19.28, -64.59, -21.82, 5.0, 3.6999999999999993, 60.92],  # wrong
    "71": [31.28, -44.54, -65.06, 33.85, -8.43, 72.96],
    "81": [30.91, -50.17, -55.65, 31.92, -1.6099999999999994, 72.57],
    "12": [
        -7.129999999999999,
        -64.46000000000001,
        -20.560000000000002,
        0.16000000000000014,
        -0.16999999999999993,
        37.7,
    ],
    "22": [
        -0.129999999999999,
        -61.46000000000001,
        -25.560000000000002,
        1.1600000000000001,
        -0.16999999999999993,
        37.7,
    ],
    "32": [
        5.870000000000001,
        -61.46000000000001,
        -26.560000000000002,
        -1.8399999999999999,
        -0.16999999999999993,
        49.7,
    ],
    "42": [
        12.870000000000001,
        -61.46000000000001,
        -23.560000000000002,
        -4.84,
        -1.17,
        58.7,
    ],  # falling
    "52": [20.87, -52.46000000000001, -41.56, 6.16, -3.17, 65.7],
    "62": [21.28, -56.59, -36.82, 7.0, 3.6999999999999993, 64.92],
    "72": [28.28, -55.59, -36.82, 7.0, 0.6999999999999993, 73.92],
    "82": [30.49, -75.33, 2.6000000000000014, -16.010000000000005, 4.7, 71.03],
    "13": [
        -9.129999999999999,
        -42.46000000000001,
        -67.56,
        28.16,
        0.8300000000000001,
        37.7,
    ],
    "23": [-1.129999999999999, -30.460000000000008, -90, 43.16, -1.17, 41.7],
    "33": [5.870000000000001, -30.460000000000008, -90, 40.16, -1.17, 48.7],
    "43": [13.870000000000001, -30.460000000000008, -90, 38.16, -2.17, 55.7],
    "53": [19.87, -28.460000000000008, -90, 37.16, -2.17, 64.7],  # stucking
    "63": [27.98, -29.35, -90, 37.89, -3.81, 72.07],  # stucking
    "73": [28.28, -49.59, -46.82, 7.0, 3.6999999999999993, 73.92],
    "83": [35.28, -52.59, -41.82, 6.0, 2.6999999999999993, 79.92],
    "14": [
        -9.129999999999999,
        -34.46000000000001,
        -79.56,
        28.16,
        0.8300000000000001,
        37.7,
    ],
    "24": [
        -1.129999999999999,
        -29.460000000000008,
        -89.56,
        33.16,
        -0.16999999999999993,
        43.7,
    ],
    "34": [
        6.870000000000001,
        -29.460000000000008,
        -90,
        32.159999999999997,
        -1.17,
        49.7,
    ],
    "44": [
        12.870000000000001,
        -29.460000000000008,
        -88,
        30.159999999999997,
        -1.17,
        59.7,
    ],  # stucking
    "54": [19.87, -25.460000000000008, -95, 34.16, 1.83, 65.7],  # stucking
    "64": [27.98, -24.35, -97, 37.89, 0.1899999999999995, 72.07],  # stucking
    "74": [28.28, -47.59, -52.82, 4.0, 7.699999999999999, 73.92],  # stucking
    "84": [34.28, -37.59, -70.82, 19.0, 6.699999999999999, 79.92],
    "15": [
        -10.129999999999999,
        -30.460000000000008,
        -83.56,
        25.159999999999997,
        -0.16999999999999993,
        35.7,
    ],
    "25": [
        0.870000000000001,
        -29.460000000000008,
        -88,
        25.159999999999997,
        -2.17,
        46.7,
    ],
    "35": [
        9.870000000000001,
        -29.460000000000008,
        -87,
        22.159999999999997,
        -3.17,
        53.7,
    ],
    "45": [
        15.870000000000001,
        -29.460000000000008,
        -88,
        22.159999999999997,
        -1.17,
        59.7,
    ],
    "55": [
        22.87,
        -29.460000000000008,
        -89,
        20.159999999999997,
        -0.16999999999999993,
        86.7,
    ],  # stucking
    "65": [29.98, -16.35, -110, 39.89, 1.1899999999999995, 75.07],  # stucking
    "75": [
        37.980000000000004,
        -17.35,
        -106,
        37.89,
        0.1899999999999995,
        84.07,
    ],  # stucking
    "85": [
        37.28,
        -29.590000000000003,
        -87.82,
        26.0,
        6.699999999999999,
        81.92,
    ],  # stucking
    "16": [
        -10.129999999999999,
        -32.46000000000001,
        -83,
        19.159999999999997,
        -2.17,
        35.7,
    ],
    "26": [0.87, -27.46, -88.5, 17.16, -2.17, 46.7],
    "36": [6.869999999999999, -31.46, -86.5, 16.16, -0.16999999999999993, 53.7],
    "46": [13.87, -28.46, -88, 15.16, 1.83, 61.7],
    "56": [
        28.87,
        -25.460000000000008,
        -90,
        14.159999999999997,
        -0.16999999999999993,
        68.7,
    ],
    "66": [
        26.870000000000005,
        -29.460000000000008,
        -90,
        19.159999999999997,
        6.83,
        70.7,
    ],  # falling
    "76": [
        44.980000000000004,
        -12.350000000000001,
        -115,
        38.89,
        1.1899999999999995,
        88.07,
    ],  # stucking
    "86": [40.28, -21.590000000000003, -100.82, 32.0, 8.7, 88.92],
    "17": [-10.13, -33.46, -82.44, 12.16, -4.17, 35.7],  # distorting
    "27": [0.0, -0.3500000000000014, -130, 43.45, -2.8599999999999994, 45.35],
    "37": [
        13.0,
        3.6499999999999986,
        -134,
        40.45,
        -2.8599999999999994,
        57.35,
    ],  # stucking
    "47": [
        23.0,
        5.649999999999999,
        -136,
        41.45,
        -1.8599999999999994,
        67.35,
    ],  # stucking
    "57": [
        31.0,
        5.649999999999999,
        -136,
        41.45,
        0.14000000000000057,
        74.35,
    ],  # stucking
    "67": [
        42.0,
        5.649999999999999,
        -136,
        41.45,
        -0.8599999999999994,
        85.35,
    ],  # stucking
    "77": [52.0, 4.649999999999999, -136, 44.45, -2.8599999999999994, 98.35],  # falling
    "87": [
        60.0,
        4.649999999999999,
        -139,
        51.45,
        -2.8599999999999994,
        103.35,
    ],  # fallingr(77)
    "18": [-10.0, 8.649999999999999, -140, 44.45, -2.8599999999999994, 34.35],
    "28": [0.0, 5.649999999999999, -142, 46.45, -2.8599999999999994, 45.35],
    "38": [15.0, 13.649999999999999, -140, 33.45, -2.8599999999999994, 59.35],
    "48": [32.0, 14.649999999999999, -143, 33.45, -1.8599999999999994, 78.35],
    "58": [
        40.0,
        14.649999999999999,
        -141,
        32.45,
        -0.8599999999999994,
        85.35,
    ],  # stucking
    "68": [
        65.0,
        24.65,
        -145,
        25.450000000000003,
        -4.859999999999999,
        111.35,
    ],  # falling(78)
    "78": [
        69.0,
        35.65,
        -150,
        25.450000000000003,
        -1.8599999999999994,
        114.35,
    ],  # stucking(88)
    "88": [69.0, 10.649999999999999, -137, 37.45, -0.8599999999999994, 113.35],
    "camera": [32.120000000000005, -7.47, -52.38, -20.74, 2.81, 75.43],  # fallingr(78)
}

# ============================================================
#  CAPTURED PIECE DROP ZONE
#  TODO: calibrate — move arm over discard pile, read
#  mc.get_angles(), paste result here.
# ============================================================
CAPTURED_ZONE_ANGLES = None  # e.g. [10, -20, -60, 30, 5, 90]

BACK_POSITION = [32.12, -7.47, -52.38, -20.74, 4.81, 75.43]


# ============================================================
#  CHESS COORDINATE MAPPING
#  "e2" -> col=5, row=2 -> key "52"
# ============================================================
def chess_to_key(square: str) -> str:
    col = ord(square[0]) - ord("a") + 1
    row = int(square[1])
    return f"{col}{row}"


def index_to_chess(r, c):
    file = chr(ord("h") - c)
    rank = str(r + 1)
    return file + rank


# ============================================================
#  VISION  — exact logic from your working detection script
# ============================================================
def detect_grid_from_frame(warped):
    """
    Exact piece detection from your reference script.
    Returns (grid 8x8, debug_image with coloured boxes).
    """
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
    value_channel = hsv[:, :, 2]

    debug = warped.copy()
    grid = np.zeros((8, 8), dtype=int)

    for r in range(8):
        for c in range(8):
            x_start = c * CELL + OFFSET
            y_start = r * CELL + OFFSET

            square = hsv[
                y_start : y_start + DETECT_SIZE, x_start : x_start + DETECT_SIZE
            ]

            # Green detection (board colour)
            mask = cv2.inRange(square, np.array([30, 20, 20]), np.array([95, 255, 255]))
            not_green = cv2.bitwise_not(mask)

            piece_pixels = cv2.countNonZero(not_green)
            total_pixels = square.shape[0] * square.shape[1]

            threshold = piece_pixels / total_pixels

            if threshold > 0.2:
                value_square = value_channel[
                    y_start : y_start + DETECT_SIZE, x_start : x_start + DETECT_SIZE
                ]
                piece_mask = not_green > 0

                if np.any(piece_mask):
                    mean_val = np.mean(value_square[piece_mask])

                    if mean_val > 100:
                        grid[r][c] = 1
                        color = (255, 255, 255)  # white box = white piece
                    else:
                        grid[r][c] = 2
                        color = (0, 255, 0)  # green box = black piece
                else:
                    grid[r][c] = 0
                    color = (0, 0, 255)
            else:
                grid[r][c] = 0
                color = (0, 0, 255)

            # Draw detection box
            cv2.rectangle(
                debug,
                (x_start, y_start),
                (x_start + DETECT_SIZE, y_start + DETECT_SIZE),
                color,
                2,
            )
            # Label square name
            sq_name = index_to_chess(r, c)
            cv2.putText(
                debug,
                sq_name,
                (x_start + 2, y_start + 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.32,
                color,
                1,
            )

    return grid, debug


def grid_to_fen(grid):
    fen = ""
    for r in range(8):
        empty = 0
        for c in range(8):
            val = grid[r][c]
            if val == 0:
                empty += 1
            else:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                fen += "P" if val == 1 else "p"
        if empty > 0:
            fen += str(empty)
        if r != 7:
            fen += "/"
    return fen


def stable_grid_detection(cap, H):
    """
    Capture FRAMES frames, majority-vote per square.
    Returns (final_grid, debug_image).
    """
    grids = []
    last_warped = None

    print("  Capturing frames for stable detection...")
    for i in range(FRAMES):
        ret, frame = cap.read()
        if not ret:
            print(f"  Warning: frame {i} failed")
            continue
        warped = cv2.warpPerspective(frame, H, (CAM_SIZE, CAM_SIZE))
        grid, _ = detect_grid_from_frame(warped)
        grids.append(grid)
        last_warped = warped
        time.sleep(0.1)

    if not grids:
        return np.zeros((8, 8), dtype=int), None

    grids_arr = np.array(grids)
    final_grid = np.zeros((8, 8), dtype=int)

    for r in range(8):
        for c in range(8):
            values, counts = np.unique(grids_arr[:, r, c], return_counts=True)
            idx = np.argmax(counts)
            if counts[idx] >= THRESHOLD:
                final_grid[r][c] = values[idx]

    # Build final debug image from the stable grid on the last warped frame
    if last_warped is not None:
        _, debug_img = detect_grid_from_frame(last_warped)
    else:
        debug_img = None

    return final_grid, debug_img


def detect_move(prev, curr):
    from_sq = to_sq = None
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


def save_move_debug(move_num, white_move, black_move, grid, debug_img, fen):
    """Save annotated image + text info after every move pair."""
    prefix = os.path.join(DEBUG_DIR, f"move_{move_num:03d}")

    if debug_img is not None:
        img_path = prefix + "_detection.jpg"
        cv2.imwrite(img_path, debug_img)

    info_path = prefix + "_info.txt"
    with open(info_path, "w") as f:
        f.write(f"Move number : {move_num}\n")
        f.write(f"White played: {white_move}\n")
        f.write(f"Black played: {black_move}\n")
        f.write(f"FEN         : {fen}\n\n")
        f.write("Grid (0=empty  1=white  2=black):\n")
        for row in grid:
            f.write("  " + str(list(row)) + "\n")

    print(f"  Saved debug -> {prefix}_*")


# ============================================================
#  ARM HELPERS
# ============================================================
def open_gripper(mc):
    mc.set_gripper_value(GRIP_OPEN, GRIP_SPEED)
    time.sleep(0.8)


def open_gripper_wide(mc):
    mc.set_gripper_value(GRIP_OPEN_ZERO, GRIP_SPEED)
    time.sleep(0.8)


def close_gripper(mc):
    mc.set_gripper_value(GRIP_CLOSE, GRIP_SPEED)
    time.sleep(0.8)


def go_to_square(mc, angles):
    """Direct move to a square — NO safe-position logic."""
    mc.send_angles(clamp(angles), SPEED)
    time.sleep(3)


def go_back(mc, current_angles):
    """
    Safe lift of J2 then return to BACK_POSITION.
    This is the ONLY place safe-position logic is used.
    """
    safe = list(current_angles)
    safe[1] += 10
    mc.send_angles(clamp(safe), SPEED)
    time.sleep(2)
    mc.send_angles(BACK_POSITION, SPEED)
    time.sleep(3)
    return list(BACK_POSITION)


# ============================================================
#  ROBOT CHESS MOVE EXECUTION
# ============================================================
def execute_chess_move(mc, current_angles, move_str, board_grid):
    """
    Physically execute a chess move.

    Sequence
    --------
    [capture] open_wide -> go_to dest -> close -> go_back
              -> go_to capture_zone -> open -> go_back
    pick up : open_wide -> go_to source -> close
    place   : go_to dest -> open
    return  : go_back
    """
    from_sq = move_str[:2]
    to_sq = move_str[2:4]
    from_key = chess_to_key(from_sq)
    to_key = chess_to_key(to_sq)

    if from_key not in position_map:
        print(f"  No angles mapped for source {from_sq} (key '{from_key}')")
        return current_angles
    if to_key not in position_map:
        print(f"  No angles mapped for destination {to_sq} (key '{to_key}')")
        return current_angles

    from_angles = position_map[from_key]
    to_angles = position_map[to_key]

    to_col = ord(to_sq[0]) - ord("a")
    to_row = 8 - int(to_sq[1])
    dest_occupied = board_grid[to_row][to_col] != 0

    print(
        f"\n  Executing: {from_sq} -> {to_sq}" + (" [CAPTURE]" if dest_occupied else "")
    )

    # ── Capture: remove opponent's piece first ────────────────
    if dest_occupied:
        if CAPTURED_ZONE_ANGLES is None:
            print("  CAPTURED_ZONE_ANGLES not set — skipping piece removal.")
            print("  Set the variable at the top of the file once calibrated.")
        else:
            print("  -> Open wide, go to captured piece")
            open_gripper_wide(mc)
            go_to_square(mc, to_angles)

            print("  -> Grip captured piece")
            close_gripper(mc)

            print("  -> Lift and go back (safe)")
            current_angles = go_back(mc, list(to_angles))

            print("  -> Move to discard zone")
            go_to_square(mc, CAPTURED_ZONE_ANGLES)

            print("  -> Release captured piece")
            open_gripper(mc)

            print("  -> Return home (safe lift)")
            current_angles = go_back(mc, list(CAPTURED_ZONE_ANGLES))

    # # ── Pick up the moving piece ──────────────────────────────
    # print(f"  -> Open wide, go to source {from_sq}")
    # open_gripper_wide(mc)
    # go_to_square(mc, from_angles)

    # print("  -> Grip piece")
    # close_gripper(mc)

    # # ── Place at destination ──────────────────────────────────
    # print(f"  -> Place at {to_sq}")
    # go_to_square(mc, to_angles)
    # open_gripper(mc)

    # # ── Return home ───────────────────────────────────────────
    # print("  -> Return to back (safe lift)")
    # current_angles = go_back(mc, list(to_angles))

    # print(f"  Move complete: {from_sq} -> {to_sq}\n")

    # ── MOVE TO SOURCE (SAFE APPROACH) ───────────────
    print(f"  -> Go to safe position above {from_sq}")
    safe_from = list(from_angles)
    safe_from[1] += 10
    mc.send_angles(clamp(safe_from), SPEED)
    time.sleep(2)

    print(f"  -> Open wide, go to source {from_sq}")
    open_gripper_wide(mc)
    go_to_square(mc, from_angles)

    print("  -> Grip piece")
    close_gripper(mc)

    # ── LIFT AFTER GRIP ─────────────────────────────
    print(f"  -> Lift to safe position above {from_sq}")
    mc.send_angles(clamp(safe_from), SPEED)
    time.sleep(2)

    print("  -> Return to back")
    mc.send_angles(BACK_POSITION, SPEED)
    time.sleep(3)
    current_angles = list(BACK_POSITION)

    # ── MOVE TO DESTINATION (SAFE APPROACH) ─────────
    print(f"  -> Go to safe position above {to_sq}")
    safe_to = list(to_angles)
    safe_to[1] += 10
    mc.send_angles(clamp(safe_to), SPEED)
    time.sleep(2)

    print(f"  -> Go to destination {to_sq}")
    go_to_square(mc, to_angles)

    print("  -> Release piece")
    open_gripper(mc)

    # ── FINAL LIFT ──────────────────────────────────
    print(f"  -> Lift to safe position above {to_sq}")
    mc.send_angles(clamp(safe_to), SPEED)
    time.sleep(2)

    print("  -> Return to back (safe lift)")
    mc.send_angles(BACK_POSITION, SPEED)
    time.sleep(3)
    current_angles = list(BACK_POSITION)

    return current_angles


# ============================================================
#  MANUAL KEYBOARD KEY MAP (joint control)
# ============================================================
key_map = {
    "q": (0, +STEP),
    "a": (0, -STEP),
    "w": (1, +STEP),
    "s": (1, -STEP),
    "e": (2, +STEP),
    "d": (2, -STEP),
    "r": (3, +STEP),
    "f": (3, -STEP),
    "t": (4, +STEP),
    "g": (4, -STEP),
    "y": (5, +STEP),
    "h": (5, -STEP),
}


# ============================================================
#  MAIN
# ============================================================
def main():
    # ── Init arm ─────────────────────────────────────────────
    print("Connecting to myCobot...")
    mc = MyCobot(PORT, BAUD)
    time.sleep(2)
    mc.power_on()
    time.sleep(1)

    current_angles = mc.get_angles() or [0, 0, 0, 0, 0, 0]

    # ── Init vision ───────────────────────────────────────────
    H = np.load("H.npy")
    cap = cv2.VideoCapture(0)
    print("Camera brightness (before):", cap.get(cv2.CAP_PROP_BRIGHTNESS))
    cap.set(cv2.CAP_PROP_BRIGHTNESS, -30)
    print("Camera brightness (after) :", cap.get(cv2.CAP_PROP_BRIGHTNESS))

    # ── Init Stockfish ────────────────────────────────────────
    engine = Stockfish(path="/usr/games/stockfish")
    moves = []  # full UCI history: white, black, white, black ...

    # ── Board state ───────────────────────────────────────────
    previous_grid = None
    board_grid = np.zeros((8, 8), dtype=int)
    move_count = 0

    print("\n" + "=" * 58)
    print("  Chess Robot  —  MyCobot plays BLACK")
    print("=" * 58)
    print(
        """
CHESS
  n           Capture board, detect White's move, robot replies

ARM
  z           Zero all joints
  i / b       Return to back/rest position (safe lift)
  camera      Move to camera position
  o           Open gripper
  c           Close gripper
  p           Open gripper wide (pre-grip)

JOINT CONTROL  (STEP per press)
  q/a  w/s  e/d  r/f  t/g  y/h   J1-J6 +/-

DIRECT SQUARE  (2-digit key e.g. 57 for e2)
  Moves arm straight to that square (no safe wrapping)

  x           Exit
"""
    )

    while True:
        key = input("Command: ").strip()

        if key == "x":
            print("Exiting...")
            break

        if key == "z":
            current_angles = [0, 0, 0, 0, 0, 0]
            mc.send_angles(current_angles, SPEED)
            print("Zero position")
            continue

        if key in ("i", "b"):
            current_angles = go_back(mc, current_angles)
            print("Back position")
            continue

        if key == "camera":
            current_angles = list(position_map["camera"])
            mc.send_angles(current_angles, SPEED)
            time.sleep(3)
            print("Camera position")
            continue

        if key == "o":
            open_gripper(mc)
            print("Gripper OPEN")
            continue
        if key == "c":
            close_gripper(mc)
            print("Gripper CLOSE")
            continue
        if key == "p":
            open_gripper_wide(mc)
            print("Gripper OPEN WIDE")
            continue

        # ── Chess move capture ────────────────────────────────
        if key == "n":
            print("\nRemove your hand from the board...")
            time.sleep(2)

            # Close gripper during image capture
            close_gripper(mc)

            # Move to camera view
            # mc.send_angles(position_map["camera"], SPEED)
            # time.sleep(3)

            current_grid, debug_img = stable_grid_detection(cap, H)
            print("\nDetected grid:\n", current_grid)

            # First capture — initialise
            if previous_grid is None:
                print("Initial board captured. Waiting for White's first move.")
                previous_grid = current_grid.copy()
                board_grid = current_grid.copy()
                fen = grid_to_fen(current_grid) + " w - - 0 1"
                print("FEN:", fen)
                if debug_img is not None:
                    cv2.imwrite(
                        os.path.join(DEBUG_DIR, "move_000_initial.jpg"), debug_img
                    )
                with open(os.path.join(DEBUG_DIR, "move_000_info.txt"), "w") as f:
                    f.write(f"Initial board\nFEN: {fen}\n")
                    for row in current_grid:
                        f.write("  " + str(list(row)) + "\n")
                # current_angles = go_back(mc, list(position_map["camera"]))
                continue

            # Detect White's move
            white_move = detect_move(previous_grid, current_grid)
            if not white_move:
                print("No valid move detected — try again.")
                # current_angles = go_back(mc, list(position_map["camera"]))
                continue

            print(f"\nWhite played: {white_move}")
            moves.append(white_move)

            # Stockfish reply for Black
            engine.set_position(moves)
            black_move = engine.get_best_move()

            if not black_move:
                print("Stockfish has no reply — game may be over.")
                previous_grid = current_grid.copy()
                board_grid = current_grid.copy()
                # current_angles = go_back(mc, list(position_map["camera"]))
                continue

            print(f"Robot (Black) plays: {black_move}")
            moves.append(black_move)
            move_count += 1

            fen = grid_to_fen(current_grid) + " b - - 0 1"
            print("FEN:", fen)
            save_move_debug(
                move_count, white_move, black_move, current_grid, debug_img, fen
            )

            board_grid = current_grid.copy()
            previous_grid = current_grid.copy()

            current_angles = go_back(mc, list(position_map["camera"]))
            current_angles = execute_chess_move(
                mc, current_angles, black_move, board_grid
            )
            continue

        # ── Direct square ─────────────────────────────────────
        if key in position_map and key != "camera":
            go_to_square(mc, position_map[key])
            current_angles = list(position_map[key])
            print(f"Moved to square {key}")
            continue

        # ── Joint control ─────────────────────────────────────
        if key in key_map:
            joint, delta = key_map[key]
            current_angles[joint] += delta
            current_angles = clamp(current_angles)
            mc.send_angles(current_angles, SPEED)
            print("Angles:", current_angles)
            continue

        print("Unknown command.")

    cap.release()
    print("Done.")


if __name__ == "__main__":
    main()
