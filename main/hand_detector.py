"""
Detección de manos con MediaPipe Tasks API — hand_detector.py

Envoltorio sobre el Hand Landmarker de MediaPipe (mediapipe >= 0.10.14).
Sustituye al API clásico mp.solutions.hands, que fue eliminado en las
versiones modernas de la librería.

Qué hace este módulo, en orden de uso:

    detector = crear_detector("hand_landmarker.task")   # una vez
    result   = detectar(detector, frame_rgb, ts_ms)     # por cada frame
    if tiene_manos(result):
        dibujar_manos(frame_bgr, result)                # dibujo opcional
        vector = extraer_coords_dinamicas(result)       # datos al modelo

Los 21 puntos (landmarks) que devuelve MediaPipe por mano vienen en
coordenadas normalizadas de 0 a 1 respecto al ancho y alto de la imagen,
más una z relativa a la profundidad de la muñeca. Este módulo los
convierte en vectores planos de números, que es lo que espera la red
neuronal.

Importante sobre el orden: las dos funciones de extracción devuelven
SIEMPRE un vector del mismo tamaño, con la mano izquierda primero y la
derecha después, rellenando con ceros la mano que no aparezca. Así el
modelo recibe siempre la misma estructura, haya una mano o dos.
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import os

# Pares de landmarks que hay que unir con una línea para que la mano
# dibujada se parezca a una mano: cada tupla es (punto_origen, punto_fin)
# siguiendo el esqueleto estándar de MediaPipe (muñeca -> cada dedo).
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
    """Crea y devuelve un HandLandmarker de MediaPipe en modo VIDEO.

    El modo VIDEO (en vez de IMAGE) hace que MediaPipe recuerde dónde
    estaba la mano en el frame anterior, así que va más rápido y da un
    seguimiento más estable en una secuencia de webcam.

    Args:
        model_path: ruta al archivo .task del modelo. NO está en el
            repositorio: hay que descargarlo una vez (ver README).
        max_hands: número máximo de manos a detectar a la vez.
        det_conf: confianza mínima para dar por detectada una mano
            nueva. Subirlo reduce falsos positivos.
        track_conf: confianza mínima para seguir una mano ya detectada.

    Returns:
        Instancia de HandLandmarker lista para usar con detectar().

    Raises:
        FileNotFoundError: si no existe el archivo del modelo. El
            mensaje incluye el comando exacto para descargarlo.
    """
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
    """Procesa un frame y devuelve el resultado de MediaPipe.

    Args:
        detector: el HandLandmarker que devolvió crear_detector().
        rgb_frame: imagen en RGB (OpenCV trabaja en BGR, así que hay que
            convertirla antes con cv2.cvtColor).
        timestamp_ms: milisegundos transcurridos desde que empezó el
            vídeo. Tiene que ser ESTRICTAMENTE creciente entre llamadas
            o MediaPipe lanza un error; el bucle del traductor se
            encarga de garantizarlo.

    Returns:
        Objeto resultado de MediaPipe, con .hand_landmarks (los puntos)
        y .handedness (si cada mano es izquierda o derecha).
    """
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    return detector.detect_for_video(mp_image, timestamp_ms)


def dibujar_manos(frame, result):
    """Dibuja el esqueleto de las manos encima del frame.

    Modifica el frame recibido (no devuelve uno nuevo). Pinta primero
    las líneas verdes que unen los puntos y luego un círculo blanco con
    borde verde en cada uno de los 21 landmarks.

    Args:
        frame: imagen BGR de OpenCV sobre la que se dibuja.
        result: lo que devolvió detectar().
    """
    h, w = frame.shape[:2]
    for hand_lms in result.hand_landmarks:
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lms]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (0, 200, 0), 2)
        for pt in pts:
            cv2.circle(frame, pt, 4, (255, 255, 255), -1)
            cv2.circle(frame, pt, 4, (0, 150, 0), 1)


def tiene_manos(result):
    """Indica si en ese frame se detectó al menos una mano.

    Args:
        result: lo que devolvió detectar().

    Returns:
        True si hay al menos una mano. El traductor lo usa para saber
        cuándo hay gesto y cuándo el usuario bajó las manos (lo que
        acaba metiendo un espacio en el texto).
    """
    return bool(result.hand_landmarks)


def extraer_coords_estaticas(result):
    """Extrae el vector de características para señas ESTÁTICAS.

    Para una seña que no se mueve (una letra, por ejemplo) solo importa
    la forma de la mano, no dónde está en la imagen. Por eso se restan
    las coordenadas de la muñeca (landmark 0) a todos los puntos: la
    misma seña hecha arriba o abajo de la pantalla da el mismo vector.

    Además, a la mano izquierda se le invierte el eje X para que una
    seña hecha con la izquierda se parezca numéricamente a la misma seña
    hecha con la derecha.

    Args:
        result: lo que devolvió detectar().

    Returns:
        Lista plana de 126 números: [izquierda_63, derecha_63], donde
        cada bloque son 21 puntos por 3 coordenadas relativas (x, y, z).
        La mano que no aparezca en el frame va rellena de ceros.
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
    """Extrae el vector de características para señas DINÁMICAS.

    Es el que usa de verdad el traductor (modelo LSTM). A diferencia de
    la versión estática, aquí se guardan DOS cosas por cada punto:
        - las coordenadas absolutas (x, y, z), que dicen por dónde se
          mueve la mano en la imagen: en una seña con movimiento, la
          trayectoria es parte del significado;
        - las coordenadas relativas a la muñeca, que describen la forma
          de la mano independientemente de dónde esté.

    Igual que en la versión estática, a la mano izquierda se le invierte
    el eje X para unificar ambas manos.

    Args:
        result: lo que devolvió detectar().

    Returns:
        Lista plana de 252 números: [izquierda_126, derecha_126], donde
        cada bloque son 21 puntos por 6 valores (3 absolutos + 3
        relativos). La mano ausente va rellena de ceros.

    Este vector es la mitad de lo que recibe el modelo: el bucle del
    traductor le concatena la diferencia con el frame anterior (delta),
    llegando a los 504 valores por frame que espera la red.
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
