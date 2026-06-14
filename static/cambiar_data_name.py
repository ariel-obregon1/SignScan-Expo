import pandas as pd

# Archivo CSV
archivo = "datos_2manos.csv"

# Leer dataset
df = pd.read_csv(archivo, header=None)

# Mostrar señas existentes
senas = df[0].unique()

print("\nSeñas encontradas:")
for s in senas:
    print("-", s)

# Pedir datos
vieja = input("\nSeña que quieres cambiar: ")
nueva = input("Nuevo nombre: ")

# Contar muestras
cantidad = (df[0] == vieja).sum()

# Verificar existencia
if cantidad == 0:

    print("\nEsa seña no existe.")

else:

    # Reemplazar nombre
    df[0] = df[0].replace(vieja, nueva)

    # Guardar cambios
    df.to_csv(archivo, header=False, index=False)

    print(f"\n{cantidad} muestras cambiadas.")
    print(f"{vieja} → {nueva}")