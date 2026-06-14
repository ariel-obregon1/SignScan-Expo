"""
Generador de DATOS SINTETICOS para probar el pipeline multi-clase.

IMPORTANTE: estos datos son ARTIFICIALES. Sirven solo para demostrar que el
entrenamiento y la inferencia con varias clases funcionan correctamente.
NO sirven para reconocer senas reales — para eso hay que capturar con
capturar_lstm.py usando manos reales.

Formato replicado exactamente del real:
  - secuencia: (45 frames, 504 features)
  - 504 = 252 (frame_actual) + 252 (deltas)
  - 252 = mano_izquierda(126) + mano_derecha(126)
  - 126 por mano = 21 landmarks x [abs_x,abs_y,abs_z, rel_x,rel_y,rel_z]
"""

import numpy as np
import os
import shutil

FRAMES = 45
N_LANDMARKS = 21
SAMPLES_POR_CLASE = 40

# Cada clase: (nombre, funcion_de_movimiento)
# El movimiento es una traslacion global de la mano a lo largo del tiempo.
# t va de 0 a 1 sobre los 45 frames.

def mov_adios(t):      # saludo horizontal (onda en X)
    return np.array([0.12 * np.sin(2 * np.pi * 2 * t), 0.0, 0.0])

def mov_que_tal(t):    # sube y baja (parabola en Y)
    return np.array([0.0, -0.15 * np.sin(np.pi * t), 0.0])

def mov_bien(t):       # pulgar arriba: sube
    return np.array([0.0, -0.18 * t, 0.02 * t])

def mov_mal(t):        # pulgar abajo: baja
    return np.array([0.0, 0.18 * t, -0.02 * t])

def mov_idle(t):       # quieto
    return np.array([0.0, 0.0, 0.0])

CLASES = [
    ("adios",   mov_adios),
    ("que_tal", mov_que_tal),
    ("bien",    mov_bien),
    ("mal",     mov_mal),
    ("idle",    mov_idle),
]

# Esqueleto base de una mano (21 landmarks alrededor de la muneca en 0)
rng_base = np.random.default_rng(7)
ESQUELETO = rng_base.uniform(-0.15, 0.15, size=(N_LANDMARKS, 3))
ESQUELETO[0] = [0.0, 0.0, 0.0]  # muneca en el origen relativo

# Offset de pose distinto por clase (para que la configuracion difiera)
POSE_OFFSET = {
    nombre: rng_base.uniform(-0.05, 0.05, size=(N_LANDMARKS, 3))
    for nombre, _ in CLASES
}

CENTRO = np.array([0.5, 0.5, 0.0])  # posicion de la muneca en la imagen


def generar_muestra(nombre, movimiento, seed):
    rng = np.random.default_rng(seed)
    pose = POSE_OFFSET[nombre]

    frames_actual = []  # cada uno 252

    for f in range(FRAMES):
        t = f / (FRAMES - 1)
        traslacion = movimiento(t)
        ruido = rng.normal(0, 0.006, size=(N_LANDMARKS, 3))

        # Posiciones absolutas de la mano derecha
        abs_pos = CENTRO + ESQUELETO + pose + traslacion + ruido
        muneca_abs = abs_pos[0]

        # Construir mano derecha: 21 x [abs, rel] = 126
        mano_der = []
        for l in range(N_LANDMARKS):
            ax, ay, az = abs_pos[l]
            rx = abs_pos[l, 0] - muneca_abs[0]
            ry = abs_pos[l, 1] - muneca_abs[1]
            rz = abs_pos[l, 2] - muneca_abs[2]
            mano_der.extend([ax, ay, az, rx, ry, rz])

        mano_izq = [0.0] * 126  # sena de una mano
        frames_actual.append(np.array(mano_izq + mano_der, dtype=np.float32))

    frames_actual = np.array(frames_actual)  # (45, 252)

    # Deltas igual que capturar_lstm.py: delta[0]=0, delta[t]=actual[t]-actual[t-1]
    deltas = np.zeros_like(frames_actual)
    deltas[1:] = frames_actual[1:] - frames_actual[:-1]

    secuencia = np.concatenate([frames_actual, deltas], axis=1)  # (45, 504)
    return secuencia.astype(np.float32)


def main():
    dataset_path = "dataset_lstm"

    # Limpiar dataset previo
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
    os.makedirs(dataset_path)

    total = 0
    for nombre, movimiento in CLASES:
        carpeta = os.path.join(dataset_path, nombre)
        os.makedirs(carpeta, exist_ok=True)
        for i in range(SAMPLES_POR_CLASE):
            seed = hash((nombre, i)) % (2**32)
            sec = generar_muestra(nombre, movimiento, seed)
            np.save(os.path.join(carpeta, f"{i}.npy"), sec)
            total += 1
        print(f"  {nombre}: {SAMPLES_POR_CLASE} muestras  shape={sec.shape}")

    print(f"\nTotal: {total} muestras en {len(CLASES)} clases")
    print("Clases:", [c[0] for c in CLASES])
    print("\nLISTO. Ahora corre: python train_lstm.py")


if __name__ == "__main__":
    main()
