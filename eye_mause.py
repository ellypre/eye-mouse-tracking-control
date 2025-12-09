import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import sys

pyautogui.FAILSAFE = False

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

# MediaPipe göz index setleri
LEFT_EYE_IDX = sorted(list({idx for pair in mp_face_mesh.FACEMESH_LEFT_EYE for idx in pair}))
RIGHT_EYE_IDX = sorted(list({idx for pair in mp_face_mesh.FACEMESH_RIGHT_EYE for idx in pair}))

def eye_openness(landmarks, idx_list, img_w, img_h):
    """Gözün yükseklik/genişlik oranını döndürür. Küçükse göz kapalıdır."""
    xs, ys = [], []
    for idx in idx_list:
        lm = landmarks[idx]
        xs.append(lm.x * img_w)
        ys.append(lm.y * img_h)
    if not xs:
        return 0.0
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max_x - min_x
    h = max_y - min_y
    if w <= 0:
        return 0.0
    return h / w

# Göz kapalı frame sayaçları
left_closed_frames = 0
right_closed_frames = 0

# Eşikler
EYE_CLOSED_RATIO = 0.24      # bundan küçükse göz kapalı say
MIN_FRAMES_CLICK = 2         # bu kadar frame kapalıysa "kısa tık"
LONG_PRESS_FRAMES = 8        # drag için

# Drag durumu
left_dragging = False

# Mouse hareketi smoothing
smooth_x, smooth_y = screen_w / 2, screen_h / 2
SMOOTH = 0.25
MOVE_DEADZONE = 12

last_action = ""
last_action_time = 0

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 360)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]

            # ===== İMLEÇ HAREKETİ (BURUN) =====
            nose_lm = face.landmark[1]  # burun ucu
            nose_x = int(nose_lm.x * w)
            nose_y = int(nose_lm.y * h)

            # Kameradaki ortadaki %60'lık alanı tüm ekrana yay
            x_min = w * 0.2
            x_max = w * 0.8
            y_min = h * 0.2
            y_max = h * 0.8

            nose_x_clamped = max(x_min, min(nose_x, x_max))
            nose_y_clamped = max(y_min, min(nose_y, y_max))

            target_x = np.interp(nose_x_clamped, [x_min, x_max], [0, screen_w])
            target_y = np.interp(nose_y_clamped, [y_min, y_max], [0, screen_h])

            dx = target_x - smooth_x
            dy = target_y - smooth_y

            if abs(dx) > MOVE_DEADZONE or abs(dy) > MOVE_DEADZONE:
                smooth_x = smooth_x + dx * SMOOTH
                smooth_y = smooth_y + dy * SMOOTH

            try:
                pyautogui.moveTo(smooth_x, smooth_y, duration=0)
            except:
                pass

            # ===== GÖZ AÇIKLIĞI =====
            left_ratio = eye_openness(face.landmark, LEFT_EYE_IDX, w, h)
            right_ratio = eye_openness(face.landmark, RIGHT_EYE_IDX, w, h)

            left_closed = left_ratio < EYE_CLOSED_RATIO
            right_closed = right_ratio < EYE_CLOSED_RATIO

            cv2.putText(frame, f"L:{left_ratio:.2f} R:{right_ratio:.2f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            # ===== Sayaç güncelleme =====
            if left_closed:
                left_closed_frames += 1
            else:
                # Sol göz açıldı
                if left_dragging:
                    pyautogui.mouseUp()
                    left_dragging = False
                    last_action = "DRAG END"
                    last_action_time = time.time()
                else:
                    if MIN_FRAMES_CLICK <= left_closed_frames < LONG_PRESS_FRAMES:
                        pyautogui.click()
                        last_action = "LEFT CLICK"
                        last_action_time = time.time()
                left_closed_frames = 0

            if right_closed:
                right_closed_frames += 1
            else:
                if MIN_FRAMES_CLICK <= right_closed_frames:
                    if not left_closed:
                        pyautogui.rightClick()
                        last_action = "RIGHT CLICK"
                        last_action_time = time.time()
                right_closed_frames = 0

            # ===== Uzun süre sol göz kapalıysa: DRAG START =====
            if left_closed and not right_closed:
                if (not left_dragging) and left_closed_frames >= LONG_PRESS_FRAMES:
                    pyautogui.mouseDown()
                    left_dragging = True
                    last_action = "DRAG START"
                    last_action_time = time.time()

            mp_draw.draw_landmarks(
                frame,
                face,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_draw.DrawingSpec(
                    color=(0, 255, 0),
                    thickness=1,
                    circle_radius=1
                )
            )

        if time.time() - last_action_time < 1 and last_action:
            cv2.putText(frame, last_action, (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("Eye Mouse", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()
