import os
import numpy as np
import random

# ============================================
# CONFIG
# ============================================

DATASET = "dataset_lstm"

# Clases a aumentar
CLASES_A_AUMENTAR = [
    "Hola"
]

# Cuántas nuevas generar por cada muestra real
AUGMENTACIONES_POR_MUESTRA = 4

# ============================================
# FUNCIONES
# ============================================

def agregar_ruido(secuencia, intensidad=0.005):
    ruido = np.random.normal(0, intensidad, secuencia.shape)
    return secuencia + ruido


def escalar(secuencia, factor):
    nueva = secuencia.copy()

    if nueva.shape[1] >= 504:
        nueva[:, :252] *= factor
        nueva[:, 252:] *= factor

    return nueva


def desplazar(secuencia, dx, dy):

    nueva = secuencia.copy()

    if nueva.shape[1] >= 252:

        coords = nueva[:, :252]

        for i in range(0, 252, 6):

            coords[:, i] += dx

            if i + 1 < 252:
                coords[:, i + 1] += dy

        nueva[:, :252] = coords

    return nueva


def variar_velocidad(secuencia):

    frames = secuencia.shape[0]

    factor = random.uniform(0.8, 1.2)

    idx_original = np.arange(frames)

    idx_nuevo = np.linspace(
        0,
        frames - 1,
        max(2, int(frames * factor))
    )

    nueva = np.zeros(
        (len(idx_nuevo), secuencia.shape[1]),
        dtype=np.float32
    )

    for f in range(secuencia.shape[1]):

        nueva[:, f] = np.interp(
            idx_nuevo,
            idx_original,
            secuencia[:, f]
        )

    idx_final = np.linspace(
        0,
        len(nueva) - 1,
        frames
    )

    final = np.zeros(
        (frames, secuencia.shape[1]),
        dtype=np.float32
    )

    for f in range(secuencia.shape[1]):

        final[:, f] = np.interp(
            idx_final,
            np.arange(len(nueva)),
            nueva[:, f]
        )

    return final


# ============================================
# INICIO
# ============================================

print("\n==============================")
print("AUMENTADOR DE DATASET LSTM")
print("==============================")

print("\nDirectorio actual:")
print(os.getcwd())

if not os.path.exists(DATASET):
    print(f"\n[ERROR] No existe la carpeta: {DATASET}")
    exit()

print("\nClases encontradas:")
print(os.listdir(DATASET))

total_nuevas = 0

# ============================================
# PROCESO
# ============================================

for clase in CLASES_A_AUMENTAR:

    print("\n----------------------------------")
    print("Clase:", clase)

    carpeta = os.path.join(DATASET, clase)

    print("Ruta:", carpeta)

    if not os.path.isdir(carpeta):
        print("[ERROR] La carpeta no existe")
        continue

    todos = [
        f for f in os.listdir(carpeta)
        if f.endswith(".npy")
    ]

    originales = [
        f for f in todos
        if not f.startswith("aug_")
    ]

    print("Total .npy:", len(todos))
    print("Originales:", len(originales))

    if len(originales) == 0:
        print("[ADVERTENCIA] No hay muestras originales")
        continue

    indice = len(todos)

    generadas = 0

    for archivo in originales:

        ruta = os.path.join(carpeta, archivo)

        try:
            secuencia = np.load(ruta)

        except Exception as e:

            print(f"[ERROR] No se pudo cargar {archivo}")
            print(e)
            continue

        for _ in range(AUGMENTACIONES_POR_MUESTRA):

            nueva = secuencia.copy()

            nueva = agregar_ruido(
                nueva,
                random.uniform(0.002, 0.008)
            )

            nueva = escalar(
                nueva,
                random.uniform(0.95, 1.05)
            )

            nueva = desplazar(
                nueva,
                random.uniform(-0.03, 0.03),
                random.uniform(-0.03, 0.03)
            )

            nueva = variar_velocidad(nueva)

            nombre = f"aug_{indice}.npy"

            salida = os.path.join(
                carpeta,
                nombre
            )

            np.save(salida, nueva)

            indice += 1
            generadas += 1
            total_nuevas += 1

    print("Generadas:", generadas)

# ============================================
# RESUMEN
# ============================================

print("\n==============================")
print("TOTAL NUEVAS:", total_nuevas)
print("==============================")