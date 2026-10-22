"""Enhanced virtual gesture-controlled car for Python 3.14.

Install: py -3.14 -m pip install --upgrade mediapipe opencv-python numpy
Run:     py -3.14 gesture_car_enhanced_py314.py

MediaPipe Tasks pretrained hand landmarks; no custom gesture data or sklearn.
Gesture commands (four non-thumb fingers):
  fist -> FORWARD, index -> LEFT, index+middle -> RIGHT,
  index+middle+ring -> REVERSE, four fingers -> STOP.
No hand / unrecognized hand -> STOP immediately.
Keyboard: Q/ESC quit, R reset, P pause, +/- adjust maximum speed.
"""
from __future__ import annotations

from collections import deque
import math
from pathlib import Path
import time
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/1/hand_landmarker.task")
MODEL_PATH = Path(__file__).resolve().parent / "hand_landmarker.task"
VIEW_W, VIEW_H = 900, 630
ROAD_L, ROAD_R = 95, 690
CAR_W, CAR_H = 58, 94
FINGER_JOINTS = ((8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17))
COMMANDS = {
    (False, False, False, False): "FORWARD",
    (True, False, False, False): "LEFT",
    (True, True, False, False): "RIGHT",
    (True, True, True, False): "REVERSE",
    (True, True, True, True): "STOP",
}
EDGES = ((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
         (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),
         (13,17),(17,18),(18,19),(19,20),(0,17))


def download_model():
    if MODEL_PATH.is_file() and MODEL_PATH.stat().st_size > 100_000:
        return
    print("Downloading MediaPipe hand landmarker model (one-time)...")
    part = MODEL_PATH.with_suffix(".part")
    try:
        urllib.request.urlretrieve(MODEL_URL, part)
        if part.stat().st_size < 100_000:
            raise RuntimeError("Downloaded model is too small")
        part.replace(MODEL_PATH)
    except Exception:
        part.unlink(missing_ok=True)
        raise


def joint_extended(points, tip, pip, mcp):
    a = np.array((points[tip].x, points[tip].y, points[tip].z))
    b = np.array((points[pip].x, points[pip].y, points[pip].z))
    c = np.array((points[mcp].x, points[mcp].y, points[mcp].z))
    v, w = a-b, c-b
    cosine = np.dot(v, w) / max(1e-8, np.linalg.norm(v) * np.linalg.norm(w))
    return math.degrees(math.acos(float(np.clip(cosine, -1, 1)))) >= 155


def classify(points):
    state = tuple(joint_extended(points, *j) for j in FINGER_JOINTS)
    return COMMANDS.get(state, "STOP")


def overlay_landmarks(frame, points):
    h, w = frame.shape[:2]
    coords = [(int(p.x*w), int(p.y*h)) for p in points]
    for a, b in EDGES:
        cv2.line(frame, coords[a], coords[b], (52, 235, 120), 2, cv2.LINE_AA)
    for p in coords:
        cv2.circle(frame, p, 4, (40, 80, 255), -1, cv2.LINE_AA)


def text(img, message, xy, scale=0.6, color=(245,245,245), thickness=1):
    cv2.putText(img, message, xy, cv2.FONT_HERSHEY_SIMPLEX, scale,
                color, thickness, cv2.LINE_AA)


class Car:
    def __init__(self):
        self.max_speed = 290.0
        self.reset()

    def reset(self):
        self.x = (ROAD_L + ROAD_R) / 2
        self.y = VIEW_H * .58
        self.vx = self.vy = 0.0
        self.travel = 0.0

    def update(self, command, dt):
        # Arrow-like gesture actions; smoothly accelerate in any of four directions.
        directions = {"FORWARD":(0,-1), "REVERSE":(0,1),
                      "LEFT":(-1,0), "RIGHT":(1,0)}
        dx, dy = directions.get(command, (0,0))
        desired_x, desired_y = dx*self.max_speed, dy*self.max_speed
        # Braking is intentionally stronger than acceleration.
        response = 11.0 if command == "STOP" else 5.5
        blend = 1.0 - math.exp(-response * dt)
        self.vx += (desired_x-self.vx)*blend
        self.vy += (desired_y-self.vy)*blend
        # STOP must halt immediately, including when tracking is lost.
        if command == "STOP":
            self.vx = self.vy = 0.0
        ox, oy = self.x, self.y
        self.x = float(np.clip(self.x+self.vx*dt,
                               ROAD_L + CAR_W/2 + 13, ROAD_R-CAR_W/2-13))
        self.y = float(np.clip(self.y+self.vy*dt,
                               CAR_H/2+12, VIEW_H-CAR_H/2-12))
        self.travel += math.hypot(self.x-ox, self.y-oy)

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)


def render(car, command, raw, fps, camera_ok, paused, lane_offset):
    screen = np.zeros((VIEW_H, VIEW_W, 3), np.uint8)
    screen[:] = (40, 105, 44)
    cv2.rectangle(screen, (ROAD_L, 0), (ROAD_R, VIEW_H), (67,67,67), -1)
    for border in (ROAD_L+7, ROAD_R-7):
        cv2.line(screen, (border,0),(border,VIEW_H),(210,210,210),4)
    for line_x in (ROAD_L+(ROAD_R-ROAD_L)//3, ROAD_L+2*(ROAD_R-ROAD_L)//3):
        for y in range(-75, VIEW_H+75, 94):
            yy = int(y + lane_offset) % (VIEW_H+94)-94
            cv2.line(screen,(line_x,yy),(line_x,yy+46),(190,190,190),4)
    x,y = int(car.x),int(car.y)
    x0,y0 = x-CAR_W//2,y-CAR_H//2
    x1,y1 = x0+CAR_W,y0+CAR_H
    cv2.ellipse(screen, (x+4,y+7),(CAR_W//2+12,CAR_H//2+9),0,0,360,(31,31,31),-1)
    for wx in (x0-8,x1+1):
        for wy in (y0+11,y1-27):
            cv2.rectangle(screen,(wx,wy),(wx+7,wy+17),(15,15,15),-1)
    cv2.rectangle(screen,(x0,y0),(x1,y1),(40,50,218),-1)
    cv2.rectangle(screen,(x0+9,y0+14),(x1-9,y0+36),(220,184,112),-1)
    cv2.rectangle(screen,(x0+10,y1-24),(x1-10,y1-12),(157,125,86),-1)
    for xx in (x0+10,x1-10):
        cv2.circle(screen,(xx,y0+5),5,(189,242,255),-1)
    # Dashboard
    cv2.rectangle(screen,(700,0),(VIEW_W,VIEW_H),(29,35,44),-1)
    text(screen,"GESTURE CAR",(712,40),.68,(255,255,255),2)
    cv2.line(screen,(712,55),(888,55),(90,90,90),1)
    text(screen,"COMMAND",(712,91),.51,(190,197,205))
    text(screen,command,(712,120),.85,(100,225,145) if command != "STOP" else (98,185,255),2)
    text(screen,"RAW: " + raw,(712,147),.44)
    text(screen,"SPEED",(712,184),.52,(190,197,205))
    text(screen,f"{car.speed:5.0f} px/s",(712,211),.7)
    cv2.rectangle(screen,(713,226),(875,240),(70,70,70),-1)
    cv2.rectangle(screen,(713,226),(713+int(162*min(1,car.speed/max(car.max_speed,1))),240),(80,204,130),-1)
    text(screen,f"MAX: {int(car.max_speed)} px/s",(712,269),.52)
    text(screen,f"FPS: {fps:.0f}",(712,305),.56)
    text(screen,f"DIST: {car.travel:.0f} px",(712,334),.52)
    text(screen,"HAND: " + ("FOUND" if camera_ok else "MISSING"),(712,370),.47,
         (90,220,150) if camera_ok else (90,120,255))
    if paused:
        text(screen,"PAUSED",(712,410),.75,(90,200,255),2)
    cv2.line(screen,(712,437),(888,437),(90,90,90),1)
    for j, line in enumerate(("Fist      = Forward", "1 finger  = Left", "2 fingers = Right",
                               "3 fingers = Reverse", "4 fingers = Stop", "R reset | P pause",
                               "+/- speed | Q quit")):
        text(screen,line,(712,460+j*22),.39)
    return screen


def main():
    download_model()
    settings = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.VIDEO, num_hands=1,
        min_hand_detection_confidence=.6,
        min_hand_presence_confidence=.6, min_tracking_confidence=.5)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Webcam could not open. Check Windows camera permission.")
    car, history = Car(), deque(maxlen=5)
    paused = False
    last_time = time.monotonic()
    frame_timestamp = 0
    fps = 0.0
    lane_offset = 0.0
    try:
        with vision.HandLandmarker.create_from_options(settings) as detector:
            while True:
                ok, frame = cap.read()
                if not ok:
                    print("Webcam disconnected. Stopping.")
                    break
                frame = cv2.flip(frame,1)
                frame_timestamp = max(frame_timestamp+1, int(time.monotonic()*1000))
                image = mp.Image(image_format=mp.ImageFormat.SRGB,
                                 data=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
                result = detector.detect_for_video(image,frame_timestamp)
                has_hand = bool(result.hand_landmarks)
                raw = "STOP"
                if has_hand:
                    points = result.hand_landmarks[0]
                    raw = classify(points)
                    overlay_landmarks(frame, points)
                    history.append(raw)
                    # Preserve immediate STOP on unknown or open-palm gestures.
                    command = "STOP" if raw == "STOP" else (
                        raw if history.count(raw) >= 3 else "STOP")
                else:
                    history.clear()
                    command = "STOP"  # no hand -> immediate safety stop
                now = time.monotonic()
                dt = min(.08, max(0.0, now-last_time))
                last_time = now
                fps = fps*.85 + (1/dt if dt else 0)*.15
                if not paused:
                    car.update(command, dt)
                    lane_offset = (lane_offset + car.vy*dt*.5) % 94
                else:
                    car.update("STOP", 0)
                    command = "STOP"
                text(frame,f"DETECTED: {raw}",(15,36),.82,(60,250,130),2)
                text(frame,f"CONTROL: {command}",(15,70),.7,(255,230,130),2)
                text(frame,"Q=Quit   R=Reset   P=Pause   +/-=Speed",
                     (15,frame.shape[0]-16),.54,(240,240,240),2)
                cv2.imshow("Hand Gesture Camera", frame)
                cv2.imshow("Gesture Car - Enhanced", render(car,command,raw,fps,has_hand,paused,lane_offset))
                key = cv2.waitKey(1) & 0xFF
                if key in (27,ord('q')):
                    break
                if key == ord('r'):
                    car.reset()
                elif key == ord('p'):
                    paused = not paused
                elif key in (ord('+'),ord('=')):
                    car.max_speed = min(600,car.max_speed+25)
                elif key in (ord('-'),ord('_')):
                    car.max_speed = max(75,car.max_speed-25)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
