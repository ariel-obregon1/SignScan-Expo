"""
Wrapper de detección de manos con MediaPipe Tasks API (mediapipe >= 0.10.14).
Reemplaza el API clásico mp.solutions.hands que fue eliminado en versiones modernas.
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import os

# Conexiones estándar de la mano para dibujar
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),(0,17),
]


def crear_detector(model_path="hand_landmarker.task", max_hands=2,
                   det_conf=0.7, track_conf=0.7):
    """Crea y devuelve un HandLandmarker en modo VIDEO (frame a frame)."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No se encontró el modelo: {model_path}\n"
            "Descárgalo con:\n"
            "  python -c \"import urllib.request; urllib.request.urlretrieve("
            "'https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
            "hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')\""
        )

    base_options = mp_python.BaseOptions(model_asset_path=model_path)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=max_hands,
        min_hand_detection_confidence=det_conf,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=track_conf,
        running_mode=mp_vision.RunningMode.VIDEO,
    )
    return mp_vision.HandLandmarker.create_from_options(options)


def detectar(detector, rgb_frame, timestamp_ms):
    """Procesa un frame RGB y devuelve el resultado del Tasks API."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    return detector.detect_for_video(mp_image, timestamp_ms)


def dibujar_manos(frame, result):
    """Dibuja landmarks y conexiones sobre el frame BGR."""
    h, w = frame.shape[:2]
    for hand_lms in result.hand_landmarks:
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lms]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (0, 200, 0), 2)
        for pt in pts:
            cv2.circle(frame, pt, 4, (255, 255, 255), -1)
            cv2.circle(frame, pt, 4, (0, 150, 0), 1)


def tiene_manos(result):
    """True si se detectó al menos una mano."""
    return bool(result.hand_landmarks)


def extraer_coords_estaticas(result):
    """
    Extrae vector de 126 dimensiones (relativo al muñeca) para señas estáticas.
    Retorna lista plana: [izq_63, der_63]
    """
    mano_izq = [0.0] * 63
    mano_der = [0.0] * 63

    for i, hand_lms in enumerate(result.hand_landmarks):
        handedness = result.handedness[i][0].category_name  # "Left" o "Right"

        base_x = hand_lms[0].x
        base_y = hand_lms[0].y
        base_z = hand_lms[0].z

        datos = []
        for lm in hand_lms:
            x_rel = lm.x - base_x
            if handedness == "Left":
                x_rel = -x_rel
            datos.extend([x_rel, lm.y - base_y, lm.z - base_z])

        if handedness == "Left":
            mano_izq = datos
        else:
            mano_der = datos

    return mano_izq + mano_der


def extraer_coords_dinamicas(result):
    """
    Extrae vector de 252 dimensiones (abs + rel por muñeca) para señas dinámicas.
    Retorna lista plana: [izq_126, der_126]
    """
    mano_izq = [0.0] * 126
    mano_der = [0.0] * 126

    for i, hand_lms in enumerate(result.hand_landmarks):
        handedness = result.handedness[i][0].category_name

        base_x = hand_lms[0].x
        base_y = hand_lms[0].y
        base_z = hand_lms[0].z

        datos = []
        for lm in hand_lms:
            # Absolutos
            datos.extend([lm.x, lm.y, lm.z])
            # Relativos al muñeca
            x_rel = lm.x - base_x
            if handedness == "Left":
                x_rel = -x_rel
            datos.extend([x_rel, lm.y - base_y, lm.z - base_z])

        if handedness == "Left":
            mano_izq = datos
        else:
            mano_der = datos

    return mano_izq + mano_der
