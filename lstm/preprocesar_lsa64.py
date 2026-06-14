"""
Convierte videos de LSA64 al formato del pipeline SignScan LSTM.

LSA64 raw: archivos NNN_SSS_RRR.mp4
  NNN = id de sena (001-064)
  SSS = id de sujeto (001-010)
  RRR = repeticion (001-005)

Cada video -> secuencia (45, 504) guardada en dataset_lstm/<sena>/<i>.npy
  504 = frame_actual(252) + deltas(252), igual que capturar_lstm.py

Uso:
  python preprocesar_lsa64.py
Configura abajo SENAS_A_PROCESAR y MAX_VIDEOS_POR_SENA.
"""

import cv2
import numpy as np
import os
import glob
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from hand_detector import extraer_coords_dinamicas

# ============================================
# CONFIG
# ============================================

# Carpeta donde se descomprimio LSA64 (busca .mp4 recursivamente)
LSA64_DIR = "lsa64_download"

# IDs de senas a procesar (subconjunto para el demo).
# Etiquetadas por id para no asignar nombres incorrectos;
# renombra las carpetas con los nombres oficiales si querés.
SENAS_A_PROCESAR = {
    "03": "sena_03",
    "05": "sena_05",
    "23": "sena_23",
    "51": "sena_51",
    "56": "sena_56",
}

MAX_VIDEOS_POR_SENA = 50   # 10 sujetos x 5 reps = 50 max
FRAMES_OBJETIVO = 45
MODEL_TASK = "hand_landmarker.task"
SALIDA = "dataset_lstm"


def crear_detector_imagen():
    base = mp_python.BaseOptions(model_asset_path=MODEL_TASK)
    opts = mp_vision.HandLandmarkerOptions(
        base_options=base,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        running_mode=mp_vision.RunningMode.IMAGE,
    )
    return mp_vision.HandLandmarker.create_from_options(opts)


def muestrear_indices(total, n):
    """n indices equiespaciados en [0, total)."""
    if total <= n:
        return list(range(total)) + [total - 1] * (n - total)
    return np.linspace(0, total - 1, n).astype(int).tolist()


def procesar_video(detector, ruta):
    cap = cv2.VideoCapture(ruta)
    frames = []
    while True:
        ret, f = cap.read()
        if not ret:
            break
        frames.append(f)
    cap.release()

    if len(frames) == 0:
        return None

    indices = muestrear_indices(len(frames), FRAMES_OBJETIVO)

    actuales = []
    validos = 0
    for idx in indices:
        frame = cv2.flip(frames[idx], 1)  # espejo, igual que en captura
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_img)
        if result.hand_landmarks:
            validos += 1
        actuales.append(np.array(extraer_coords_dinamicas(result), dtype=np.float32))

    if validos < FRAMES_OBJETIVO * 0.5:   # al menos 50% con manos
        return None, validos

    actuales = np.array(actuales)              # (45, 252)
    deltas = np.zeros_like(actuales)
    deltas[1:] = actuales[1:] - actuales[:-1]
    secuencia = np.concatenate([actuales, deltas], axis=1)  # (45, 504)
    return secuencia.astype(np.float32), validos


def main():
    videos = glob.glob(os.path.join(LSA64_DIR, "**", "*.mp4"), recursive=True)
    print(f"Videos .mp4 encontrados: {len(videos)}")
    if not videos:
        print("No se encontraron videos. Verifica que LSA64 este descomprimido en", LSA64_DIR)
        return

    detector = crear_detector_imagen()

    # Agrupar por id de sena
    contador = {k: 0 for k in SENAS_A_PROCESAR}
    os.makedirs(SALIDA, exist_ok=True)

    for ruta in sorted(videos):
        base = os.path.basename(ruta)
        partes = base.split("_")
        if len(partes) < 3:
            continue
        sena_id = partes[0].zfill(3)[-3:]   # "003"
        sena_key = sena_id.lstrip("0").zfill(2)  # "03"

        if sena_key not in SENAS_A_PROCESAR:
            continue
        if contador[sena_key] >= MAX_VIDEOS_POR_SENA:
            continue

        nombre = SENAS_A_PROCESAR[sena_key]
        carpeta = os.path.join(SALIDA, nombre)
        os.makedirs(carpeta, exist_ok=True)

        res = procesar_video(detector, ruta)
        if res is None or res[0] is None:
            validos = res[1] if isinstance(res, tuple) else 0
            print(f"  [SKIP] {base} (pocas manos: {validos})")
            continue

        sec, validos = res
        idx = contador[sena_key]
        np.save(os.path.join(carpeta, f"{idx}.npy"), sec)
        contador[sena_key] += 1
        print(f"  [OK] {base} -> {nombre}/{idx}.npy  (manos: {validos}/45)")

    detector.close()

    print("\n=== RESUMEN ===")
    total = 0
    for k, nombre in SENAS_A_PROCESAR.items():
        print(f"  {nombre}: {contador[k]} muestras")
        total += contador[k]
    print(f"Total: {total} muestras")
    print("\nAhora corre: python train_lstm.py")


if __name__ == "__main__":
    main()
