import pandas as pd

# Archivo
archivo = "datos_estaticas.csv"

# Leer dataset
df = pd.read_csv(archivo, header=None)

# Contar muestras
conteo = df[0].value_counts()

print("\n====== DATASET ======\n")

for sena, cantidad in conteo.items():

    print(f"{sena}: {cantidad} muestras")

print("\nTotal de señas:", len(conteo))
print("Total de muestras:", len(df))