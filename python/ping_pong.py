import subprocess
import sys
import os
import urllib.request

def install_deps():
    print("Checking dependencies...")
    try:
        import cv2
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "opencv-python"])
    try:
        import mediapipe
    except ImportError:
        print("Installing mediapipe...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "mediapipe"])
    try:
        import numpy
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "numpy"])

install_deps()

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import random
import time

# ── Model download ──────────────────────────────────────────────────────────
MODEL_PATH = 'hand_landmarker.task'
if not os.path.exists(MODEL_PATH):
    print("Downloading hand_landmarker.task from Google…")
    urllib.request.urlretrieve(
        'https://storage.googleapis.com/mediapipe-models/hand_landmarker/'
        'hand_landmarker/float16/1/hand_landmarker.task',
        MODEL_PATH)
    print("Download complete.")

# ── MediaPipe setup ──────────────────────────────────────────────────────────
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.5)
detector = vision.HandLandmarker.create_from_options(options)

# ── Finger-tip indices in MediaPipe 21-landmark model ───────────────────────
TIP_IDS   = [4, 8, 12, 16, 20]   # thumb … pinky tips
PIP_IDS   = [3, 6, 10, 14, 18]   # knuckles (to check if finger is up)
WRIST_ID  = 0
MID_MCP   = 9                     # middle-finger MCP (for palm centre)

# ── Colour palette ───────────────────────────────────────────────────────────
BLUE   = (255, 120,  30)
PURPLE = (255,  60, 180)
WHITE  = (255, 255, 255)
CYAN   = (255, 220,   0)
ORANGE = (  0, 140, 255)

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def dist2d(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

# ── Physics string class ─────────────────────────────────────────────────────
class SpringString:
    def __init__(self, p1, p2):
        self.p1 = list(p1)
        self.p2 = list(p2)
        # mid-point oscillator
        mx = (p1[0]+p2[0])//2
        my = (p1[1]+p2[1])//2
        self.mid  = [float(mx), float(my)]
        self.vmid = [0.0, 0.0]

    def update(self, p1, p2, dt=1.0):
        self.p1 = list(p1)
        self.p2 = list(p2)
        target_mx = (p1[0]+p2[0])/2
        target_my = (p1[1]+p2[1])/2
        k  = 0.18   # spring
        dmp= 0.72   # damping
        self.vmid[0] += (target_mx - self.mid[0]) * k
        self.vmid[1] += (target_my - self.mid[1]) * k
        # add slight perpendicular wobble
        dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
        L  = math.hypot(dx,dy)+1e-5
        px = -dy/L; py = dx/L
        self.vmid[0] += px * random.uniform(-1.5, 1.5)
        self.vmid[1] += py * random.uniform(-1.5, 1.5)
        self.vmid[0] *= dmp
        self.vmid[1] *= dmp
        self.mid[0]  += self.vmid[0]
        self.mid[1]  += self.vmid[1]

    def draw(self, glow, sharp, stretch_norm):
        col = lerp_color(BLUE, WHITE, stretch_norm)
        thick_g = max(1, int(4 * stretch_norm + 2))
        # Quadratic bezier via mid point
        pts = []
        for t in [i/20 for i in range(21)]:
            bx = (1-t)**2*self.p1[0] + 2*(1-t)*t*self.mid[0] + t**2*self.p2[0]
            by = (1-t)**2*self.p1[1] + 2*(1-t)*t*self.mid[1] + t**2*self.p2[1]
            pts.append((int(bx), int(by)))
        for i in range(len(pts)-1):
            cv2.line(glow,  pts[i], pts[i+1], col, thick_g+2, cv2.LINE_AA)
            cv2.line(sharp, pts[i], pts[i+1], WHITE, 1, cv2.LINE_AA)

# ── Shockwave / explosion ring class ─────────────────────────────────────────
class Ring:
    def __init__(self, cx, cy, color=WHITE):
        self.cx = cx; self.cy = cy
        self.r  = 10
        self.life = 1.0
        self.color = color

    def update(self):
        self.r    += 18
        self.life -= 0.04

    def draw(self, glow, sharp):
        if self.life <= 0: return
        alpha = self.life
        col   = tuple(int(c*alpha) for c in self.color)
        thick = max(1, int(alpha*6))
        cv2.circle(glow,  (self.cx, self.cy), int(self.r), col, thick+4)
        cv2.circle(sharp, (self.cx, self.cy), int(self.r), WHITE, 1, cv2.LINE_AA)

# ── Orbital particle for portal ───────────────────────────────────────────────
class OrbitalParticle:
    def __init__(self, cx, cy, orbit_r):
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = random.uniform(0.04, 0.10)
        self.orbit_r = orbit_r + random.uniform(-15,15)
        self.cx = cx; self.cy = cy
        self.life = random.uniform(0.6,1.0)

    def update(self, cx, cy, orbit_r):
        self.cx = cx; self.cy = cy
        self.orbit_r = orbit_r
        self.angle  += self.speed

    def pos(self):
        x = self.cx + math.cos(self.angle)*self.orbit_r
        y = self.cy + math.sin(self.angle)*self.orbit_r
        return int(x), int(y)

    def draw(self, glow, sharp):
        p = self.pos()
        cv2.circle(glow,  p, 8,  CYAN,  -1)
        cv2.circle(sharp, p, 3,  WHITE, -1)

# ── Star dust trail ───────────────────────────────────────────────────────────
class StarDust:
    def __init__(self, x, y):
        self.x  = float(x)
        self.y  = float(y)
        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-2,2)
        self.life = 1.0
        self.size = random.randint(2,6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.03

    def draw(self, glow, sharp):
        if self.life <= 0: return
        col = lerp_color(PURPLE, BLUE, 1-self.life)
        cv2.circle(glow,  (int(self.x), int(self.y)), self.size*2, col, -1)
        cv2.circle(sharp, (int(self.x), int(self.y)), self.size,   WHITE, -1)

# ── Lightning helper ──────────────────────────────────────────────────────────
def draw_lightning(canvas, p1, p2, color, segs=12, jitter=25, thick=3):
    pts = [p1]
    for i in range(1, segs):
        t  = i/segs
        mx = int(p1[0]+(p2[0]-p1[0])*t + random.randint(-jitter,jitter))
        my = int(p1[1]+(p2[1]-p1[1])*t + random.randint(-jitter,jitter))
        pts.append((mx,my))
    pts.append(p2)
    for i in range(len(pts)-1):
        cv2.line(canvas, pts[i], pts[i+1], color, thick, cv2.LINE_AA)

# ── Landmark helpers ──────────────────────────────────────────────────────────
def lm_px(lm, w, h):
    return int(lm.x*w), int(lm.y*h)

def finger_up(lms, idx):
    tip = lms[TIP_IDS[idx]]
    pip = lms[PIP_IDS[idx]]
    return tip.y < pip.y          # tip higher on screen = finger up

def all_fingers_up(lms):
    return all(finger_up(lms, i) for i in range(5))

def is_fist(lms):
    return not any(finger_up(lms, i) for i in range(1,5))

def hand_angle(lms):
    wrist  = lms[WRIST_ID]
    middle = lms[MID_MCP]
    return math.atan2(middle.y - wrist.y, middle.x - wrist.x)

def palm_center_px(lms, w, h):
    cx = int(sum(lms[i].x for i in [0,5,9,13,17]) / 5 * w)
    cy = int(sum(lms[i].y for i in [0,5,9,13,17]) / 5 * h)
    return cx, cy

def palm_size(lms, w, h):
    wrist  = lm_px(lms[0],  w, h)
    middle = lm_px(lms[MID_MCP], w, h)
    return dist2d(wrist, middle)

def spread_amount(lms):
    tips = [lms[t] for t in TIP_IDS]
    dists = []
    for i in range(len(tips)):
        for j in range(i+1, len(tips)):
            dists.append(math.hypot(tips[i].x-tips[j].x, tips[i].y-tips[j].y))
    return sum(dists)/len(dists)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam"); return

    ret, frame = cap.read()
    if not ret: return
    H, W = frame.shape[:2]

    # State
    springs      = {}          # key: (i,j) tip index pair
    rings        = []
    orbitals     = []
    star_dust    = []
    prev_fist    = [False, False]
    flash_alpha  = 0.0
    portal_angle = 0.0
    galaxy_angle = 0.0
    prev_hand_angle = [None, None]
    edge_glow    = 0.0
    frame_count  = 0

    print("\n🪄  MAGIC HANDS — Controls:")
    print("   Fingers spread     → web strings between fingertips")
    print("   Open palm wide     → spinning portal in palm")
    print("   Rotate hand        → spiral galaxy follows")
    print("   Two palms facing   → energy beam + screen glow")
    print("   Make a fist        → EXPLOSION shockwave")
    print("   Press Q to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame      = cv2.flip(frame, 1)
        frame_rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img     = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        results    = detector.detect(mp_img)

        # Dark base
        dark = (frame * 0.35).astype(np.uint8)
        glow  = np.zeros_like(frame)
        sharp = np.zeros_like(frame)

        # Draw grid
        for gy in range(0, H, 50):
            cv2.line(dark, (0,gy), (W,gy), (0,25,0), 1)
        for gx in range(0, W, 50):
            cv2.line(dark, (gx,0), (gx,H), (0,25,0), 1)

        portal_angle += 0.04
        frame_count  += 1

        hands_data = []   # list of (landmarks, tip_pixels, pcx, pcy, psize)

        if results.hand_landmarks:
            for hi, lms in enumerate(results.hand_landmarks):
                tips_px = [lm_px(lms[t], W, H) for t in TIP_IDS]
                pcx, pcy = palm_center_px(lms, W, H)
                psize    = palm_size(lms, W, H)
                hands_data.append((lms, tips_px, pcx, pcy, psize))

                # ── 1. STRING WEB ───────────────────────────────────────────
                for i in range(5):
                    for j in range(i+1, 5):
                        key = (hi*10+i, hi*10+j)
                        if key not in springs:
                            springs[key] = SpringString(tips_px[i], tips_px[j])
                        sp = springs[key]
                        sp.update(tips_px[i], tips_px[j])
                        natural = psize * 0.8
                        stretch = dist2d(tips_px[i], tips_px[j])
                        norm    = min(1.0, max(0.0, (stretch-natural)/(natural+1e-5)))
                        sp.draw(glow, sharp, norm)

                # ── 2. OPEN PALM → PORTAL ───────────────────────────────────
                if all_fingers_up(lms):
                    spread = spread_amount(lms)
                    portal_r = int(min(psize * 1.8, 180) * min(1.0, spread/0.25))

                    # Rotating rings
                    for ring_idx in range(4):
                        r_off  = portal_r - ring_idx*18
                        if r_off < 10: continue
                        angle  = portal_angle * (1 + ring_idx*0.3)
                        col    = lerp_color(BLUE, PURPLE, ring_idx/4)
                        # Draw arc as rotated ellipse
                        axes   = (r_off, max(5, r_off//3))
                        cv2.ellipse(glow,  (pcx,pcy), axes, math.degrees(angle), 0, 360, col, 5)
                        cv2.ellipse(sharp, (pcx,pcy), axes, math.degrees(angle), 0, 360, WHITE, 1)

                    # Mandala spokes
                    for spoke in range(12):
                        a  = portal_angle + spoke * (2*math.pi/12)
                        x2 = int(pcx + math.cos(a)*portal_r)
                        y2 = int(pcy + math.sin(a)*portal_r)
                        cv2.line(glow,  (pcx,pcy), (x2,y2), PURPLE, 3)
                        cv2.line(sharp, (pcx,pcy), (x2,y2), WHITE,  1)

                    # Orbital particles
                    while len(orbitals) < 12:
                        orbitals.append(OrbitalParticle(pcx, pcy, portal_r*0.7))
                    for orb in orbitals:
                        orb.update(pcx, pcy, portal_r*0.7)
                        orb.draw(glow, sharp)
                else:
                    orbitals.clear()

                # ── 3. ROTATING HAND → GALAXY ──────────────────────────────
                ha = hand_angle(lms)
                if prev_hand_angle[hi] is not None:
                    delta = ha - prev_hand_angle[hi]
                    # wrap
                    if delta >  math.pi: delta -= 2*math.pi
                    if delta < -math.pi: delta += 2*math.pi
                    galaxy_angle += delta * 2.0

                    if abs(delta) > 0.015:   # hand is rotating
                        # Spawn star dust at each tip
                        for tp in tips_px:
                            star_dust.append(StarDust(tp[0], tp[1]))

                        # Draw spiral galaxy centred on palm
                        for arm in range(3):
                            arm_off = arm * (2*math.pi/3)
                            prev_pt = None
                            for s in range(60):
                                t2   = s / 60
                                r2   = t2 * psize * 2.2
                                ang2 = galaxy_angle + arm_off + t2 * 4 * math.pi
                                gx2  = int(pcx + math.cos(ang2)*r2)
                                gy2  = int(pcy + math.sin(ang2)*r2)
                                col  = lerp_color(BLUE, PURPLE, t2)
                                cv2.circle(glow,  (gx2,gy2), 4, col,   -1)
                                cv2.circle(sharp, (gx2,gy2), 1, WHITE, -1)
                                if prev_pt:
                                    cv2.line(glow, prev_pt, (gx2,gy2), col, 2)
                                prev_pt = (gx2, gy2)

                prev_hand_angle[hi] = ha

                # ── 5. FIST → EXPLOSION ─────────────────────────────────────
                fist_now = is_fist(lms)
                if fist_now and not prev_fist[hi]:
                    flash_alpha = 1.0
                    for _ in range(8):
                        rings.append(Ring(pcx, pcy, WHITE))
                    # Scatter existing star dust outward
                    for sd in star_dust:
                        sd.vx *= 4; sd.vy *= 4
                prev_fist[hi] = fist_now

                # Draw fingertip dots
                for tp in tips_px:
                    cv2.circle(glow,  tp, 12, CYAN,  -1)
                    cv2.circle(sharp, tp, 4,  WHITE, -1)

            # ── 4. TWO HANDS → ENERGY BEAM ─────────────────────────────────
            if len(hands_data) == 2:
                (_, _, pc1x, pc1y, ps1) = hands_data[0]
                (_, _, pc2x, pc2y, ps2) = hands_data[1]
                beam_dist = dist2d((pc1x,pc1y), (pc2x,pc2y))
                if beam_dist < W * 0.55:
                    edge_glow = min(1.0, edge_glow + 0.08)
                    # Core thick beam
                    cv2.line(glow, (pc1x,pc1y), (pc2x,pc2y), CYAN,   20)
                    cv2.line(glow, (pc1x,pc1y), (pc2x,pc2y), WHITE,  8)
                    cv2.line(sharp,(pc1x,pc1y), (pc2x,pc2y), WHITE,  2, cv2.LINE_AA)
                    # Lightning crackles along beam
                    for _ in range(3):
                        draw_lightning(glow, (pc1x,pc1y), (pc2x,pc2y), PURPLE, segs=10, jitter=20, thick=2)
                    # Shockwave rings along beam
                    if frame_count % 6 == 0:
                        t3 = random.random()
                        rx = int(pc1x + (pc2x-pc1x)*t3)
                        ry = int(pc1y + (pc2y-pc1y)*t3)
                        rings.append(Ring(rx, ry, CYAN))
                else:
                    edge_glow = max(0.0, edge_glow - 0.05)
            else:
                edge_glow = max(0.0, edge_glow - 0.05)

        # ── Update & draw star dust ─────────────────────────────────────────
        live_dust = []
        for sd in star_dust:
            sd.update()
            if sd.life > 0:
                sd.draw(glow, sharp)
                live_dust.append(sd)
        star_dust = live_dust

        # ── Update & draw rings ─────────────────────────────────────────────
        live_rings = []
        for rr in rings:
            rr.update()
            if rr.life > 0:
                rr.draw(glow, sharp)
                live_rings.append(rr)
        rings = live_rings

        # ── Compose ─────────────────────────────────────────────────────────
        if np.any(glow):
            glow = cv2.GaussianBlur(glow, (45, 45), 0)

        final = cv2.add(dark, glow)
        final = cv2.add(final, sharp)

        # Edge glow for beam effect
        if edge_glow > 0.01:
            border = int(edge_glow * 60)
            overlay = final.copy()
            cv2.rectangle(overlay, (0,0), (W,H), CYAN, border*2)
            final = cv2.addWeighted(final, 1.0, overlay, edge_glow*0.6, 0)

        # Flash
        if flash_alpha > 0:
            white = np.full_like(final, 255)
            final = cv2.addWeighted(final, 1-flash_alpha, white, flash_alpha, 0)
            flash_alpha = max(0.0, flash_alpha - 0.08)

        # HUD
        cv2.putText(final, "MAGIC HANDS", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100,255,100), 2, cv2.LINE_AA)
        hints = ["SPREAD FINGERS=WEB", "OPEN PALM=PORTAL",
                 "ROTATE=GALAXY", "2 HANDS=BEAM", "FIST=BOOM"]
        for hi2, hint in enumerate(hints):
            cv2.putText(final, hint, (10, H-120+hi2*22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0,180,0), 1, cv2.LINE_AA)

        cv2.imshow("🪄 Magic Hands", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()