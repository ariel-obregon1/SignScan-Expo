import os

# Carpeta principal del proyecto
carpeta_proyecto = "."

# Archivo de salida
archivo_salida = "todos_los_codigos.txt"

# Extensiones permitidas
extensiones = [".py"]

with open(archivo_salida, "w", encoding="utf-8") as salida:

    for root, dirs, files in os.walk(carpeta_proyecto):

        # Ignorar entorno virtual
        if "venv" in root:
            continue

        for file in files:

            if any(file.endswith(ext) for ext in extensiones):

                ruta_completa = os.path.join(root, file)

                salida.write("\n")
                salida.write("=" * 80 + "\n")
                salida.write(f"ARCHIVO: {ruta_completa}\n")
                salida.write("=" * 80 + "\n\n")

                try:

                    with open(ruta_completa, "r", encoding="utf-8") as f:

                        contenido = f.read()

                        salida.write(contenido)

                except Exception as e:

                    salida.write(f"\nERROR LEYENDO ARCHIVO: {e}\n")

                salida.write("\n\n")

print(f"\nCodigos exportados en: {archivo_salida}")