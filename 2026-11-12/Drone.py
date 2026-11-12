
"""Enhanced hand-gesture virtual drone, Python 3.14 / MediaPipe Tasks.

Controls: index = LEFT, index+middle = RIGHT, three fingers = UP,
closed fist = DOWN, four fingers = HOVER. No hand = emergency hover.
Keys: P pause, R restart, 1/2/3 difficulty, H toggle help, Q/Esc quit.
No training data / sklearn / joblib required.
"""
import math
import random
import time
import urllib.request
from collections import Counter, deque
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

HERE = Path(__file__).resolve().parent
MODEL = HERE / 'hand_landmarker.task'
MODEL_URL = ('https://storage.googleapis.com/mediapipe-models/hand_landmarker/'
             'hand_landmarker/float16/1/hand_landmarker.task')
W, H, GAME_W = 1180, 740, 835
SIDEBAR = W - GAME_W
TOP = 78
BGR_WHITE = (245, 250, 255)
EDGES = ((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
         (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),
         (13,17),(17,18),(18,19),(19,20),(0,17))
DIFFICULTIES = {
    1: {'name':'EASY', 'speed': 180., 'spawn': 2.1, 'fall': 95., 'lives': 4},
    2: {'name':'NORMAL', 'speed': 245., 'spawn': 1.5, 'fall': 140., 'lives': 3},
    3: {'name':'HARD', 'speed': 310., 'spawn': 1.0, 'fall': 195., 'lives': 2},
}


def put(img, value, xy, size=.56, color=BGR_WHITE, thick=1):
    cv2.putText(img, str(value), (int(xy[0]),int(xy[1])),
                cv2.FONT_HERSHEY_SIMPLEX, size, color, thick, cv2.LINE_AA)


def panel(img, x1, y1, x2, y2, fill, rim=None):
    cv2.rectangle(img, (x1,y1), (x2,y2), fill, -1)
    if rim is not None:
        cv2.rectangle(img, (x1,y1), (x2,y2), rim, 1, cv2.LINE_AA)


def ensure_model():
    if not MODEL.exists() or MODEL.stat().st_size < 1_000_000:
        print('Downloading MediaPipe Hand Landmarker model...')
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL)
        except Exception as e:
            raise RuntimeError('Could not download hand_landmarker.task. '
                               'Download it into the script folder manually.') from e
    return str(MODEL)


def gesture(hand):
    fingers=[]
    # Ignore the thumb; 4 robust finger-extension tests independent of hand side.
    for tip, pip, mcp in ((8,6,5),(12,10,9),(16,14,13),(20,18,17)):
        t=np.array([hand[tip].x,hand[tip].y])
        p=np.array([hand[pip].x,hand[pip].y])
        m=np.array([hand[mcp].x,hand[mcp].y])
        fingers.append(np.linalg.norm(t-m) > 1.35*np.linalg.norm(p-m))
    return {
        (0,0,0,0):'DOWN',
        (1,0,0,0):'LEFT',
        (1,1,0,0):'RIGHT',
        (1,1,1,0):'UP',
        (1,1,1,1):'HOVER'
    }.get(tuple(map(int,fingers)),'HOVER')


def draw_hand(img, hand):
    h,w=img.shape[:2]
    pts=[(int(p.x*w),int(p.y*h)) for p in hand]
    for a,b in EDGES:
        cv2.line(img,pts[a],pts[b],(90,245,138),2,cv2.LINE_AA)
    for p in pts:
        cv2.circle(img,p,3,(56,213,255),-1,cv2.LINE_AA)
    cv2.circle(img,pts[8],7,(75,92,255),2,cv2.LINE_AA)


def new_game(level):
    return dict(x=GAME_W*.5,y=H*.65,vx=0.,vy=0.,elapsed=0.,
                score=0.,best_score=0,obstacles=[],pickups=[],
                spawn=0.,ring_spawn=0.,lives=DIFFICULTIES[level]['lives'],
                invulnerable=1.5,game_over=False,collected=0,combo=0,
                distance=0.,damage_flash=0.)


def sky(scene, t):
    # Blue gradient, faint moving altitude grid and clouds.
    for yy in range(TOP,H):
        v=(yy-TOP)/(H-TOP)
        cv2.line(scene,(0,yy),(GAME_W,yy),
                 (int(189-43*v),int(152-51*v),int(93-28*v)),1)
    for x in range(20,GAME_W,75):
        cv2.line(scene,(x,TOP),(x,H-8),(175,135,102),1)
    for y in range(TOP+28,H,75):
        yy=int(TOP+(y-TOP+t*15)%(H-TOP))
        cv2.line(scene,(0,yy),(GAME_W,yy),(173,139,112),1)
    for i in range(11):
        cx=int((i*211+68+15*math.sin(i*4.3))%GAME_W)
        cy=int((i*137+t*(18+i%3*7))%(H+130))-65
        cv2.ellipse(scene,(cx,cy),(56,17),0,0,360,(212,188,166),-1,cv2.LINE_AA)
        cv2.ellipse(scene,(cx+10,cy-11),(39,18),0,0,360,(235,213,193),-1,cv2.LINE_AA)
    cv2.rectangle(scene,(3,TOP+2),(GAME_W-4,H-5),(242,226,194),2)


def draw_drone(scene,x,y,t,vx,invulnerable):
    x,y=int(x),int(y)
    if invulnerable > 0 and int(t*10)%2==0:
        cv2.circle(scene,(x,y),76,(115,238,255),2,cv2.LINE_AA)
    cv2.ellipse(scene,(x+8,y+48),(69,14),0,0,360,(76,107,114),-1,cv2.LINE_AA)
    for i,(ox,oy) in enumerate(((-45,-32),(45,-32),(-45,32),(45,32))):
        end=(x+ox,y+oy)
        cv2.line(scene,(x,y),end,(25,37,52),15,cv2.LINE_AA)
        cv2.line(scene,(x,y),end,(164,186,208),8,cv2.LINE_AA)
        cv2.circle(scene,end,21,(37,63,86),-1,cv2.LINE_AA)
        cv2.circle(scene,end,18,(58,188,217),2,cv2.LINE_AA)
        angle=t*24+i*.9
        dd=(round(21*math.cos(angle)),round(10*math.sin(angle)))
        cv2.line(scene,(end[0]-dd[0],end[1]-dd[1]),
                 (end[0]+dd[0],end[1]+dd[1]),(230,252,253),3,cv2.LINE_AA)
        cv2.circle(scene,end,5,(250,247,240),-1,cv2.LINE_AA)
    tilt=round(np.clip(vx/25,-12,12))
    cv2.ellipse(scene,(x,y),(39,29),tilt,0,360,(34,63,89),-1,cv2.LINE_AA)
    cv2.ellipse(scene,(x,y),(31,22),tilt,0,360,(240,198,68),-1,cv2.LINE_AA)
    cv2.ellipse(scene,(x,y-5),(13,10),0,0,360,(246,250,249),-1,cv2.LINE_AA)
    cv2.circle(scene,(x-30,y-25),5,(70,75,255),-1,cv2.LINE_AA)
    cv2.circle(scene,(x+30,y-25),5,(69,255,92),-1,cv2.LINE_AA)


def draw_obstacle(img,o):
    x,y,r=round(o['x']),round(o['y']),o['r']
    cv2.circle(img,(x,y),r+7,(35,57,81),-1,cv2.LINE_AA)
    cv2.circle(img,(x,y),r,(51,76,240),-1,cv2.LINE_AA)
    cv2.circle(img,(x-7,y-7),max(5,r//3),(122,165,250),-1,cv2.LINE_AA)
    cv2.circle(img,(x,y),r+7,(239,223,173),2,cv2.LINE_AA)


def draw_ring(img,o,t):
    x,y=round(o['x']),round(o['y'])
    radius=round(24+2*math.sin(t*6))
    cv2.circle(img,(x,y),radius+5,(22,74,123),5,cv2.LINE_AA)
    cv2.circle(img,(x,y),radius,(54,233,255),5,cv2.LINE_AA)
    cv2.circle(img,(x,y),radius-8,(160,250,255),2,cv2.LINE_AA)
    put(img,'+25',(x-19,y+5),.42,(248,255,255),2)


def spawn_obstacle(s,random_gen,level):
    cfg=DIFFICULTIES[level]
    s['obstacles'].append(dict(x=random_gen.randint(60,GAME_W-60),
        y=TOP-40.,r=random_gen.randint(20,31),
        speed=cfg['fall']*random_gen.uniform(.82,1.27)))


def spawn_ring(s,random_gen,level):
    cfg=DIFFICULTIES[level]
    s['pickups'].append(dict(x=random_gen.randint(65,GAME_W-65),
        y=TOP-40.,speed=cfg['fall']*.83))


def update_game(s,dt,command,hand_found,level,rng):
    if s['game_over']:
        return
    cfg=DIFFICULTIES[level]
    s['elapsed']+=dt
    s['damage_flash']=max(0.,s['damage_flash']-dt)
    s['invulnerable']=max(0.,s['invulnerable']-dt)
    dx={'LEFT':-1,'RIGHT':1}.get(command,0)
    dy={'UP':-1,'DOWN':1}.get(command,0)
    speed=cfg['speed']
    factor=min(1.,dt*8.5)
    s['vx']+=(dx*speed-s['vx'])*factor
    s['vy']+=(dy*speed-s['vy'])*factor
    if not hand_found:  # safety: no hand = no movement
        s['vx']=s['vy']=0.
    oldx,oldy=s['x'],s['y']
    s['x']=float(np.clip(s['x']+s['vx']*dt,70,GAME_W-70))
    s['y']=float(np.clip(s['y']+s['vy']*dt,TOP+90,H-73))
    s['distance']+=math.hypot(s['x']-oldx,s['y']-oldy)
    s['score']+=dt*3
    s['spawn']+=dt
    s['ring_spawn']+=dt
    obstacle_interval=max(.67,cfg['spawn']-s['elapsed']*.002)
    if s['spawn']>=obstacle_interval:
        s['spawn']=0.
        spawn_obstacle(s,rng,level)
    if s['ring_spawn']>=3.2:
        s['ring_spawn']=0.
        spawn_ring(s,rng,level)
    remaining=[]
    for o in s['obstacles']:
        o['y']+=o['speed']*dt
        if math.hypot(o['x']-s['x'],o['y']-s['y']) < o['r']+33:
            if s['invulnerable']<=0:
                s['lives']-=1
                s['invulnerable']=2.0
                s['damage_flash']=.3
                s['combo']=0
                if s['lives']<=0:
                    s['game_over']=True
            # remove hit obstacle to avoid repeat collisions
            continue
        if o['y']<H+48:
            remaining.append(o)
        else:
            s['score']+=8
    s['obstacles']=remaining
    remaining=[]
    for o in s['pickups']:
        o['y']+=o['speed']*dt
        if math.hypot(o['x']-s['x'],o['y']-s['y'])<48:
            s['combo']=min(5,s['combo']+1)
            s['score']+=25*s['combo']
            s['collected']+=1
        elif o['y']<H+40:
            remaining.append(o)
        else:
            s['combo']=0
    s['pickups']=remaining


def draw_hud(scene,s,level,command,hand_found,fps,frame,pause,show_help):
    panel(scene,0,0,W,TOP-1,(47,34,24))
    put(scene,'GESTURE CONTROLLED  |  DRONE FLIGHT+', (20,48),.84,(255,238,193),2)
    panel(scene,GAME_W+5,TOP+9,W-9,H-10,(54,43,31),(127,124,115))
    put(scene,'LIVE HAND TRACKING',(GAME_W+20,113),.62,(255,232,165),2)
    preview=cv2.resize(frame,(SIDEBAR-48,213))
    scene[128:341,GAME_W+24:W-24]=preview
    cv2.rectangle(scene,(GAME_W+23,127),(W-23,342),(216,216,218),2)
    x=GAME_W+21
    put(scene,'HAND: '+('DETECTED' if hand_found else 'LOST'),(x,374),.57,
        (107,242,150) if hand_found else (91,102,255),2)
    put(scene,'GESTURE: '+command,(x,406),.61,(252,231,170),2)
    put(scene,f'DIFFICULTY: {DIFFICULTIES[level]["name"]}',(x,438),.57)
    put(scene,f'SCORE: {int(s["score"])}    LIVES: {s["lives"]}',(x,470),.55)
    put(scene,f'RINGS: {s["collected"]}    COMBO: x{s["combo"]}',(x,500),.52)
    put(scene,f'SPEED: {math.hypot(s["vx"],s["vy"]):.0f}   FPS: {fps:.0f}',(x,531),.52)
    if show_help:
        put(scene,'1 FINGER    LEFT',(x,566),.47)
        put(scene,'2 FINGERS   RIGHT',(x,589),.47)
        put(scene,'3 FINGERS   UP',(x,612),.47)
        put(scene,'FIST        DOWN',(x,635),.47)
        put(scene,'OPEN PALM   HOVER',(x,658),.47)
    else:
        put(scene,'PRESS H TO SHOW GESTURES',(x,586),.48,(240,223,172))
    put(scene,'1/2/3 LEVEL  P PAUSE  R RESET',(x,696),.43,(250,225,174))
    put(scene,'H HELP  Q/ESC EXIT',(x,719),.43,(250,225,174))
    if s['damage_flash']>0:
        cv2.rectangle(scene,(8,TOP+8),(GAME_W-8,H-10),(64,60,252),8)
    if pause or s['game_over']:
        panel(scene,140,300,GAME_W-140,423,(34,40,59),(181,211,246))
        msg='GAME OVER' if s['game_over'] else 'PAUSED'
        put(scene,msg,(285,352),1.1,(255,248,226),3)
        put(scene,'PRESS R TO RESTART' if s['game_over'] else 'PRESS P TO RESUME',
            (255,394),.7,(237,227,185),2)


def main():
    level=2
    state=new_game(level)
    rng=random.Random()
    history=deque(maxlen=5)
    pause=False
    show_help=True
    options=mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=ensure_model()),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=.65,
        min_tracking_confidence=.65)
    cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap=cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError('Webcam unavailable. Check camera access in Windows settings.')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    last=time.monotonic()
    start=last
    last_ms=0
    fps=0.
    try:
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as tracker:
            while True:
                ok,frame=cap.read()
                if not ok:
                    print('Webcam disconnected')
                    break
                frame=cv2.flip(frame,1)
                rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                now=time.monotonic()
                dt=max(.001,min(.05,now-last))
                last=now
                fps=.9*fps+.1/dt
                ms=max(last_ms+1,int((now-start)*1000))
                last_ms=ms
                result=tracker.detect_for_video(
                    mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),ms)
                hand_found=bool(result.hand_landmarks)
                if hand_found:
                    hand=result.hand_landmarks[0]
                    draw_hand(frame,hand)
                    history.append(gesture(hand))
                    command=Counter(history).most_common(1)[0][0]
                else:
                    history.clear()
                    command='HOVER'
                if not pause and not state['game_over']:
                    update_game(state,dt,command,hand_found,level,rng)
                scene=np.zeros((H,W,3),np.uint8)
                sky(scene,state['elapsed'])
                for o in state['pickups']:
                    draw_ring(scene,o,state['elapsed'])
                for o in state['obstacles']:
                    draw_obstacle(scene,o)
                draw_drone(scene,state['x'],state['y'],state['elapsed'],
                           state['vx'],state['invulnerable'])
                draw_hud(scene,state,level,command,hand_found,fps,frame,pause,show_help)
                cv2.imshow('Virtual Gesture Drone - Enhanced Python 3.14',scene)
                key=cv2.waitKey(1)&0xff
                if key in (ord('q'),ord('Q'),27):
                    break
                elif key in (ord('r'),ord('R')):
                    state=new_game(level)
                    pause=False
                    history.clear()
                elif key in (ord('p'),ord('P')):
                    pause=not pause
                elif key in (ord('h'),ord('H')):
                    show_help=not show_help
                elif key in (ord('1'),ord('2'),ord('3')):
                    level=int(chr(key))
                    state=new_game(level)
                    history.clear()
                    pause=False
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__=='__main__':
    main()
