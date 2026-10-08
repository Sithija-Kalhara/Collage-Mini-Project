import cv2
import mediapipe as mp
import numpy as np
import time
import os
import threading
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# 1. OPTIONAL WINDOWS ALARM (Threaded for smooth FPS)
# ============================================================
try:
    import winsound
    WINDOWS_SOUND = True
except ImportError:
    WINDOWS_SOUND = False

def play_beep():
    """ Runs beep sound in a separate thread to prevent webcam freezing """
    if WINDOWS_SOUND:
        threading.Thread(target=winsound.Beep, args=(1200, 250), daemon=True).start()

# ============================================================
# 2. USER NAME
# ============================================================
person_name = input("Enter your name: ").strip()
if not person_name:
    person_name = "User"

# ============================================================
# 3. MODEL CHECK
# ============================================================
MODEL_PATH = "face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("\nERROR: face_landmarker.task not found.")
    print("Put face_landmarker.task in the same folder.\n")
    exit()

# ============================================================
# 4. FONT LOADING WITH SAFE FALLBACK
# ============================================================
FONT_PATHS = [
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/msgothic.ttc"
]

FONT_PATH = None
for path in FONT_PATHS:
    if os.path.exists(path):
        FONT_PATH = path
        break

try:
    if FONT_PATH:
        font_title = ImageFont.truetype(FONT_PATH, 26)
        font_status = ImageFont.truetype(FONT_PATH, 25)
        font_medium = ImageFont.truetype(FONT_PATH, 19)
        font_small = ImageFont.truetype(FONT_PATH, 16)
    else:
        raise FileNotFoundError
except Exception:
    print("Japanese system font not found. Using default Pillow font.")
    font_title = font_status = font_medium = font_small = ImageFont.load_default()

# ============================================================
# 5. THEME & COLORS
# ============================================================
COLOR_BG = (25, 18, 28)
COLOR_PANEL = (45, 28, 45)
COLOR_PANEL_LIGHT = (65, 42, 63)
COLOR_PINK = (255, 195, 215)
COLOR_WHITE = (255, 255, 255)
COLOR_SOFT_WHITE = (235, 225, 235)
COLOR_GREEN = (60, 220, 130)
COLOR_ORANGE = (255, 180, 70)
COLOR_RED = (255, 65, 85)
COLOR_GRAY = (120, 110, 125)

def rgb_to_bgr(color):
    return (color[2], color[1], color[0])

# ============================================================
# 6. LANDMARK INDICES & THRESHOLDS
# ============================================================
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESHOLD = 0.21
EAR_OPEN_THRESHOLD = 0.24
DROWSY_SECONDS = 1.5
ALARM_ENABLED = True
ALARM_COOLDOWN = 2.0

# ============================================================
# 7. HELPER FUNCTIONS
# ============================================================
def distance(point1, point2):
    return np.linalg.norm(point1 - point2)

def calculate_ear(points):
    vertical_1 = distance(points[1], points[5])
    vertical_2 = distance(points[2], points[4])
    horizontal = distance(points[0], points[3])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)

def get_eye_points(landmarks, indices, width, height):
    points = []
    for index in indices:
        landmark = landmarks[index]
        points.append([int(landmark.x * width), int(landmark.y * height)])
    return np.array(points, dtype=np.float32)

def get_face_box(landmarks, width, height):
    xs = [int(lm.x * width) for lm in landmarks]
    ys = [int(lm.y * height) for lm in landmarks]
    return (
        max(min(xs) - 20, 0),
        max(min(ys) - 30, 0),
        min(max(xs) + 20, width - 1),
        min(max(ys) + 30, height - 1)
    )

def draw_face_corners(frame, box, color):
    x1, y1, x2, y2 = box
    length, thickness = 28, 3
    cv2.line(frame, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(frame, (x1, y1), (x1, y1 + length), color, thickness)
    cv2.line(frame, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(frame, (x2, y1), (x2, y1 + length), color, thickness)
    cv2.line(frame, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(frame, (x1, y2), (x1, y2 - length), color, thickness)
    cv2.line(frame, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(frame, (x2, y2), (x2, y2 - length), color, thickness)

def draw_eye(frame, eye_points, color):
    points = eye_points.astype(np.int32)
    cv2.polylines(frame, [points], True, color, 2, cv2.LINE_AA)
    for point in points:
        cv2.circle(frame, (int(point[0]), int(point[1])), 3, color, -1, cv2.LINE_AA)

def rounded_panel(draw, box, fill, outline=None, radius=18, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_status_badge(draw, status, color, frame_width):
    badge_width, badge_height = 145, 38
    x1 = frame_width - badge_width - 20
    y1 = 16
    rounded_panel(draw, (x1, y1, x1 + badge_width, y1 + badge_height), color, radius=19)
    
    bbox = draw.textbbox((0, 0), status, font=font_small)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (x1 + (badge_width - text_width) / 2, y1 + (badge_height - text_height) / 2 - 3),
        status, font=font_small, fill=COLOR_WHITE
    )

def draw_progress_bar(draw, x, y, width, height, progress, color):
    progress = max(0.0, min(progress, 1.0))
    rounded_panel(draw, (x, y, x + width, y + height), COLOR_PANEL_LIGHT, radius=height // 2)
    filled_width = int(width * progress)
    if filled_width > 3:
        rounded_panel(draw, (x, y, x + filled_width, y + height), color, radius=height // 2)

def draw_dashboard(frame, name, status, japanese_status, status_color, ear, closed_seconds, blink_count, fps):
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image, "RGBA")
    width, height = pil_image.size

    # Header
    rounded_panel(draw, (15, 12, width - 15, 67), (25, 18, 28, 225), outline=(255, 195, 215, 100), radius=20)
    draw.text((32, 23), "AI DROWSINESS MONITOR", font=font_title, fill=COLOR_PINK)
    draw_status_badge(draw, status, status_color, width)

    # Main Status
    rounded_panel(draw, (20, 82, width - 20, 145), (45, 28, 45, 220), outline=(*status_color[:3], 180), radius=18, width=2)
    draw.text((38, 96), f"{name}: {japanese_status}", font=font_status, fill=COLOR_WHITE)

    # Bottom Dashboard
    panel_y1 = height - 145
    rounded_panel(draw, (15, panel_y1, width - 15, height - 15), (25, 18, 28, 230), outline=(255, 195, 215, 100), radius=22)

    # Telemetry
    draw.text((35, panel_y1 + 18), "EAR", font=font_small, fill=COLOR_GRAY)
    draw.text((35, panel_y1 + 42), f"{ear:.3f}", font=font_medium, fill=COLOR_WHITE)

    draw.text((155, panel_y1 + 18), "CLOSED", font=font_small, fill=COLOR_GRAY)
    draw.text((155, panel_y1 + 42), f"{closed_seconds:.1f}s", font=font_medium, fill=status_color)

    draw.text((300, panel_y1 + 18), "BLINKS", font=font_small, fill=COLOR_GRAY)
    draw.text((300, panel_y1 + 42), str(blink_count), font=font_medium, fill=COLOR_WHITE)

    draw.text((425, panel_y1 + 18), "FPS", font=font_small, fill=COLOR_GRAY)
    draw.text((425, panel_y1 + 42), f"{fps:.1f}", font=font_medium, fill=COLOR_WHITE)

    # Progress Bar
    draw.text((35, panel_y1 + 82), "Drowsiness level", font=font_small, fill=COLOR_SOFT_WHITE)
    draw_progress_bar(draw, 175, panel_y1 + 88, width - 215, 14, closed_seconds / DROWSY_SECONDS, status_color)

    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# ============================================================
# 8. MEDIAPIPE INITIALIZATION
# ============================================================
options = mp.tasks.vision.FaceLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

# Variables
eyes_closed_since = None
closed_duration = 0.0
blink_count = 0
eyes_currently_closed = False
last_timestamp_ms = 0
previous_frame_time = time.monotonic()
fps = 0.0
last_alarm_time = 0.0

print("\n" + "=" * 50 + "\n AI DROWSINESS MONITOR\n" + "=" * 50)
print(f" Hello {person_name}\n Press Q to quit\n" + "=" * 50 + "\n")

# ============================================================
# 9. MAIN LOOP
# ============================================================
with mp.tasks.vision.FaceLandmarker.create_from_options(options) as face_landmarker:
    while True:
        success, frame = camera.read()
        if not success:
            print("Could not read webcam.")
            break

        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]

        # FPS Calc
        current_frame_time = time.monotonic()
        delta = current_frame_time - previous_frame_time
        previous_frame_time = current_frame_time
        if delta > 0:
            fps = fps * 0.90 + (1.0 / delta) * 0.10

        # MediaPipe Timestamp
        timestamp_ms = int(time.monotonic() * 1000)
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = face_landmarker.detect_for_video(mp_image, timestamp_ms)

        # Defaults
        status = "NO FACE"
        japanese_status = "顔が見つかりません"
        status_color = COLOR_GRAY
        average_ear = 0.0

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            right_eye_points = get_eye_points(landmarks, RIGHT_EYE, width, height)
            left_eye_points = get_eye_points(landmarks, LEFT_EYE, width, height)

            right_ear = calculate_ear(right_eye_points)
            left_ear = calculate_ear(left_eye_points)
            average_ear = (right_ear + left_ear) / 2.0
            current_time = time.monotonic()

            # Eyes Closed
            if average_ear < EAR_THRESHOLD:
                if not eyes_currently_closed:
                    eyes_currently_closed = True
                if eyes_closed_since is None:
                    eyes_closed_since = current_time

                closed_duration = current_time - eyes_closed_since

                if closed_duration >= DROWSY_SECONDS:
                    status = "DROWSY"
                    japanese_status = "眠そうです！目を開けてください"
                    status_color = COLOR_RED

                    # Async Beep (Does not lag video stream)
                    if ALARM_ENABLED and WINDOWS_SOUND:
                        if current_time - last_alarm_time >= ALARM_COOLDOWN:
                            play_beep()
                            last_alarm_time = current_time
                else:
                    status = "EYES CLOSED"
                    japanese_status = "目を閉じています"
                    status_color = COLOR_ORANGE

            # Eyes Open
            else:
                if eyes_currently_closed and average_ear >= EAR_OPEN_THRESHOLD:
                    blink_count += 1
                    eyes_currently_closed = False

                eyes_closed_since = None
                closed_duration = 0.0
                status = "AWAKE"
                japanese_status = "起きています"
                status_color = COLOR_GREEN

            # Render Tracking & Face Box
            eye_color_bgr = rgb_to_bgr(status_color)
            draw_eye(frame, right_eye_points, eye_color_bgr)
            draw_eye(frame, left_eye_points, eye_color_bgr)
            draw_face_corners(frame, get_face_box(landmarks, width, height), eye_color_bgr)

        else:
            eyes_closed_since = None
            closed_duration = 0.0
            eyes_currently_closed = False

        # Flashing Screen Border when Drowsy
        if status == "DROWSY":
            if int(time.monotonic() * 4) % 2 == 0:
                cv2.rectangle(frame, (4, 4), (width - 4, height - 4), rgb_to_bgr(COLOR_RED), 8)

        # Draw UI Dashboard
        frame = draw_dashboard(
            frame, person_name, status, japanese_status,
            status_color, average_ear, closed_duration, blink_count, fps
        )

        cv2.imshow("AI Drowsiness Monitor", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Cleanup
camera.release()
cv2.destroyAllWindows()
print("\n" + "=" * 50)
print(" Drowsiness Monitor Stopped")
print(f" Total blinks detected: {blink_count}")
print("=" * 50)