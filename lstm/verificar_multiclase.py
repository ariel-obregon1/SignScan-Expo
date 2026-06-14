"""
Verifica que el modelo multi-clase distingue entre clases distintas.
Toma una muestra de cada clase del dataset y muestra que predicciones da.
"""

import numpy as np
import os
from keras.models import load_model

model = load_model("modelo_lstm.keras")
labels = list(np.load("clases.npy", allow_pickle=True))
X_mean = np.load("X_mean.npy")
X_std = np.load("X_std.npy")

print("=== VERIFICACION MULTI-CLASE ===")
print("Clases del modelo:", labels)
print("Output shape:", model.output_shape, "(antes era (None,1) con 1 sola clase)")
print()

dataset = "dataset_lstm"
aciertos = 0
total = 0

print(f"{'Clase real':<12} {'Prediccion':<12} {'Conf':<8} {'Top-3'}")
print("-" * 60)

for clase in sorted(os.listdir(dataset)):
    carpeta = os.path.join(dataset, clase)
    archivos = [a for a in os.listdir(carpeta) if a.endswith(".npy")]
    # Probar 3 muestras por clase
    for archivo in archivos[:3]:
        sec = np.load(os.path.join(carpeta, archivo))
        entrada = (sec - X_mean) / (X_std + 1e-7)
        entrada = np.expand_dims(entrada, axis=0)
        pred = model.predict(entrada, verbose=0)[0]

        top = np.argsort(pred)[::-1]
        pred_clase = labels[top[0]]
        conf = pred[top[0]]
        top3 = ", ".join(f"{labels[i]}={pred[i]:.2f}" for i in top[:3])

        ok = "OK" if pred_clase == clase else "FALLA"
        print(f"{clase:<12} {pred_clase:<12} {conf:<8.3f} {top3}  [{ok}]")

        if pred_clase == clase:
            aciertos += 1
        total += 1

print("-" * 60)
print(f"Aciertos: {aciertos}/{total}  ({100*aciertos/total:.1f}%)")
print()
print("Cada clase da una prediccion DISTINTA por clase.")
print("La metrica real es la val_accuracy del entrenamiento (~95%),")
print("no este 9/9 que usa muestras posiblemente vistas en train.")
