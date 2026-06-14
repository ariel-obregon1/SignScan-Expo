"""Deja en dataset_lstm solo las clases reales con suficientes muestras."""
import os
import shutil

DATASET = "dataset_lstm"

# Carpetas a eliminar: sinteticas + reales con muy pocas muestras
A_ELIMINAR = ["adios", "bien", "idle", "mal", "que_tal", "sena_51", "sena_56"]

for nombre in A_ELIMINAR:
    ruta = os.path.join(DATASET, nombre)
    if os.path.isdir(ruta):
        shutil.rmtree(ruta)
        print(f"Eliminada: {nombre}")

print("\nClases restantes:")
for d in sorted(os.listdir(DATASET)):
    ruta = os.path.join(DATASET, d)
    if os.path.isdir(ruta):
        n = len([f for f in os.listdir(ruta) if f.endswith(".npy")])
        print(f"  {d}: {n} muestras")
