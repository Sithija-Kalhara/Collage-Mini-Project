"""Hand gesture controlled virtual robotic arm — Python 3.14 / MediaPipe Tasks.
No training or scikit-learn. Index finger steers arm; pinch grabs cubes.
One raised index finger drives the base LEFT; index + middle drive RIGHT. A/D also work.
Run: py -3.14 gesture_robot_arm_py314.py
"""
import math
import time
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / 'hand_landmarker.task'
MODEL_URL = ('https://storage.googleapis.com/mediapipe-models/hand_landmarker/'
             'hand_landmarker/float16/1/hand_landmarker.task')
W, H = 1120, 680
PANEL = 330
BASE = np.array([585., 493.])
L1, L2 = 245., 215.  # extended reach so the far-right yellow cube is reachable
ORANGE = (0, 164, 255)  # OpenCV BGR
WHITE = (244, 244, 247)


def ensure_model():
    if not MODEL_PATH.is_file():
        print('Downloading official MediaPipe hand model...')
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return str(MODEL_PATH)

def pt(p):
    return tuple(np.rint(p).astype(int))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def label(img, text, xy, scale=.58, color=WHITE, thick=1):
    cv2.putText(img, text, xy, cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thick, cv2.LINE_AA)


def inverse_kinematics(target):
    direction = target - BASE
    dist = float(np.linalg.norm(direction))
    if dist < 0.001:
        direction = np.array([0., -1.]); dist = 1.
    direction /= dist
    radius = clamp(dist, abs(L1-L2)+.1, L1+L2-.1)
    endpoint = BASE + direction * radius
    phi = math.atan2(direction[1], direction[0])
    cosine = clamp((L1*L1 + radius*radius - L2*L2)/(2*L1*radius), -1, 1)
    shoulder = phi - math.acos(cosine)
    elbow = BASE + L1*np.array([math.cos(shoulder),math.sin(shoulder)])
    return elbow, endpoint


def draw_limb(img, a, b, width=26):
    # Heavy black rim, dark orange shadow, bright orange mechanical shell
    cv2.line(img, pt(a), pt(b), (17, 29, 43), width+8, cv2.LINE_AA)
    cv2.line(img, pt(a), pt(b), (0, 95, 199), width+4, cv2.LINE_AA)
    cv2.line(img, pt(a), pt(b), ORANGE, width, cv2.LINE_AA)
    highlight_a = a + np.array([-3.,-4.]); highlight_b = b + np.array([-3.,-4.])
    cv2.line(img, pt(highlight_a), pt(highlight_b), (72,210,255), 3, cv2.LINE_AA)


def draw_joint(img, center, radius=21):
    c = pt(center)
    cv2.circle(img, c, radius+3, (9,17,27), -1,cv2.LINE_AA)
    cv2.circle(img, c, radius, (178,190,204),-1,cv2.LINE_AA)
    cv2.circle(img, c, radius-5, (70,88,108),-1,cv2.LINE_AA)
    cv2.circle(img, c, radius-10, (192,209,221),-1,cv2.LINE_AA)
    cv2.circle(img, c, 5, (28,44,62),-1,cv2.LINE_AA)


def draw_cube(img, center, color, size=38):
    cx,cy=pt(center)
    half=size//2
    # Front face and dimensional side/top, with outline
    top=np.array([[cx-half,cy-half],[cx,cy-half-10],[cx+half,cy-half],[cx,cy-half+10]],np.int32)
    cv2.rectangle(img,(cx-half,cy-half),(cx+half,cy+half),(18,25,35),-1)
    cv2.rectangle(img,(cx-half+2,cy-half+2),(cx+half-2,cy+half-2),color,-1)
    lighter=tuple(min(255,int(c)+48) for c in color)
    cv2.fillConvexPoly(img,top,lighter)
    cv2.polylines(img,[top],True,(26,36,50),2,cv2.LINE_AA)
    cv2.rectangle(img,(cx-half,cy-half),(cx+half,cy+half),(22,29,38),2)


def draw_claw(img, wrist, tip, is_closed):
    # Two tapered stainless-steel jaws, oriented perpendicular to the arm's final link
    along=np.asarray(tip)-np.asarray(wrist)
    n=np.linalg.norm(along)
    along=along/max(n,1.)
    perp=np.array([-along[1],along[0]])
    spread=7 if is_closed else 19
    for sign in (-1,1):
        outer=tip+perp*spread*sign
        finger=outer+along*27
        inward=finger-perp*7*sign
        cv2.line(img,pt(tip),pt(outer),(28,37,49),11,cv2.LINE_AA)
        cv2.line(img,pt(tip),pt(outer),(201,213,224),7,cv2.LINE_AA)
        cv2.line(img,pt(outer),pt(finger),(28,37,49),10,cv2.LINE_AA)
        cv2.line(img,pt(outer),pt(finger),(201,213,224),6,cv2.LINE_AA)
        cv2.line(img,pt(finger),pt(inward),(225,229,234),5,cv2.LINE_AA)
    draw_joint(img,tip,12)


def draw_hand(img, landmarks):
    h,w=img.shape[:2]
    edges=((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
           (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),
           (13,17),(17,18),(18,19),(19,20),(0,17))
    pts=[(int(p.x*w),int(p.y*h)) for p in landmarks]
    for i,j in edges:
        cv2.line(img,pts[i],pts[j],(62,237,125),2,cv2.LINE_AA)
    for pos in pts:
        cv2.circle(img,pos,4,(64,222,255),-1,cv2.LINE_AA)
    cv2.circle(img,pts[8],8,(80,80,255),2,cv2.LINE_AA)


def main():
    options=mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=ensure_model()),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1, min_hand_detection_confidence=.65,
        min_tracking_confidence=.65)
    cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
    if not cap.isOpened(): cap=cv2.VideoCapture(0)
    if not cap.isOpened(): raise RuntimeError('Camera unavailable. Check Windows camera permissions.')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    target=np.array([825.,340.])
    desired=target.copy()
    cubes=[{'pos':np.array([840.,505.]),'home':(840.,505.),'color':(215,70,70)},
           {'pos':np.array([935.,505.]),'home':(935.,505.),'color':(80,210,75)},
           {'pos':np.array([1035.,505.]),'home':(1035.,505.),'color':(65,190,245)}]
    selected=None
    pinch=False
    base_motion = "STOP"
    start=last_frame=time.monotonic()
    last_ms=0; fps=0.
    try:
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
            while True:
                ok,frame=cap.read()
                if not ok: print('Camera disconnected'); break
                frame=cv2.flip(frame,1)
                rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                now=time.monotonic()
                ms=max(last_ms+1,int((now-start)*1000));last_ms=ms
                result=detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),ms)
                visible=bool(result.hand_landmarks)
                pinch=False
                base_motion = "STOP"
                if visible:
                    lm=result.hand_landmarks[0]
                    draw_hand(frame,lm)
                    desired=np.array([PANEL+95+clamp(lm[8].x,0,1)*(W-PANEL-200),
                                      110+clamp(lm[8].y,0,1)*390],dtype=float)
                    thumb=np.array([lm[4].x,lm[4].y]);index=np.array([lm[8].x,lm[8].y])
                    palm=np.array([lm[0].x,lm[0].y]);mid=np.array([lm[9].x,lm[9].y])
                    ratio=np.linalg.norm(thumb-index)/max(.01,np.linalg.norm(palm-mid))
                    # Hand movement positions the arm in all modes except base steering.
                    # Thumb is ignored for gesture counting.
                    def raised(tip_id, pip_id):
                        t = np.array([lm[tip_id].x, lm[tip_id].y])
                        p = np.array([lm[pip_id].x, lm[pip_id].y])
                        wrist = np.array([lm[0].x, lm[0].y])
                        return np.linalg.norm(t - wrist) > np.linalg.norm(p - wrist) * 1.12

                    fingers = [raised(t, p) for t, p in ((8, 6), (12, 10), (16, 14), (20, 18))]
                    # Priority: pinch to pick/release, then 1/2-finger driving commands.
                    pinch = ratio < (.61 if selected is not None else .43)
                    steering = None
                    if not pinch:
                        if fingers == [True, False, False, False]:
                            steering = 'LEFT'
                        elif fingers == [True, True, False, False]:
                            steering = 'RIGHT'
                    if steering is not None:
                        dx = -5. if steering == 'LEFT' else 5.
                        before = float(BASE[0])
                        BASE[0] = clamp(BASE[0] + dx, PANEL + 95., W - 85.)
                        delta = BASE[0] - before
                        target[0] += delta
                        desired[0] += delta
                        base_motion = steering if abs(delta) > .001 else 'STOP (LIMIT)'
                    else:
                        # Move the arm using hand position for other gestures / pinches.
                        target=.77*target+.23*desired
                elbow,tip=inverse_kinematics(target)
                if not visible or not pinch:
                    selected=None
                if visible and pinch and selected is None:
                    best=min(range(len(cubes)),key=lambda i: np.linalg.norm(cubes[i]['pos']-tip))
                    if np.linalg.norm(cubes[best]['pos']-tip)<45:
                        selected=best
                if selected is not None:
                    cubes[selected]['pos']=tip+np.array([10.,22.])
                screen=np.full((H,W,3),(36,24,13),dtype=np.uint8)
                # Right workspace: dark blue grid, stage, highlights
                cv2.rectangle(screen,(PANEL+8,75),(W-12,H-20),(49,35,18),-1)
                for x in range(PANEL+30,W-10,40):
                    cv2.line(screen,(x,85),(x,H-25),(78,57,35),1)
                for y in range(95,H-20,40):
                    cv2.line(screen,(PANEL+12,y),(W-16,y),(78,57,35),1)
                cv2.rectangle(screen,(PANEL+20,529),(W-24,610),(76,84,89),-1)
                cv2.line(screen,(PANEL+20,529),(W-24,529),(178,183,180),3,cv2.LINE_AA)
                cv2.rectangle(screen,(PANEL+20,529),(W-24,610),(27,32,41),2)
                # Top bar
                cv2.rectangle(screen,(0,0),(W,69),(65,35,18),-1)
                label(screen,'HAND GESTURE  |  ROBOTIC ARM SIMULATOR',(22,45),.86,(255,227,179),2)
                # Webcam/control sidebar
                cv2.rectangle(screen,(10,84),(PANEL-10,H-18),(54,42,31),-1)
                label(screen,'LIVE HAND TRACKING',(24,113),.61,(255,217,154),2)
                mini=cv2.resize(frame,(PANEL-40,230))
                screen[125:355,20:PANEL-20]=mini
                cv2.rectangle(screen,(19,124),(PANEL-19,356),(170,189,201),2)
                label(screen,'HAND: '+('DETECTED' if visible else 'NOT VISIBLE'),(23,397),.58,
                      (124,232,128) if visible else (85,125,255),2)
                label(screen,'GRIPPER: '+('CLOSED' if pinch else 'OPEN'),(23,425),.58,(255,201,123))
                label(screen,'OBJECT: '+('PICKED UP' if selected is not None else 'READY'),(23,453),.58)
                label(screen,'INDEX FINGER - MOVE ARM',(23,508),.52)
                label(screen,'PINCH - PICK / DROP CUBE',(23,537),.52)
                label(screen,'1 FINGER LEFT / 2 RIGHT',(23,566),.49)
                label(screen,'A/D - MOVE BASE   R - RESET',(23,607),.49,(247,204,148))
                label(screen,'Q / ESC - EXIT',(23,636),.58,(247,204,148))
                # Three pickable cubes with shadows
                for i,cube in enumerate(cubes):
                    c=cube['pos']
                    if i != selected:
                        cv2.ellipse(screen,(int(c[0]),548),(29,8),0,0,360,(32,37,40),-1)
                    draw_cube(screen,c,cube['color'])
                # Mechanical support & arm
                cv2.rectangle(screen,(int(BASE[0]-28),int(BASE[1]-10)),
                              (int(BASE[0]+28),int(BASE[1]+48)),(0,135,222),-1)
                cv2.rectangle(screen,(int(BASE[0]-51),int(BASE[1]+43)),
                              (int(BASE[0]+51),int(BASE[1]+83)),(80,83,92),-1)
                cv2.rectangle(screen,(int(BASE[0]-51),int(BASE[1]+43)),
                              (int(BASE[0]+51),int(BASE[1]+83)),(20,27,38),3)
                draw_limb(screen,BASE,elbow,29)
                draw_limb(screen,elbow,tip,24)
                draw_joint(screen,BASE,26)
                draw_joint(screen,elbow,23)
                draw_claw(screen,elbow,tip,pinch)
                # Top-right live telemetry
                shoulder=math.degrees(math.atan2(elbow[1]-BASE[1],elbow[0]-BASE[0]))
                forearm=math.degrees(math.atan2(tip[1]-elbow[1],tip[0]-elbow[0]))
                x0,y0=W-260,89
                cv2.rectangle(screen,(x0,y0),(W-27,y0+150),(15,22,34),-1)
                cv2.rectangle(screen,(x0,y0),(W-27,y0+150),(152,169,186),2)
                label(screen,f'X: {int(tip[0])}   Y: {int(tip[1])}',(x0+13,y0+27),.55)
                label(screen,f'Joint 1: {shoulder:.0f} deg',(x0+13,y0+55),.57,(73,227,255))
                label(screen,f'Joint 2: {forearm-shoulder:.0f} deg',(x0+13,y0+84),.57,(73,227,255))
                label(screen,'Gripper: '+('CLOSED' if pinch else 'OPEN'),(x0+13,y0+113),.56,(119,255,158))
                fps=.88*fps+.12*(1/max(now-last_frame,.001));last_frame=now
                label(screen,f'BASE: {int(BASE[0])}  {base_motion}',(x0+13,y0+138),.5,(213,215,219))
                cv2.imshow('Gesture Robotic Arm Simulator - Python 3.14',screen)
                key=cv2.waitKey(1)&0xFF
                if key in (27,ord('q'),ord('Q')): break
                if key in (ord('a'),ord('A'),ord('d'),ord('D')):
                    dx = -14. if key in (ord('a'),ord('A')) else 14.
                    old_x = float(BASE[0])
                    BASE[0] = clamp(BASE[0] + dx, PANEL + 95., W - 85.)
                    target[0] += BASE[0] - old_x
                    desired[0] += BASE[0] - old_x
                if key in (ord('r'),ord('R')):
                    selected=None
                    for cube in cubes: cube['pos']=np.array(cube['home'],dtype=float)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__=='__main__':
    main()
