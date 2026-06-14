import cv2
import mediapipe as mp
import csv
import time

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

# Etiqueta
label = input("Seña que vas a capturar: ")

# Tiempo entre muestras
ultimo_guardado = 0
intervalo = 0.2

# Contador
contador = 0

with open("datos_estaticas.csv", mode="a", newline="") as f:

    writer = csv.writer(f)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Espejo
        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(rgb)

        # Dibujar manos
        if result.multi_hand_landmarks:

            for hand_landmarks in result.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        # Guardar datos
        if result.multi_hand_landmarks and result.multi_handedness:

            tiempo_actual = time.time()

            if tiempo_actual - ultimo_guardado > intervalo:

                # Mano izquierda y derecha
                mano_izquierda = [0.0] * 63
                mano_derecha = [0.0] * 63

                # Recorrer manos detectadas
                for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):

                    handedness = result.multi_handedness[idx].classification[0].label

                    base_x = hand_landmarks.landmark[0].x
                    base_y = hand_landmarks.landmark[0].y
                    base_z = hand_landmarks.landmark[0].z

                    datos_mano = []

                    for lm in hand_landmarks.landmark:

                        x_rel = lm.x - base_x

                        # Corregir mano izquierda
                        if handedness == "Left":
                            x_rel = -x_rel

                        datos_mano.extend([
                            x_rel,
                            lm.y - base_y,
                            lm.z - base_z
                        ])

                    # Guardar en lado correcto
                    if handedness == "Left":
                        mano_izquierda = datos_mano
                    else:
                        mano_derecha = datos_mano

                # Crear fila final
                fila = [label] + mano_izquierda + mano_derecha

                # Guardar CSV
                writer.writerow(fila)

                ultimo_guardado = tiempo_actual

                contador += 1

                print(f"Muestras: {contador}")

        # Mostrar contador
        cv2.putText(
            frame,
            f"Muestras: {contador}",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Captura 2 Manos", frame)

        # ESC para salir
        if cv2.waitKey(1) & 0xFF == 27:
            break

# Cerrar
cap.release()
cv2.destroyAllWindows()