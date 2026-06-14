import cv2
import mediapipe as mp
import pickle
import numpy as np
from collections import deque, Counter
import time
import os


class SignEngine:

    def __init__(self, camera_index=0):

        # Modelo — ruta absoluta para funcionar desde cualquier directorio
        _base = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(_base, "modelo_estaticas.pkl"), "rb") as f:
            self.model = pickle.load(f)

        # MediaPipe
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.mp_draw = mp.solutions.drawing_utils

        # Cámara
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            print("ERROR: No se pudo abrir la cámara")

        # Texto generado
        self.texto = ""

        # Control letras
        self.ultima_letra = ""
        self.ultimo_tiempo = 0
        self.cooldown = 3

        # Espacios automáticos
        self.ultimo_tiempo_mano = time.time()
        self.cooldown_espacio = 2

        # Estabilización
        self.historial = deque(maxlen=15)

        self.running = False

    def start(self):

        if self.running:
            return

        self.running = True

        print("Motor iniciado")

        # Crear ventana UNA sola vez
        cv2.namedWindow(
            "Reconocimiento 2 Manos",
            cv2.WINDOW_NORMAL
        )

        cv2.resizeWindow(
            "Reconocimiento 2 Manos",
            1280,
            720
        )

        while self.running:

            ret, frame = self.cap.read()

            if not ret:
                print("No se pudo leer la cámara")
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            result = self.hands.process(rgb)

            pred_estable = ""

            # =====================================
            # DETECCIÓN DE MANOS
            # =====================================

            if result.multi_hand_landmarks and result.multi_handedness:

                self.ultimo_tiempo_mano = time.time()

                # Dibujar manos
                for hand_landmarks in result.multi_hand_landmarks:

                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

                mano_izquierda = [0.0] * 63
                mano_derecha = [0.0] * 63

                for idx, hand_landmarks in enumerate(
                    result.multi_hand_landmarks
                ):

                    handedness = (
                        result.multi_handedness[idx]
                        .classification[0]
                        .label
                    )

                    base_x = hand_landmarks.landmark[0].x
                    base_y = hand_landmarks.landmark[0].y
                    base_z = hand_landmarks.landmark[0].z

                    datos_mano = []

                    for lm in hand_landmarks.landmark:

                        x_rel = lm.x - base_x

                        if handedness == "Left":
                            x_rel = -x_rel

                        datos_mano.extend([
                            x_rel,
                            lm.y - base_y,
                            lm.z - base_z
                        ])

                    if handedness == "Left":
                        mano_izquierda = datos_mano
                    else:
                        mano_derecha = datos_mano

                fila = np.array(
                    mano_izquierda + mano_derecha
                ).reshape(1, -1)

                pred = self.model.predict(fila)[0]

                self.historial.append(pred)

                if len(self.historial) == self.historial.maxlen:

                    conteo = Counter(self.historial)

                    letra, cantidad = (
                        conteo.most_common(1)[0]
                    )

                    if cantidad >= 12:
                        pred_estable = letra

            else:

                self.historial.clear()

                tiempo_sin_mano = (
                    time.time()
                    - self.ultimo_tiempo_mano
                )

                if tiempo_sin_mano > self.cooldown_espacio:

                    if (
                        self.texto != ""
                        and not self.texto.endswith(" ")
                    ):
                        self.texto += " "
                        self.ultima_letra = ""  # FIX: permitir misma letra tras pausa

            # =====================================
            # CONSTRUIR TEXTO
            # =====================================

            if pred_estable != "":

                tiempo_actual = time.time()

                if pred_estable != self.ultima_letra:

                    self.texto += pred_estable

                    self.ultima_letra = pred_estable

                    self.ultimo_tiempo = tiempo_actual

                elif (
                    tiempo_actual
                    - self.ultimo_tiempo
                    > self.cooldown
                ):

                    self.texto += pred_estable

                    self.ultimo_tiempo = tiempo_actual

            # =====================================
            # MOSTRAR INFO
            # =====================================

            cv2.putText(
                frame,
                f"Letra: {pred_estable}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Texto: {self.texto}",
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Reconocimiento 2 Manos",
                frame
            )

            if cv2.waitKey(1) & 0xFF == 27:
                self.running = False

        self.cap.release()
        cv2.destroyAllWindows()

    def stop(self):

        self.running = False

    def get_text(self):

        return self.texto