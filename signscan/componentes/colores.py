# componentes/colores.py

AZUL = "#062B7A"
AZUL_OSCURO = "#001F5C"
AZUL_MEDIO = "#0B3E91"
AZUL_CLARO = "#244A99"

TURQUESA = "#46D7CF"
TURQUESA_OSCURO = "#17C7BA"

AMARILLO = AZUL
NARANJA = "#FFB000"
MORADO = "#8B4CF6"
ROJO = "#EF4444"
VERDE = "#22C55E"

FONDO_CLARO = "#F5F7FA"
FONDO_OSCURO = "#0F172A"

BLANCO = "#FFFFFF"
NEGRO = "#1F2122"
GRIS = "#EEF1F5"
GRIS_BORDE = "#E5EAF1"
TEXTO_GRIS = "#64748B"
TEXTO_SUAVE = "#94A3B8"

SOMBRA = "#00000018"


def obtener_colores(tema="Claro", color_acento=TURQUESA):
    es_oscuro = tema == "Oscuro"

    return {
        "fondo": FONDO_OSCURO if es_oscuro else FONDO_CLARO,
        "tarjeta": "#1E293B" if es_oscuro else BLANCO,
        "texto": BLANCO if es_oscuro else AZUL,
        "texto_secundario": "#CBD5E1" if es_oscuro else TEXTO_GRIS,
        "acento": color_acento or TURQUESA,
        "sidebar": AZUL,
    }