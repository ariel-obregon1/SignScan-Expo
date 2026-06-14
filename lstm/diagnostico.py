import numpy as np
from keras.models import load_model

model = load_model("modelo_lstm_v2.keras")
labels = np.load("clases.npy", allow_pickle=True)
X_mean = np.load("X_mean.npy")
X_std = np.load("X_std.npy")

print("=== DIAGNOSTICO DEL MODELO ===")
print("Clases:", list(labels))
print("Numero de clases:", len(labels))
print("Output shape:", model.output_shape)
ultima = model.layers[-1]
print("Ultima capa:", ultima.name, "| units:", ultima.units,
      "| activation:", ultima.activation.__name__)
print()

print("=== PRUEBA: 3 entradas COMPLETAMENTE distintas ===")

e1 = np.zeros((1, 45, 504), dtype=np.float32)
e1n = (e1 - X_mean) / (X_std + 1e-7)
p1 = model.predict(e1n, verbose=0)[0]
print("CEROS     ->", p1, "-> clase:", labels[np.argmax(p1)])

np.random.seed(1)
e2 = np.random.randn(1, 45, 504).astype(np.float32)
e2n = (e2 - X_mean) / (X_std + 1e-7)
p2 = model.predict(e2n, verbose=0)[0]
print("RUIDO     ->", p2, "-> clase:", labels[np.argmax(p2)])

np.random.seed(999)
e3 = np.random.randn(1, 45, 504).astype(np.float32) * 10
e3n = (e3 - X_mean) / (X_std + 1e-7)
p3 = model.predict(e3n, verbose=0)[0]
print("RUIDO x10 ->", p3, "-> clase:", labels[np.argmax(p3)])

print()
print("CONCLUSION: softmax de 1 sola neurona = SIEMPRE 1.0")
print("exp(x)/exp(x) = 1.0 para cualquier x. Imposible predecir otra cosa.")

# Historial de entrenamiento
print()
print("=== HISTORIAL DE ENTRENAMIENTO ===")
import os
for f in ["accuracy.npy", "val_accuracy.npy", "loss.npy", "val_loss.npy"]:
    if os.path.exists(f):
        arr = np.load(f)
        print(f"{f}: {len(arr)} epochs | ultimo valor: {arr[-1]:.4f}")
