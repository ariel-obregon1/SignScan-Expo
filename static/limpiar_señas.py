import pandas as pd

# Cargar dataset
df = pd.read_csv("datos_2manos.csv", header=None)

# Mostrar etiquetas disponibles
etiquetas = df[0].unique()

print("Señas disponibles:")

for e in etiquetas:
    print("-", e)

# Elegir seña
eliminar = input(
    "\nEscribe la seña que quieres eliminar: "
)

if eliminar not in etiquetas:
    print("❌ Esa seña no existe")

else:
    # Filtrar
    df_nuevo = df[df[0] != eliminar]

    # Guardar cambios
    df_nuevo.to_csv(
        "datos_2manos.csv",
        index=False,
        header=False
    )

    print(f"✅ Se eliminaron todas las muestras de '{eliminar}'")