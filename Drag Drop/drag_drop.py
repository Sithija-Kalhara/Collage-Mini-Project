import cv2
import mediapipe as mp
import math
import time
import numpy as np
import random

# ============================
# MEDIAPIPE TASKS SETUP
# ============================

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

# ============================
# CAMERA
# ============================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# =========================
# GAME SETTINGS
# =========================

rabbit_x = 300
rabbit_y = 350
rabbit_size = 140

carrot_x = 900
carrot_y = 350
carrot_size = 120

dragging = False

score = 0

start_time = time.time()

last_scored = False

# ============================
# HAND CONNECTIONS
# ============================

connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),

    (0, 5), (5, 6), (6, 7), (7, 8),

    (5, 9), (9, 10), (10, 11), (11, 12),

    (9, 13), (13, 14), (14, 15), (15, 16),

    (13, 17), (17, 18), (18, 19), (19, 20),

    (0, 17)
]


# ============================
# DRAW GLASSY RABBIT
# ============================

def draw_rabbit(frame, cx, cy, size, dragging=False):

    overlay = frame.copy()

    if dragging:
        body = (180, 255, 220)
        glow = (100, 255, 180)
    else:
        body = (245, 220, 255)
        glow = (255, 210, 255)

    belly = (255, 245, 255)
    ear = (235, 190, 245)

    # Shadow
    cv2.ellipse(
        overlay,
        (cx, cy + size // 2 + 15),
        (size // 3, size // 10),
        0, 0, 360,
        (40, 40, 40),
        -1
    )

    # Ears
    cv2.ellipse(
        overlay,
        (cx - size // 6, cy - size // 2),
        (size // 10, size // 3),
        -10, 0, 360,
        body,
        -1
    )

    cv2.ellipse(
        overlay,
        (cx + size // 6, cy - size // 2),
        (size // 10, size // 3),
        10, 0, 360,
        body,
        -1
    )

    cv2.ellipse(
        overlay,
        (cx - size // 6, cy - size // 2),
        (size // 22, size // 4),
        -10, 0, 360,
        ear,
        -1
    )

    cv2.ellipse(
        overlay,
        (cx + size // 6, cy - size // 2),
        (size // 22, size // 4),
        10, 0, 360,
        ear,
        -1
    )

    # Body
    cv2.ellipse(
        overlay,
        (cx, cy + 20),
        (size // 3, size // 2),
        0, 0, 360,
        body,
        -1
    )

    # Head
    cv2.circle(
        overlay,
        (cx, cy - size // 6),
        size // 3,
        body,
        -1
    )

    # Belly
    cv2.ellipse(
        overlay,
        (cx, cy + size // 5),
        (size // 5, size // 4),
        0, 0, 360,
        belly,
        -1
    )

    # Eyes
    eye_y = cy - size // 5
    eye_gap = size // 9

    for ex in [cx - eye_gap, cx + eye_gap]:

        cv2.circle(
            overlay,
            (ex, eye_y),
            size // 22,
            (255, 255, 255),
            -1
        )

        cv2.circle(
            overlay,
            (ex, eye_y),
            size // 40,
            (20, 20, 20),
            -1
        )

    # Nose
    nose = np.array([
        [cx, cy - size // 10],
        [cx - size // 25, cy - size // 14],
        [cx + size // 25, cy - size // 14]
    ])

    cv2.fillPoly(
        overlay,
        [nose],
        (160, 130, 255)
    )

    # Feet
    cv2.ellipse(
        overlay,
        (cx - size // 5, cy + size // 2),
        (size // 8, size // 15),
        0, 0, 360,
        body,
        -1
    )

    cv2.ellipse(
        overlay,
        (cx + size // 5, cy + size // 2),
        (size // 8, size // 15),
        0, 0, 360,
        body,
        -1
    )

    # Glass highlight
    cv2.ellipse(
        overlay,
        (cx - size // 10, cy - size // 4),
        (size // 14, size // 7),
        25, 0, 360,
        (255, 255, 255),
        -1
    )

    # Glow ring
    cv2.circle(
        overlay,
        (cx, cy),
        size // 2 + 12,
        glow,
        3
    )

    alpha = 0.62 if dragging else 0.48

    cv2.addWeighted(
        overlay,
        alpha,
        frame,
        1 - alpha,
        0,
        frame
    )


# ============================
# DRAW GLOWING CARROT
# ============================

def draw_carrot(frame, cx, cy, size):

    glow = frame.copy()

    pulse = int(
        10 + abs(math.sin(time.time() * 3)) * 10
    )

    # Glow circles
    for radius in range(
        size // 2 + pulse,
        size // 2,
        -4
    ):
        cv2.circle(
            glow,
            (cx, cy),
            radius,
            (0, 140, 255),
            2
        )

    cv2.addWeighted(
        glow,
        0.25,
        frame,
        0.75,
        0,
        frame
    )

    # Carrot body
    carrot = np.array([
        [cx - size // 5, cy - size // 4],
        [cx + size // 5, cy - size // 4],
        [cx, cy + size // 2]
    ])

    cv2.fillPoly(
        frame,
        [carrot],
        (0, 140, 255)
    )

    # Carrot detail lines
    cv2.line(
        frame,
        (cx - size // 8, cy),
        (cx + size // 10, cy + 5),
        (0, 100, 220),
        2
    )

    cv2.line(
        frame,
        (cx - size // 10, cy + size // 6),
        (cx + size // 12, cy + size // 5),
        (0, 100, 220),
        2
    )

    # Leaves
    cv2.ellipse(
        frame,
        (cx - size // 10, cy - size // 3),
        (size // 12, size // 5),
        -25, 0, 360,
        (60, 200, 60),
        -1
    )

    cv2.ellipse(
        frame,
        (cx + size // 10, cy - size // 3),
        (size // 12, size // 5),
        25, 0, 360,
        (60, 200, 60),
        -1
    )

    cv2.ellipse(
        frame,
        (cx, cy - size // 3),
        (size // 12, size // 5),
        0, 0, 360,
        (70, 220, 70),
        -1
    )


# ============================
# COLLISION CHECKS
# ============================

def inside_rabbit(px, py, cx, cy, size):

    return (
        cx - size // 2 < px < cx + size // 2
        and
        cy - size // 2 < py < cy + size // 2
    )


def rabbit_on_carrot(rx, ry, cx, cy):

    distance = math.hypot(
        rx - cx,
        ry - cy
    )

    return distance < 90


# ============================
# RANDOMIZE CARROT
# ============================

def move_carrot(width, height):

    x = random.randint(
        width // 2,
        width - 150
    )

    y = random.randint(
        150,
        height - 150
    )

    return x, y


# ============================
# MAIN LOOP
# ============================

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape


    # ============================
    # GLASSY HUD
    # ============================

    hud = frame.copy()

    cv2.rectangle(
        hud,
        (15, 15),
        (330, 120),
        (230, 230, 230),
        -1
    )

    cv2.addWeighted(
        hud,
        0.18,
        frame,
        0.82,
        0,
        frame
    )


    # ============================
    # MEDIAPIPE IMAGE
    # ============================

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


    # ============================
    # HAND TRACKING
    # ============================

    if result.hand_landmarks:

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

            cv2.circle(
                frame,
                (x, y),
                4,
                (100, 255, 180),
                -1
            )

        for start, end in connections:

            cv2.line(
                frame,
                points[start],
                points[end],
                (255, 255, 255),
                2
            )


        # Thumb + index
        thumb_x, thumb_y = points[4]
        index_x, index_y = points[8]


        cv2.circle(
            frame,
            (thumb_x, thumb_y),
            11,
            (255, 0, 255),
            -1
        )

        cv2.circle(
            frame,
            (index_x, index_y),
            11,
            (255, 0, 255),
            -1
        )


        cv2.line(
            frame,
            (thumb_x, thumb_y),
            (index_x, index_y),
            (255, 0, 255),
            3
        )


        distance = math.hypot(
            index_x - thumb_x,
            index_y - thumb_y
        )


        pinch_x = (
            thumb_x + index_x
        ) // 2

        pinch_y = (
            thumb_y + index_y
        ) // 2


        cv2.circle(
            frame,
            (pinch_x, pinch_y),
            7,
            (0, 255, 255),
            -1
        )


        over_rabbit = inside_rabbit(
            pinch_x,
            pinch_y,
            rabbit_x,
            rabbit_y,
            rabbit_size
        )


        # Grab
        if distance < 50 and over_rabbit:

            dragging = True


        # Move rabbit
        if dragging:

            rabbit_x = pinch_x
            rabbit_y = pinch_y


        # Release
        if distance > 80:

            if dragging:

                dragging = False

                # Score check
                if rabbit_on_carrot(
                    rabbit_x,
                    rabbit_y,
                    carrot_x,
                    carrot_y
                ):

                    score += 1

                    carrot_x, carrot_y = move_carrot(
                        width,
                        height
                    )

                    rabbit_x = 250
                    rabbit_y = 350


    # ============================
    # RABBIT BOUNCE
    # ============================

    bounce = 0

    if not dragging:

        elapsed = (
            time.time()
            - start_time
        )

        bounce = int(
            math.sin(elapsed * 3) * 4
        )


    # ============================
    # DRAW GAME OBJECTS
    # ============================

    draw_carrot(
        frame,
        carrot_x,
        carrot_y,
        carrot_size
    )

    draw_rabbit(
        frame,
        rabbit_x,
        rabbit_y + bounce,
        rabbit_size,
        dragging
    )


    # ============================
    # SCORE
    # ============================

    cv2.putText(
        frame,
        f"SCORE: {score}",
        (30, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )


    # ============================
    # STATUS
    # ============================

    if dragging:

        status = "Rabbit grabbed!"

        color = (100, 255, 180)

    else:

        status = "Drag rabbit to carrot"

        color = (255, 255, 255)


    cv2.putText(
        frame,
        status,
        (30, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2
    )


    # ============================
    # INSTRUCTIONS
    # ============================

    cv2.putText(
        frame,
        "Pinch = Grab",
        (20, height - 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Open fingers = Drop",
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    cv2.imshow(
        "Rabbit Carrot Game",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================
# CLEANUP
# ============================

landmarker.close()

cap.release()

cv2.destroyAllWindows()
