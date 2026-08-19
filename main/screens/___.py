"""
Utilidad suelta: volcar todo el código en un solo archivo de texto.

NO forma parte de la aplicación. Nadie la importa y ejecutarla no
afecta a la app: recorre una carpeta, junta el contenido de todos los
archivos .py y los escribe seguidos en `todos_los_codigos.txt`, con una
cabecera antes de cada archivo. Sirve para pegar el proyecto entero en
un chat, un correo o un documento.

Uso:
    cd main
    python screens/___.py

Dos avisos:
    - La ruta `carpeta_proyecto` es RELATIVA a donde se ejecuta el
      comando, no a donde está este archivo. Si se lanza desde otra
      carpeta, no encontrará nada y generará un archivo vacío.
    - Este script vive dentro del paquete `screens/`, que es donde van
      las pantallas de la app. Su sitio natural sería una carpeta de
      herramientas aparte (`tools/`), para que nadie lo confunda con una
      pantalla.
"""

import os

# Carpeta que se va a recorrer, relativa al directorio actual
carpeta_proyecto = "screens"  # Cambia esto a la ruta de tu proyecto si es necesario

# Archivo donde se escribe todo junto (se sobrescribe en cada uso)
archivo_salida = "todos_los_codigos.txt"

# Solo se copian los archivos con estas extensiones
extensiones = [".py"]

with open(archivo_salida, "w", encoding="utf-8") as salida:

    for root, dirs, files in os.walk(carpeta_proyecto):

        # Saltarse el entorno virtual: son miles de archivos ajenos
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