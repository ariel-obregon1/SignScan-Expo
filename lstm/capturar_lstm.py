import cv2
import numpy as np
import os
import time

from hand_detector import (
    crear_detector,
    detectar,
    dibujar_manos,
    tiene_manos,
    extraer_coords_dinamicas,
)

# ============================================
# CONFIG
# ============================================

label = input("Nombre de la dinámica: ")
total_muestras = int(input("Cantidad de muestras: "))

frames_por_muestra = 45
ruta = f"dataset_lstm/{label}"
os.makedirs(ruta, exist_ok=True)

# ============================================
# DETECTOR Y CÁMARA
# ============================================

detector = crear_detector("hand_landmarker.task")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

muestra_actual = 0

# ============================================
# LOOP PRINCIPAL
# ============================================

while muestra_actual < total_muestras:

    secuencia = []
    ultimo_frame = None
    print(f"\nPreparando muestra {muestra_actual + 1}")
    print("Presiona ESPACIO para grabar")

    # ---- Pantalla de espera con detección en vivo ----
    while True:

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ts = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        result = detectar(detector, rgb, ts)

        # FIX: mostrar detección en pantalla de espera
        if tiene_manos(result):
            dibujar_manos(frame, result)
            estado_color = (0, 255, 0)
            estado_txt = "Manos detectadas"
        else:
            estado_color = (0, 0, 255)
            estado_txt = "Sin deteccion"

        cv2.putText(frame, f"Muestra: {muestra_actual + 1}/{total_muestras}",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "ESPACIO = grabar",
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, estado_txt,
                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, estado_color, 2)

        cv2.imshow("Capture LSTM", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:
            break
        if key == 27:
            cap.release()
            detector.close()
            cv2.destroyAllWindows()
            exit()

    # ---- Captura de 45 frames ----
    frames_validos = 0

    for frame_num in range(frames_por_muestra):

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ts = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        result = detectar(detector, rgb, ts)

        if tiene_manos(result):
            frames_validos += 1
            dibujar_manos(frame, result)

        frame_actual = extraer_coords_dinamicas(result)

        # Deltas / velocidad
        if ultimo_frame is None:
            delta = [0.0] * len(frame_actual)
        else:
            delta = np.array(frame_actual) - np.array(ultimo_frame)

        ultimo_frame = frame_actual.copy()

        frame_final = np.concatenate([frame_actual, delta])
        secuencia.append(frame_final)

        cv2.putText(frame, f"Grabando {frame_num + 1}/{frames_por_muestra}",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Frames validos: {frames_validos}",
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Capture LSTM", frame)
        cv2.waitKey(1)

    # ---- Validar muestra ----
    if frames_validos < 35:
        print(f"Muestra descartada ({frames_validos}/{frames_por_muestra} frames validos)")
        continue

    secuencia = np.array(secuencia)
    print("Shape:", secuencia.shape)
    np.save(f"{ruta}/{muestra_actual}.npy", secuencia)
    print(f"Muestra {muestra_actual + 1} guardada ({frames_validos}/{frames_por_muestra} frames validos)")
    muestra_actual += 1

cap.release()
detector.close()
cv2.destroyAllWindows()
