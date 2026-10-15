import cv2
import mediapipe as mp
import time
import math
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

SCREEN_W = 1280
SCREEN_H = 720

DWELL_TIME = 0.7

WINDOW_NAME = "Advanced Air Smart Home Controller"


# ============================================================
# MEDIAPIPE TASKS SETUP
# ============================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),

    running_mode=RunningMode.VIDEO,

    num_hands=1,

    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

landmarker = HandLandmarker.create_from_options(options)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    SCREEN_W
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    SCREEN_H
)

cap.set(
    cv2.CAP_PROP_FPS,
    30
)


# ============================================================
# SMART HOME STATE
# ============================================================

home = {

    "light": False,

    "fan": False,

    "ac": False,

    "music": False,

    "door_locked": True,

    "temperature": 24,

    "scene": "NORMAL"
}


# ============================================================
# UI BUTTON DEFINITIONS
# ============================================================

buttons = {

    "light": {
        "label": "LIGHT",
        "x1": 60,
        "y1": 155,
        "x2": 300,
        "y2": 285
    },

    "fan": {
        "label": "FAN",
        "x1": 330,
        "y1": 155,
        "x2": 570,
        "y2": 285
    },

    "ac": {
        "label": "AC",
        "x1": 600,
        "y1": 155,
        "x2": 840,
        "y2": 285
    },

    "music": {
        "label": "MUSIC",
        "x1": 870,
        "y1": 155,
        "x2": 1110,
        "y2": 285
    },

    "door": {
        "label": "DOOR",
        "x1": 60,
        "y1": 330,
        "x2": 300,
        "y2": 460
    },

    "temp_down": {
        "label": "TEMP -",
        "x1": 330,
        "y1": 330,
        "x2": 500,
        "y2": 460
    },

    "temp_up": {
        "label": "TEMP +",
        "x1": 515,
        "y1": 330,
        "x2": 685,
        "y2": 460
    },

    "home_scene": {
        "label": "HOME MODE",
        "x1": 720,
        "y1": 330,
        "x2": 925,
        "y2": 460
    },

    "away_scene": {
        "label": "AWAY MODE",
        "x1": 940,
        "y1": 330,
        "x2": 1145,
        "y2": 460
    }
}


# ============================================================
# HAND CONNECTIONS
# ============================================================

connections = [

    (0, 1), (1, 2), (2, 3), (3, 4),

    (0, 5), (5, 6), (6, 7), (7, 8),

    (5, 9), (9, 10), (10, 11), (11, 12),

    (9, 13), (13, 14), (14, 15), (15, 16),

    (13, 17), (17, 18), (18, 19), (19, 20),

    (0, 17)
]


# ============================================================
# HOVER / DWELL VARIABLES
# ============================================================

hover_button = None

hover_start = 0

last_triggered_button = None

last_trigger_time = 0

feedback_message = ""

feedback_time = 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def inside_button(x, y, button):

    return (
        button["x1"] <= x <= button["x2"]
        and
        button["y1"] <= y <= button["y2"]
    )


def draw_glass_panel(
    frame,
    x1,
    y1,
    x2,
    y2,
    color=(255, 255, 255),
    alpha=0.18,
    border=2
):

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (x1, y1),
        (x2, y2),
        color,
        -1
    )

    cv2.addWeighted(
        overlay,
        alpha,
        frame,
        1 - alpha,
        0,
        frame
    )

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        color,
        border
    )

    # glossy highlight
    cv2.line(
        frame,
        (x1 + 12, y1 + 12),
        (x2 - 12, y1 + 12),
        (255, 255, 255),
        2
    )


def draw_neon_button(
    frame,
    key,
    active=False,
    hovered=False,
    progress=0
):

    button = buttons[key]

    x1 = button["x1"]
    y1 = button["y1"]
    x2 = button["x2"]
    y2 = button["y2"]

    if active:

        color = (80, 255, 150)

    else:

        color = (180, 110, 255)


    # hover glow
    if hovered:

        for glow in [12, 8, 4]:

            cv2.rectangle(
                frame,
                (x1 - glow, y1 - glow),
                (x2 + glow, y2 + glow),
                (0, 255, 255),
                2
            )


    # background
    draw_glass_panel(
        frame,
        x1,
        y1,
        x2,
        y2,
        color=color,
        alpha=0.24,
        border=3
    )


    # activation progress bar
    if hovered and progress > 0:

        bar_width = int(
            (x2 - x1) * progress
        )

        cv2.rectangle(
            frame,
            (x1, y2 - 10),
            (x1 + bar_width, y2),
            (0, 255, 255),
            -1
        )


    cv2.putText(
        frame,
        button["label"],
        (
            x1 + 20,
            y1 + 42
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (255, 255, 255),
        2
    )


# ============================================================
# DEVICE ICONS
# ============================================================

def draw_light(frame, cx, cy, on):

    bulb_color = (
        (0, 255, 255)
        if on
        else (100, 100, 100)
    )

    if on:

        for radius in [38, 32, 26]:

            cv2.circle(
                frame,
                (cx, cy),
                radius,
                (0, 220, 255),
                2
            )

    cv2.circle(
        frame,
        (cx, cy),
        20,
        bulb_color,
        -1
    )

    cv2.rectangle(
        frame,
        (cx - 10, cy + 20),
        (cx + 10, cy + 35),
        (220, 220, 220),
        -1
    )


def draw_fan(
    frame,
    cx,
    cy,
    on,
    angle
):

    center_color = (
        (80, 255, 150)
        if on
        else (150, 150, 150)
    )

    for i in range(3):

        a = math.radians(
            angle + i * 120
        )

        x2 = int(
            cx + 38 * math.cos(a)
        )

        y2 = int(
            cy + 38 * math.sin(a)
        )

        cv2.line(
            frame,
            (cx, cy),
            (x2, y2),
            center_color,
            10
        )

    cv2.circle(
        frame,
        (cx, cy),
        10,
        (255, 255, 255),
        -1
    )


def draw_ac(frame, cx, cy, on):

    color = (
        (255, 255, 80)
        if on
        else (130, 130, 130)
    )

    cv2.rectangle(
        frame,
        (cx - 38, cy - 18),
        (cx + 38, cy + 18),
        color,
        3
    )

    if on:

        for offset in [-20, 0, 20]:

            cv2.line(
                frame,
                (cx + offset, cy + 20),
                (cx + offset, cy + 42),
                (255, 255, 80),
                2
            )


def draw_music(frame, cx, cy, on):

    color = (
        (255, 80, 255)
        if on
        else (140, 140, 140)
    )

    cv2.line(
        frame,
        (cx, cy - 30),
        (cx, cy + 25),
        color,
        5
    )

    cv2.line(
        frame,
        (cx, cy - 30),
        (cx + 32, cy - 40),
        color,
        5
    )

    cv2.circle(
        frame,
        (cx - 10, cy + 30),
        12,
        color,
        -1
    )

    cv2.circle(
        frame,
        (cx + 25, cy + 20),
        12,
        color,
        -1
    )


def draw_door(frame, cx, cy, locked):

    color = (
        (80, 120, 255)
        if locked
        else (80, 255, 150)
    )

    cv2.rectangle(
        frame,
        (cx - 28, cy - 35),
        (cx + 28, cy + 35),
        color,
        3
    )

    cv2.circle(
        frame,
        (cx + 16, cy),
        4,
        color,
        -1
    )


# ============================================================
# ACTION HANDLER
# ============================================================

def activate_control(key):

    global feedback_message
    global feedback_time


    if key == "light":

        home["light"] = (
            not home["light"]
        )

        feedback_message = (
            "Light ON"
            if home["light"]
            else "Light OFF"
        )


    elif key == "fan":

        home["fan"] = (
            not home["fan"]
        )

        feedback_message = (
            "Fan ON"
            if home["fan"]
            else "Fan OFF"
        )


    elif key == "ac":

        home["ac"] = (
            not home["ac"]
        )

        feedback_message = (
            "AC ON"
            if home["ac"]
            else "AC OFF"
        )


    elif key == "music":

        home["music"] = (
            not home["music"]
        )

        feedback_message = (
            "Music PLAYING"
            if home["music"]
            else "Music PAUSED"
        )


    elif key == "door":

        home["door_locked"] = (
            not home["door_locked"]
        )

        feedback_message = (
            "Door LOCKED"
            if home["door_locked"]
            else "Door UNLOCKED"
        )


    elif key == "temp_down":

        home["temperature"] = max(
            16,
            home["temperature"] - 1
        )

        feedback_message = (
            f"Temperature {home['temperature']} C"
        )


    elif key == "temp_up":

        home["temperature"] = min(
            30,
            home["temperature"] + 1
        )

        feedback_message = (
            f"Temperature {home['temperature']} C"
        )


    elif key == "home_scene":

        home["scene"] = "HOME"

        home["light"] = True

        home["fan"] = True

        home["ac"] = True

        home["music"] = True

        home["door_locked"] = True

        home["temperature"] = 24

        feedback_message = (
            "HOME MODE activated"
        )


    elif key == "away_scene":

        home["scene"] = "AWAY"

        home["light"] = False

        home["fan"] = False

        home["ac"] = False

        home["music"] = False

        home["door_locked"] = True

        home["temperature"] = 26

        feedback_message = (
            "AWAY MODE activated"
        )


    feedback_time = time.time()


# ============================================================
# RESET
# ============================================================

def reset_home():

    home["light"] = False

    home["fan"] = False

    home["ac"] = False

    home["music"] = False

    home["door_locked"] = True

    home["temperature"] = 24

    home["scene"] = "NORMAL"


# ============================================================
# WINDOW
# ============================================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW_NAME,
    SCREEN_W,
    SCREEN_H
)


# ============================================================
# ANIMATION
# ============================================================

fan_angle = 0


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:

        print("Camera error")
        break


    frame = cv2.flip(
        frame,
        1
    )


    frame = cv2.resize(
        frame,
        (SCREEN_W, SCREEN_H)
    )


    height, width, _ = frame.shape


    # ========================================================
    # BACKGROUND TINT
    # ========================================================

    tint = np.zeros_like(frame)

    tint[:] = (
        25,
        20,
        35
    )

    cv2.addWeighted(
        frame,
        0.82,
        tint,
        0.18,
        0,
        frame
    )


    # ========================================================
    # HEADER
    # ========================================================

    draw_glass_panel(
        frame,
        20,
        15,
        1260,
        115,
        color=(220, 220, 255),
        alpha=0.17
    )


    cv2.putText(
        frame,
        "AIR SMART HOME CONTROLLER",
        (350, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.15,
        (255, 255, 255),
        3
    )


    cv2.putText(
        frame,
        "Point and hold 0.7 sec to activate",
        (430, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (180, 255, 240),
        2
    )


    # ========================================================
    # HAND TRACKING
    # ========================================================

    index_x = None
    index_y = None

    hand_detected = False


    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )


    timestamp_ms = int(
        time.time() * 1000
    )


    result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )


    if result.hand_landmarks:

        hand_detected = True

        hand = result.hand_landmarks[0]

        points = []


        for landmark in hand:

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            points.append((x, y))


        for start, end in connections:

            cv2.line(
                frame,
                points[start],
                points[end],
                (120, 255, 210),
                2
            )


        index_x, index_y = points[8]


        # neon cursor

        for radius in [28, 22, 16]:

            cv2.circle(
                frame,
                (index_x, index_y),
                radius,
                (0, 255, 255),
                2
            )


        cv2.circle(
            frame,
            (index_x, index_y),
            7,
            (255, 255, 255),
            -1
        )


    # ========================================================
    # DETERMINE HOVER BUTTON
    # ========================================================

    current_hover = None


    if hand_detected:

        for key, button in buttons.items():

            if inside_button(
                index_x,
                index_y,
                button
            ):

                current_hover = key
                break


    # ========================================================
    # DWELL TIMER
    # ========================================================

    progress = 0


    if current_hover is not None:

        if current_hover != hover_button:

            hover_button = current_hover

            hover_start = time.time()


        elapsed_hover = (
            time.time()
            - hover_start
        )


        progress = min(
            elapsed_hover / DWELL_TIME,
            1.0
        )


        if elapsed_hover >= DWELL_TIME:

            # prevent repeated rapid toggling
            if (
                current_hover
                != last_triggered_button

                or

                time.time()
                - last_trigger_time
                > 1.2
            ):

                activate_control(
                    current_hover
                )

                last_triggered_button = (
                    current_hover
                )

                last_trigger_time = time.time()


            hover_start = time.time()


    else:

        hover_button = None


    # ========================================================
    # BUTTON STATES
    # ========================================================

    button_states = {

        "light": home["light"],

        "fan": home["fan"],

        "ac": home["ac"],

        "music": home["music"],

        "door": not home["door_locked"],

        "temp_down": False,

        "temp_up": False,

        "home_scene":
            home["scene"] == "HOME",

        "away_scene":
            home["scene"] == "AWAY"
    }


    # ========================================================
    # DRAW BUTTONS
    # ========================================================

    for key in buttons:

        draw_neon_button(

            frame,

            key,

            active=button_states[key],

            hovered=(
                hover_button == key
            ),

            progress=(
                progress
                if hover_button == key
                else 0
            )
        )


    # ========================================================
    # DEVICE ICONS
    # ========================================================

    draw_light(
        frame,
        180,
        245,
        home["light"]
    )


    if home["fan"]:

        fan_angle += 12


    draw_fan(
        frame,
        450,
        245,
        home["fan"],
        fan_angle
    )


    draw_ac(
        frame,
        720,
        245,
        home["ac"]
    )


    draw_music(
        frame,
        990,
        245,
        home["music"]
    )


    draw_door(
        frame,
        180,
        420,
        home["door_locked"]
    )


    # ========================================================
    # TEMPERATURE DISPLAY
    # ========================================================

    draw_glass_panel(
        frame,
        330,
        485,
        685,
        600,
        color=(120, 220, 255),
        alpha=0.20
    )


    cv2.putText(
        frame,
        "TEMPERATURE",
        (395, 525),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"{home['temperature']} C",
        (440, 575),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.3,
        (80, 255, 255),
        3
    )


    # ========================================================
    # STATUS PANEL
    # ========================================================

    draw_glass_panel(
        frame,
        720,
        485,
        1145,
        635,
        color=(190, 160, 255),
        alpha=0.18
    )


    cv2.putText(
        frame,
        "SYSTEM STATUS",
        (840, 520),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Scene: {home['scene']}",
        (750, 555),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (200, 255, 230),
        2
    )


    door_text = (
        "LOCKED"
        if home["door_locked"]
        else "UNLOCKED"
    )


    cv2.putText(
        frame,
        f"Door: {door_text}",
        (750, 585),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (200, 255, 230),
        2
    )


    hand_text = (
        "HAND DETECTED"
        if hand_detected
        else "NO HAND"
    )


    hand_color = (
        (80, 255, 150)
        if hand_detected
        else (80, 80, 255)
    )


    cv2.putText(
        frame,
        hand_text,
        (750, 615),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        hand_color,
        2
    )


    # ========================================================
    # DEVICE STATUS TEXT
    # ========================================================

    cv2.putText(
        frame,
        "ON" if home["light"] else "OFF",
        (225, 265),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (80, 255, 150)
        if home["light"]
        else (180, 180, 180),
        2
    )


    cv2.putText(
        frame,
        "ON" if home["fan"] else "OFF",
        (495, 265),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (80, 255, 150)
        if home["fan"]
        else (180, 180, 180),
        2
    )


    cv2.putText(
        frame,
        "ON" if home["ac"] else "OFF",
        (765, 265),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (80, 255, 150)
        if home["ac"]
        else (180, 180, 180),
        2
    )


    cv2.putText(
        frame,
        "PLAY"
        if home["music"]
        else "PAUSE",
        (1025, 265),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (80, 255, 150)
        if home["music"]
        else (180, 180, 180),
        2
    )


    # ========================================================
    # FEEDBACK MESSAGE
    # ========================================================

    if (
        time.time()
        - feedback_time
        < 2
    ):

        cv2.putText(
            frame,
            feedback_message,
            (430, 675),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 255, 255),
            3
        )


    # ========================================================
    # FOOTER
    # ========================================================

    cv2.putText(
        frame,
        "R = Reset     Q = Quit",
        (30, 690),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SHOW
    # ========================================================

    cv2.imshow(
        WINDOW_NAME,
        frame
    )


    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


    if key == ord("r"):

        reset_home()


# ============================================================
# CLEANUP
# ============================================================

landmarker.close()

cap.release()

cv2.destroyAllWindows()
