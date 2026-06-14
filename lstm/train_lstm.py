import numpy as np
import os

from sklearn.model_selection import train_test_split

from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras import Input
from keras.layers import (
    LSTM,
    Dense,
    Dropout,
    Bidirectional
)
from keras.utils import to_categorical

# ============================================
# DATASET
# ============================================

dataset_path = "dataset_lstm"

X = []
y = []

labels = sorted(os.listdir(dataset_path))

# ============================================
# CARGAR DATOS
# ============================================

for idx, label in enumerate(labels):

    carpeta = os.path.join(dataset_path, label)

    for archivo in os.listdir(carpeta):

        if archivo.endswith(".npy"):

            ruta = os.path.join(carpeta, archivo)

            secuencia = np.load(ruta)

            X.append(secuencia)
            y.append(idx)

if len(X) == 0:
    print("ERROR: No hay secuencias en el dataset")
    exit(1)

if len(labels) < 2:
    print("ERROR: Se necesitan al menos 2 clases para entrenar")
    exit(1)

# Validar que todas las secuencias tengan el mismo shape
shapes = set(s.shape for s in X)
if len(shapes) > 1:
    print(f"ERROR: Shapes inconsistentes en las secuencias: {shapes}")
    print("Revisa que todos los .npy tengan (45, 504)")
    exit(1)

X = np.array(X, dtype=np.float32)
y = np.array(y)

print("Clases:", labels)
print("Muestras:", len(X))

# ============================================
# ONE HOT
# ============================================

y = to_categorical(y)

# ============================================
# SPLIT
# ============================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=np.argmax(y, axis=1)
)

# ============================================
# NORMALIZACION
# ============================================

X_mean = np.mean(X_train, axis=0)
X_std = np.std(X_train, axis=0)

X_train = (X_train - X_mean) / (X_std + 1e-7)
X_test = (X_test - X_mean) / (X_std + 1e-7)

print("X_train:", X_train.shape)
print("X_test :", X_test.shape)
print("y_train:", y_train.shape)
print("y_test :", y_test.shape)

# ============================================
# MODELO
# ============================================

model = Sequential([
    Input(shape=(X_train.shape[1], X_train.shape[2])),
    Bidirectional(LSTM(128, return_sequences=True)),
    Dropout(0.3),
    Bidirectional(LSTM(128)),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dense(len(labels), activation="softmax"),
])

# ============================================
# COMPILAR
# ============================================

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ============================================
# EARLY STOPPING
# ============================================

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)

# ============================================
# ENTRENAR
# ============================================

history = model.fit(
    X_train,
    y_train,
    epochs=100,
    batch_size=16,
    validation_data=(X_test, y_test),
    callbacks=[early_stop]
)

# ============================================
# EVALUAR
# ============================================

loss, acc = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print("\n==============================")
print(f"Accuracy final: {acc:.4f}")
print(f"Loss final: {loss:.4f}")
print("==============================")

# ============================================
# GUARDAR HISTORIAL
# ============================================

np.save("accuracy.npy", history.history["accuracy"])
np.save("val_accuracy.npy", history.history["val_accuracy"])

np.save("loss.npy", history.history["loss"])
np.save("val_loss.npy", history.history["val_loss"])

# ============================================
# GUARDAR MODELO
# ============================================

model.save("modelo_lstm.keras")

np.save("clases.npy", labels)

np.save("X_mean.npy", X_mean)
np.save("X_std.npy", X_std)

print("\nModelo guardado correctamente")