# sign_engine.py

class SignEngine:
    def __init__(self):
        self.activo = True
        self.ultima_sena = ""
        self.confianza = 0.0

    def detectar_sena(self, frame=None):
        return {
            "sena": self.ultima_sena or "Sin detección",
            "confianza": self.confianza,
        }

    def establecer_resultado_prueba(self, sena="Hola", confianza=95):
        self.ultima_sena = sena
        self.confianza = confianza

    def limpiar(self):
        self.ultima_sena = ""
        self.confianza = 0.0