import cv2
import mediapipe as mp
import pickle
import numpy as np
from collections import deque, Counter
import time
from gtts import gTTS
from playsound import playsound
import os

# Texto generado
texto = ""

# Control letras
ultima_letra = ""
ultimo_tiempo = 0
cooldown = 3

# Espacios automáticos
ultimo_tiempo_mano = time.time()
cooldown_espacio = 2

# Cargar modelo
with open("modelo_estaticas.pkl", "rb") as f:
    model = pickle.load(f)

# MediaPipe
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# Cámara
cap = cv2.VideoCapture(0)

cv2.namedWindow(
    "Reconocimiento 2 Manos",
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    "Reconocimiento 2 Manos",
    cv2.WND_PROP_MAXIMIZED,
    cv2.WINDOW_MAXIMIZED
)

# Historial estabilidad
historial = deque(maxlen=15)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Espejo
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    pred_estable = ""

    # Detectar manos
    if result.multi_hand_landmarks and result.multi_handedness:

        ultimo_tiempo_mano = time.time()

        # Dibujar manos
        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

        # Mano izquierda y derecha
        mano_izquierda = [0.0] * 63
        mano_derecha = [0.0] * 63

        # Procesar manos
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):

            handedness = result.multi_handedness[idx].classification[0].label

            base_x = hand_landmarks.landmark[0].x
            base_y = hand_landmarks.landmark[0].y
            base_z = hand_landmarks.landmark[0].z

            datos_mano = []

            for lm in hand_landmarks.landmark:

                x_rel = lm.x - base_x

                # Corregir izquierda
                if handedness == "Left":
                    x_rel = -x_rel

                datos_mano.extend([
                    x_rel,
                    lm.y - base_y,
                    lm.z - base_z
                ])

            # Guardar lado correcto
            if handedness == "Left":
                mano_izquierda = datos_mano
            else:
                mano_derecha = datos_mano

        # Crear fila completa
        fila = mano_izquierda + mano_derecha

        fila = np.array(fila).reshape(1, -1)

        # Predicción
        pred = model.predict(fila)[0]

        # Historial
        historial.append(pred)

        # Estabilizar
        if len(historial) == historial.maxlen:

            conteo = Counter(historial)

            letra, cantidad = conteo.most_common(1)[0]

            # Exigir coincidencias
            if cantidad >= 12:

                pred_estable = letra

    else:

        # Limpiar historial
        historial.clear()

        # Tiempo sin mano
        tiempo_sin_mano = time.time() - ultimo_tiempo_mano

        # Espacio automático
        if tiempo_sin_mano > cooldown_espacio:

            if texto != "" and not texto.endswith(" "):

                texto += " "

                ultima_letra = ""

    # Construir texto
    if pred_estable != "":

        tiempo_actual = time.time()

        # Nueva letra
        if pred_estable != ultima_letra:

            texto += pred_estable

            ultima_letra = pred_estable

            ultimo_tiempo = tiempo_actual

        # Repetir luego de tiempo
        elif tiempo_actual - ultimo_tiempo > cooldown:

            texto += pred_estable

            ultimo_tiempo = tiempo_actual

    # Mostrar letra
    cv2.putText(
        frame,
        f"Letra: {pred_estable}",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 255, 0),
        3
    )

    # Mostrar texto
    cv2.putText(
        frame,
        f"Texto: {texto}",
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    # Mostrar ventana
    cv2.imshow("Reconocimiento 2 Manos", frame)

    # Teclas
    key = cv2.waitKey(1) & 0xFF

    # ESC
    if key == 27:
        break

    # Backspace
    elif key == 8:

        texto = texto[:-1]

    # Limpiar
    elif key == ord("c"):

        texto = ""

    # Voz
    elif key == ord("v"):

        if texto.strip() != "":

            try:

                archivo = "voz.mp3"

                texto_audio = " ".join(texto.split())

                tts = gTTS(
                    text=texto_audio,
                    lang="es"
                )

                tts.save(archivo)

                playsound(archivo)

                os.remove(archivo)

            except Exception as e:

                print("Error:", e)

# Cerrar
cap.release()
cv2.destroyAllWindows()