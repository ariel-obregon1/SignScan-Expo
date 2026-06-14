import zipfile, io, h5py
import numpy as np
import keras
from keras.models import Sequential
from keras import Input
from keras.layers import Bidirectional, LSTM, Dropout, Dense

labels = np.load("clases.npy", allow_pickle=True)
num_clases = len(labels)

# ============================================
# Reconstruir arquitectura con Input() explícito
# ============================================

model = Sequential([
    Input(shape=(45, 504)),
    Bidirectional(LSTM(128, return_sequences=True)),
    Dropout(0.3),
    Bidirectional(LSTM(128)),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dense(num_clases, activation="softmax"),
])

model.build((None, 45, 504))
model.summary()

# ============================================
# Leer pesos del ZIP
# ============================================

with zipfile.ZipFile("modelo_lstm.keras", "r") as z:
    data = z.read("model.weights.h5")

with h5py.File(io.BytesIO(data), "r") as f:

    # Las keys raíz tienen backslash LITERAL; dentro de cada grupo, vars usa /
    def leer(root_key, var_idx):
        return np.array(f[root_key]["vars"][str(var_idx)])

    # BiLSTM 1 — forward
    fw1_k  = leer("layers\\bidirectional\\forward_layer\\cell", 0)
    fw1_rk = leer("layers\\bidirectional\\forward_layer\\cell", 1)
    fw1_b  = leer("layers\\bidirectional\\forward_layer\\cell", 2)

    # BiLSTM 1 — backward
    bw1_k  = leer("layers\\bidirectional\\backward_layer\\cell", 0)
    bw1_rk = leer("layers\\bidirectional\\backward_layer\\cell", 1)
    bw1_b  = leer("layers\\bidirectional\\backward_layer\\cell", 2)

    # BiLSTM 2 — forward
    fw2_k  = leer("layers\\bidirectional_1\\forward_layer\\cell", 0)
    fw2_rk = leer("layers\\bidirectional_1\\forward_layer\\cell", 1)
    fw2_b  = leer("layers\\bidirectional_1\\forward_layer\\cell", 2)

    # BiLSTM 2 — backward
    bw2_k  = leer("layers\\bidirectional_1\\backward_layer\\cell", 0)
    bw2_rk = leer("layers\\bidirectional_1\\backward_layer\\cell", 1)
    bw2_b  = leer("layers\\bidirectional_1\\backward_layer\\cell", 2)

    # Dense layers
    d1_w = leer("layers\\dense", 0)
    d1_b = leer("layers\\dense", 1)
    d2_w = leer("layers\\dense_1", 0)
    d2_b = leer("layers\\dense_1", 1)

# ============================================
# Asignar pesos capa por capa
# ============================================

# Keras 3 Bidirectional orden: [fw_kernel, fw_recurrent, fw_bias, bw_kernel, bw_recurrent, bw_bias]
model.layers[0].set_weights([fw1_k, fw1_rk, fw1_b, bw1_k, bw1_rk, bw1_b])
model.layers[2].set_weights([fw2_k, fw2_rk, fw2_b, bw2_k, bw2_rk, bw2_b])
model.layers[4].set_weights([d1_w, d1_b])
model.layers[5].set_weights([d2_w, d2_b])

print("\nPesos asignados correctamente")

# ============================================
# Guardar en formato compatible
# ============================================

model.save("modelo_lstm_v2.keras")

print("Guardado -> modelo_lstm_v2.keras")
print("Clases:", list(labels))
