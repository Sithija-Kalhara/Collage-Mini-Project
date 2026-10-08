import cv2
import mediapipe as mp
import numpy as np
import time
import os
import math
from collections import deque

# ============================================================
# 1. MEDIAPIPE MODEL
# ============================================================

MODEL_PATH = "hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print()
    print("ERROR: hand_landmarker.task was not found.")
    print("Put hand_landmarker.task in the same folder as this program.")
    print()
    exit()

# ============================================================
# 2. CAMERA SETTINGS
# ============================================================

WIDTH = 960
HEIGHT = 720

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

# ============================================================
# 3. DRAWING CANVAS & SMOOTHING SETTINGS
# ============================================================

canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

POINTS_HISTORY_SIZE = 5
point_history = deque(maxlen=POINTS_HISTORY_SIZE)

SMOOTH_FACTOR = 0.35
smoothed_x, smoothed_y = None, None

# ============================================================
# 4. DRAWING COLORS (BGR Format)
# ============================================================

COLORS = {
    "RED": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (255, 0, 0),
    "YELLOW": (0, 255, 255),
    "PINK": (255, 0, 255),
    "ORANGE": (0, 165, 255),
    "PURPLE": (128, 0, 128),
    "WHITE": (255, 255, 255)
}

current_color_name = "PINK"
current_color = COLORS[current_color_name]

# ============================================================
# 5. BRUSH SETTINGS
# ============================================================

BRUSH_SIZE = 8
ERASER_SIZE = 40
eraser_mode = False

# ============================================================
# 6. UI SETTINGS
# ============================================================

TOOLBAR_HEIGHT = 95
BUTTON_TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (30, 20, 35)

# ============================================================
# 7. COLOR BUTTONS
# ============================================================

buttons = [
    ("RED", 10, 15, 105, 70),
    ("GREEN", 115, 15, 210, 70),
    ("BLUE", 220, 15, 315, 70),
    ("YELLOW", 325, 15, 430, 70),
    ("PINK", 440, 15, 535, 70),
    ("ORANGE", 545, 15, 650, 70),
    ("PURPLE", 660, 15, 765, 70),
    ("CLEAR", 775, 15, 860, 70),
    ("SAVE", 870, 15, 950, 70)
]

# ============================================================
# 8. MEDIAPIPE HAND LANDMARKER
# ============================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

# ============================================================
# 9. HELPER FUNCTIONS
# ============================================================

def finger_is_up(landmarks, tip_id, pip_id):
    return landmarks[tip_id].y < landmarks[pip_id].y

def calculate_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# ============================================================
# 10. DRAW TOOLBAR
# ============================================================

def draw_toolbar(frame):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, TOOLBAR_HEIGHT), BACKGROUND_COLOR, -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    for name, x1, y1, x2, y2 in buttons:
        if name in COLORS:
            button_color = COLORS[name]
        elif name == "CLEAR":
            button_color = (70, 70, 70)
        elif name == "SAVE":
            button_color = (100, 40, 120)
        else:
            button_color = (80, 80, 80)

        thickness = 5 if (name == current_color_name and not eraser_mode) else 2

        cv2.rectangle(frame, (x1, y1), (x2, y2), button_color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), BORDER_COLOR, thickness)

        text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 2)[0]
        text_x = x1 + (x2 - x1 - text_size[0]) // 2
        text_y = y1 + (y2 - y1 + text_size[1]) // 2

        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, BUTTON_TEXT_COLOR, 2, cv2.LINE_AA)

# ============================================================
# 11. SAVE & CLEAR DRAWING
# ============================================================

def save_and_clear_drawing():
    filename = "letter_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
    cv2.imwrite(filename, canvas)
    print(f"Letter saved: {filename}")
    canvas[:] = 0  # Auto-clear for next letter

# ============================================================
# 12. CHECK BUTTON SELECTION
# ============================================================

def check_button(x, y):
    global current_color, current_color_name, eraser_mode

    for name, x1, y1, x2, y2 in buttons:
        if x1 <= x <= x2 and y1 <= y <= y2:
            if name in COLORS:
                current_color_name = name
                current_color = COLORS[name]
                eraser_mode = False
                print(f"Color selected: {name}")
            elif name == "CLEAR":
                canvas[:] = 0
                print("Canvas cleared.")
            elif name == "SAVE":
                save_and_clear_drawing()
            return True
    return False

# ============================================================
# 13. DRAW HAND LANDMARKS
# ============================================================

def draw_hand_landmarks(frame, landmarks):
    points = [(int(lm.x * WIDTH), int(lm.y * HEIGHT)) for lm in landmarks]
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
    ]

    for start, end in connections:
        cv2.line(frame, points[start], points[end], (255, 120, 200), 2, cv2.LINE_AA)

    for point in points:
        cv2.circle(frame, point, 3, (255, 255, 255), -1, cv2.LINE_AA)

# ============================================================
# 14. PROGRAM VARIABLES
# ============================================================

previous_x = None
previous_y = None
last_button_time = 0
last_clear_time = 0
last_timestamp_ms = 0

# ============================================================
# 15. MAIN LOOP
# ============================================================

with HandLandmarker.create_from_options(options) as hand_landmarker:

    while True:
        success, frame = camera.read()
        if not success:
            print("Could not read webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(time.monotonic() * 1000)
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms

        result = hand_landmarker.detect_for_video(mp_image, timestamp_ms)
        mode_text = "NO HAND"

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            draw_hand_landmarks(frame, landmarks)

            # Check Pinch (Thumb Tip = 4, Index Tip = 8)
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            pinch_distance = calculate_distance(thumb_tip, index_tip)

            # Is Pinch active? (Threshold ~ 0.05)
            is_pinching = pinch_distance < 0.05

            raw_x = int(index_tip.x * WIDTH)
            raw_y = int(index_tip.y * HEIGHT)

            # Smoothing
            point_history.append((raw_x, raw_y))
            avg_x = sum(p[0] for p in point_history) // len(point_history)
            avg_y = sum(p[1] for p in point_history) // len(point_history)

            if smoothed_x is None or smoothed_y is None:
                smoothed_x, smoothed_y = avg_x, avg_y
            else:
                smoothed_x = int(smoothed_x + SMOOTH_FACTOR * (avg_x - smoothed_x))
                smoothed_y = int(smoothed_y + SMOOTH_FACTOR * (avg_y - smoothed_y))

            index_x, index_y = smoothed_x, smoothed_y

            index_up = finger_is_up(landmarks, 8, 6)
            middle_up = finger_is_up(landmarks, 12, 10)
            ring_up = finger_is_up(landmarks, 16, 14)
            pinky_up = finger_is_up(landmarks, 20, 18)

            # OPEN PALM -> CLEAR
            if index_up and middle_up and ring_up and pinky_up:
                mode_text = "CLEAR"
                current_time = time.time()
                if current_time - last_clear_time > 1.5:
                    canvas[:] = 0
                    print("Canvas cleared.")
                    last_clear_time = current_time
                previous_x, previous_y = None, None
                point_history.clear()

            # INDEX + MIDDLE -> SELECT TOOLBAR
            elif index_up and middle_up and not ring_up:
                mode_text = "SELECT"
                previous_x, previous_y = None, None
                point_history.clear()

                if index_y < TOOLBAR_HEIGHT:
                    current_time = time.time()
                    if current_time - last_button_time > 0.7:
                        if check_button(index_x, index_y):
                            last_button_time = current_time

            # DRAW / HOVER MODE (Index up)
            elif index_up and not middle_up:
                if is_pinching:
                    # WRITE MODE (Pinch ON)
                    mode_text = "ERASER" if eraser_mode else "DRAW"
                    cursor_color = (0, 255, 0)  # Green cursor when writing

                    if index_y > TOOLBAR_HEIGHT:
                        if previous_x is None:
                            previous_x, previous_y = index_x, index_y

                        draw_color = (0, 0, 0) if eraser_mode else current_color
                        thickness = ERASER_SIZE if eraser_mode else BRUSH_SIZE

                        cv2.line(canvas, (previous_x, previous_y), (index_x, index_y), draw_color, thickness, cv2.LINE_AA)
                        previous_x, previous_y = index_x, index_y
                else:
                    # HOVER MODE (Pinch OFF - Not writing, moving cursor)
                    mode_text = "HOVER"
                    cursor_color = (0, 0, 255)  # Red cursor when hovering
                    previous_x, previous_y = None, None
                    point_history.clear()

                cursor_radius = ERASER_SIZE // 2 if eraser_mode else 8
                cv2.circle(frame, (index_x, index_y), cursor_radius, cursor_color, -1, cv2.LINE_AA)

            else:
                mode_text = "PAUSE"
                previous_x, previous_y = None, None
                point_history.clear()

        else:
            previous_x, previous_y = None, None
            smoothed_x, smoothed_y = None, None
            point_history.clear()

        # Combine drawing with webcam frame
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 5, 255, cv2.THRESH_BINARY)
        inverse_mask = cv2.bitwise_not(mask)

        background = cv2.bitwise_and(frame, frame, mask=inverse_mask)
        drawing = cv2.bitwise_and(canvas, canvas, mask=mask)
        combined = cv2.add(background, drawing)

        draw_toolbar(combined)

        # Status Bar
        overlay = combined.copy()
        cv2.rectangle(overlay, (0, HEIGHT - 65), (WIDTH, HEIGHT), (30, 20, 35), -1)
        cv2.addWeighted(overlay, 0.80, combined, 0.20, 0, combined)

        cv2.putText(combined, f"MODE: {mode_text}", (20, HEIGHT - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        color_text = "ERASER" if eraser_mode else current_color_name
        cv2.putText(combined, f"COLOR: {color_text}", (210, HEIGHT - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if not eraser_mode:
            cv2.circle(combined, (425, HEIGHT - 31), 14, current_color, -1)
            cv2.circle(combined, (425, HEIGHT - 31), 14, (255, 255, 255), 2)

        cv2.putText(combined, "E:Eraser  C:Clear  S:Save & Clear  Q:Quit", (480, HEIGHT - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

        cv2.imshow("AI Air Drawing", combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("c"):
            canvas[:] = 0
        elif key == ord("s"):
            save_and_clear_drawing()
        elif key == ord("e"):
            eraser_mode = not eraser_mode
        elif ord("1") <= key <= ord("8"):
            color_keys = ["RED", "GREEN", "BLUE", "YELLOW", "PINK", "ORANGE", "PURPLE", "WHITE"]
            current_color_name = color_keys[key - ord("1")]
            current_color = COLORS[current_color_name]
            eraser_mode = False

camera.release()
cv2.destroyAllWindows()