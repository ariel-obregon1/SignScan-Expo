import cv2
import numpy as np
from collections import deque, Counter
from keras.models import load_model
import time

from hand_detector import (
    crear_detector,
    detectar,
    dibujar_manos,
    tiene_manos,
    extraer_coords_dinamicas,
)

# ============================================
# MODELO
# ============================================

model = load_model("modelo_lstm.keras")

labels = np.load("clases.npy", allow_pickle=True)
X_mean = np.load("X_mean.npy")
X_std = np.load("X_std.npy")

# ============================================
# DETECTOR DE MANOS (Tasks API)
# ============================================

detector = crear_detector("hand_landmarker.task")

# ============================================
# CAMARA
# ============================================

cap = cv2.VideoCapture(0)

# ============================================
# VENTANA — pantalla completa con 'f' para toggle
# ============================================

WINDOW = "SignScan LSTM"
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW, 1280, 720)

fullscreen = False

# ============================================
# BUFFER Y CONTROL
# ============================================

frames_modelo = 45
secuencia = deque(maxlen=frames_modelo)

# Registra cuántos frames del buffer tuvieron manos reales
# Solo se predice cuando hay suficientes frames con manos
frames_con_manos = deque(maxlen=frames_modelo)
MIN_FRAMES_CON_MANOS = 20  # de 45, al menos 20 deben tener manos

historial = deque(maxlen=10)

pred_estable = ""
texto = ""
ultima_palabra = ""
ultimo_tiempo = 0
cooldown = 2
confianza = 0.0

# Auto-espacio al perder detección
ultimo_tiempo_mano = time.time()
cooldown_espacio = 2

# Predicción cada N frames para reducir carga del BiLSTM
frame_count = 0
predict_cada = 5

ultimo_frame = None

# ============================================
# LOOP PRINCIPAL
# ============================================

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    result = detectar(detector, rgb, timestamp_ms)

    hay_manos = tiene_manos(result)

    if hay_manos:
        ultimo_tiempo_mano = time.time()
        dibujar_manos(frame, result)
        frames_con_manos.append(1)
    else:
        frames_con_manos.append(0)
        # Resetear display al perder detección
        pred_estable = ""
        confianza = 0.0
        # Limpiar historial al perder manos para evitar predicciones fantasma
        historial.clear()

        # Auto-espacio
        tiempo_sin_mano = time.time() - ultimo_tiempo_mano
        if tiempo_sin_mano > cooldown_espacio:
            if texto != "" and not texto.endswith(" "):
                texto += " "
                ultima_palabra = ""

    # ============================================
    # EXTRACCIÓN DE FEATURES + DELTAS
    # ============================================

    frame_actual = extraer_coords_dinamicas(result)

    if ultimo_frame is None:
        delta = [0.0] * len(frame_actual)
    else:
        delta = np.array(frame_actual) - np.array(ultimo_frame)

    ultimo_frame = frame_actual.copy()

    frame_final = np.concatenate([frame_actual, delta])
    secuencia.append(frame_final)

    # ============================================
    # PREDICCION — solo cuando hay manos suficientes en el buffer
    # ============================================

    frame_count += 1
    manos_en_buffer = sum(frames_con_manos)

    # Resetear confianza si no hay suficientes manos para predecir
    if manos_en_buffer < MIN_FRAMES_CON_MANOS:
        confianza = 0.0

    if (len(secuencia) >= frames_modelo
            and manos_en_buffer >= MIN_FRAMES_CON_MANOS
            and frame_count % predict_cada == 0):

        entrada = np.array(secuencia)
        entrada = (entrada - X_mean) / (X_std + 1e-7)
        entrada = np.expand_dims(entrada, axis=0)

        predicciones = model.predict(entrada, verbose=0)[0]

        top_indices = np.argsort(predicciones)[::-1]
        top1 = top_indices[0]
        top2 = top_indices[1] if len(top_indices) > 1 else top1

        confianza = float(predicciones[top1])
        diferencia = predicciones[top1] - predicciones[top2]
        pred = labels[top1]

        # Con 1 sola clase la diferencia siempre es 0 — no exigirla
        diferencia_ok = (diferencia > 0.15) if len(labels) > 1 else True

        if confianza > 0.70 and diferencia_ok:
            historial.append(pred)
        else:
            # Sentinel desplaza predicciones viejas (no pop que quitaba buenas)
            historial.append("__none__")

        # Estabilizar
        if len(historial) == historial.maxlen:
            conteo = Counter(historial)
            palabra, cantidad = conteo.most_common(1)[0]

            if cantidad >= 7 and palabra != "__none__":
                pred_estable = palabra
                tiempo_actual = time.time()

                if (pred_estable != ultima_palabra
                        or tiempo_actual - ultimo_tiempo > cooldown):
                    if pred_estable != "idle":
                        texto += pred_estable + " "
                    ultima_palabra = pred_estable
                    ultimo_tiempo = tiempo_actual

        # Top 3 predicciones en pantalla
        y_pos = 300
        for i in range(min(3, len(labels))):
            idx = top_indices[i]
            cv2.putText(frame, f"{labels[idx]}: {predicciones[idx]:.2f}",
                        (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2)
            y_pos += 40

    # ============================================
    # UI
    # ============================================

    cv2.putText(frame, f"Dinamica: {pred_estable}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.putText(frame, f"Confianza: {confianza:.2f}",
                (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

    # Texto largo: cortarlo si no cabe en pantalla
    texto_display = texto[-60:] if len(texto) > 60 else texto
    cv2.putText(frame, f"Texto: {texto_display}",
                (10, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Indicador de manos en buffer
    pct = int((manos_en_buffer / frames_modelo) * 100)
    color_barra = (0, 255, 0) if manos_en_buffer >= MIN_FRAMES_CON_MANOS else (0, 165, 255)
    cv2.putText(frame, f"Buffer manos: {pct}%",
                (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_barra, 2)

    cv2.imshow(WINDOW, frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 27:       # ESC — salir
        break
    elif key == ord("f"):   # F — toggle fullscreen
        fullscreen = not fullscreen
        if fullscreen:
            cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    elif key == 8:      # Backspace
        texto = texto[:-1]
    elif key == ord("c"):   # C — limpiar texto
        texto = ""

cap.release()
detector.close()
cv2.destroyAllWindows()
