import pandas as pd
import numpy as np

# Archivo — nombre consistente con capturar_estaticas.py
archivo = "datos_estaticas.csv"

# Leer dataset
df = pd.read_csv(archivo, header=None)

print(f"\nMuestras originales: {len(df)}")

# Cantidad correcta:
# 1 etiqueta + 126 coordenadas
columnas_correctas = 127

# Guardar filas buenas
filas_validas = []

# Contador
eliminadas = 0

for i in range(len(df)):

    fila = df.iloc[i]

    try:

        # Verificar columnas
        if len(fila) != columnas_correctas:

            eliminadas += 1
            continue

        # Obtener coordenadas
        coords = fila[1:].astype(float)

        # Contar ceros
        ceros = np.sum(coords == 0)

        # Si demasiados ceros → basura
        if ceros > 100:

            eliminadas += 1
            continue

        # Si pasa todo
        filas_validas.append(fila)

    except:

        eliminadas += 1

# Crear dataframe limpio
df_limpio = pd.DataFrame(filas_validas)

# Guardar
df_limpio.to_csv(
    "datos_estaticas_limpio.csv",
    header=False,
    index=False
)

print(f"\nMuestras eliminadas: {eliminadas}")
print(f"Muestras finales: {len(df_limpio)}")

print("\nDataset limpio guardado.")