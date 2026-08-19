"""
Pantalla del traductor de señas — screens/translator.py

Ruta "/scan". Es la parte que de verdad traduce: enciende la webcam,
detecta las manos con MediaPipe, se lo pasa al modelo LSTM y va
escribiendo el texto reconocido.

Cómo está repartida la pantalla (esto es lo más raro del archivo y
conviene entenderlo antes de tocar nada):

    - El vídeo NO se dibuja dentro de Flet. Se muestra en una ventana
      aparte de OpenCV, que se coloca encima del hueco azul que se ve en
      la interfaz. compute_camera_screen_rect() calcula dónde cae ese
      hueco y la ventana de OpenCV se mueve ahí, dando la ilusión de que
      el vídeo está empotrado en la app.
    - El panel derecho de Flet sí es interfaz normal, y va reflejando en
      vivo la seña actual, la confianza y el texto acumulado.

Piezas del archivo, de arriba abajo:
    1. Constantes: colores, geometría de la caja de la cámara y
       parámetros del reconocimiento.
    2. compute_camera_screen_rect(): dónde colocar la ventana de OpenCV.
    3. _get_model(): carga el modelo una sola vez y lo cachea.
    4. SignLanguageTranslator: la clase que hace el trabajo, en un hilo
       aparte para no congelar la interfaz.
    5. screen_translator(): monta la pantalla de Flet y conecta los
       botones con la clase anterior.

Qué hace falta para que funcione de verdad:
    - webcam disponible,
    - modelo entrenado: modelo_lstm.keras, clases.npy, X_mean.npy y
      X_std.npy en la carpeta main/,
    - hand_landmarker.task de MediaPipe en la carpeta main/ (NO está en
      el repositorio, hay que descargarlo una vez; ver el README).
Si falta algo, la pantalla se abre igual y el error aparece en rojo bajo
el botón, sin tirar la app.
"""

import os
import platform
import sys
import threading
import time
from collections import Counter, deque

import cv2
import flet as ft
import numpy as np

# ------------------------------------------------------------------
# Hace que "from hand_detector import ..." funcione tanto si la app se
# lanza desde main/ como si se ejecuta este archivo desde screens/:
# mete la carpeta padre (main/) en la lista de rutas de importación.
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from hand_detector import (  # noqa: E402
    crear_detector,
    detectar,
    dibujar_manos,
    extraer_coords_dinamicas,
    tiene_manos,
)

MODEL_PATH = os.path.join(PROJECT_ROOT, "modelo_lstm.keras")
LABELS_PATH = os.path.join(PROJECT_ROOT, "clases.npy")
X_MEAN_PATH = os.path.join(PROJECT_ROOT, "X_mean.npy")
X_STD_PATH = os.path.join(PROJECT_ROOT, "X_std.npy")
HAND_LANDMARKER_PATH = os.path.join(PROJECT_ROOT, "hand_landmarker.task")


# ---- Paleta de colores ----
COLOR_BG_DARK = "#001030"
COLOR_CARD_BLUE = "#002060"
COLOR_TURQUOISE = "#40E0D0"
COLOR_GOLD = "#FFD700"
COLOR_RED = "#FF6B6B"
COLOR_WHITE_TEXT = ft.Colors.with_opacity(0.85, ft.Colors.WHITE)
COLOR_TIPS_BG = ft.Colors.with_opacity(0.6, COLOR_CARD_BLUE)
COLOR_TIPS_BORDER = ft.Colors.with_opacity(0.10, COLOR_TURQUOISE)
COLOR_CAM_ICON_BG = ft.Colors.with_opacity(0.10, COLOR_TURQUOISE)
COLOR_CAM_ICON_BORDER = ft.Colors.with_opacity(0.20, COLOR_TURQUOISE)
COLOR_BACK_BTN_BG = ft.Colors.with_opacity(0.10, ft.Colors.WHITE)

CONTENT_MAX_WIDTH = 1100
CAMERA_INDEX = 0
WINDOW_TITLE = "SignScan LSTM (Q: quit | R: re-sync)"

# ---- Geometría estimada de la caja de la cámara ----
#
# Estos números describen, en píxeles, el espacio que ocupa cada parte
# de la interfaz (cabecera, márgenes, botón...). Con ellos se deduce
# dónde queda el hueco azul del vídeo para poner encima la ventana de
# OpenCV. Son estimaciones: si se cambia el diseño de la pantalla (un
# título más alto, otro margen), hay que ajustarlos o el vídeo quedará
# descuadrado.
HEADER_HEIGHT = 117
MAIN_ROW_SIDE_PADDING = 40
MAIN_ROW_BOTTOM_PADDING = 40
COLUMN_SPACING = 25
LEFT_COLUMN_FRACTION = 7 / 12
ACTIVAR_BTN_HEIGHT = 82
ERROR_TEXT_RESERVED = 20
LEFT_COLUMN_INNER_SPACING = 16

# La app corre a pantalla completa (main.py), así que no hay barra de
# título ni borde de ventana que descontar. Si alguna vez deja de ir a
# pantalla completa, estos dos valores tendrán que dejar de ser 0.
TITLE_BAR_HEIGHT = 0
WINDOW_BORDER = 0

CALIBRATION_OFFSET_X = 0
CALIBRATION_OFFSET_Y = 0

REPOSITION_EVERY_N_FRAMES = 20


def compute_camera_screen_rect(page: ft.Page):
    """Calcula dónde colocar la ventana de vídeo de OpenCV.

    Parte de la posición y el tamaño de la ventana de la app y va
    restando lo que ocupan la cabecera, los márgenes, el botón de
    activar y el espacio reservado al mensaje de error, hasta quedarse
    con el rectángulo del hueco azul donde debería verse la cámara.

    Args:
        page: la página de Flet, de donde salen la posición y el tamaño
            de la ventana. En web esos valores pueden venir vacíos, por
            eso cada uno tiene un valor por defecto.

    Returns:
        Tupla (x, y, ancho, alto) en píxeles de pantalla, ya en enteros
        porque OpenCV no acepta decimales. El ancho y el alto tienen un
        mínimo (200x150) para que la ventana nunca quede inservible si
        la app está muy encogida.
    """
    win_left = page.window.left or 0
    win_top = page.window.top or 0
    win_width = page.window.width or CONTENT_MAX_WIDTH
    win_height = page.window.height or 820

    content_width = min(win_width, CONTENT_MAX_WIDTH)
    content_left = win_left + WINDOW_BORDER + max(0, (win_width - content_width) / 2)
    content_top = win_top + TITLE_BAR_HEIGHT

    row_area_width = content_width - (2 * MAIN_ROW_SIDE_PADDING)
    row_area_height = win_height - TITLE_BAR_HEIGHT - HEADER_HEIGHT - MAIN_ROW_BOTTOM_PADDING

    left_col_width = (row_area_width - COLUMN_SPACING) * LEFT_COLUMN_FRACTION

    camera_width = left_col_width
    camera_height = row_area_height - ACTIVAR_BTN_HEIGHT - ERROR_TEXT_RESERVED - LEFT_COLUMN_INNER_SPACING

    camera_left = content_left + MAIN_ROW_SIDE_PADDING + CALIBRATION_OFFSET_X
    camera_top = content_top + HEADER_HEIGHT + CALIBRATION_OFFSET_Y

    return (
        int(camera_left),
        int(camera_top),
        max(200, int(camera_width)),
        max(150, int(camera_height)),
    )


# ---- Parámetros del reconocimiento ----
# Ajustar estos números cambia el comportamiento del traductor:
#   FRAMES_MODELO      -> cuántos frames seguidos ve el modelo de una
#                         vez; tiene que coincidir con el valor usado al
#                         entrenar, no se puede cambiar a la ligera.
#   MIN_FRAMES_CON_MANOS -> cuántos de esos frames deben tener manos
#                         para intentar predecir; evita predecir con la
#                         pantalla medio vacía.
#   HISTORIAL_LEN      -> cuántas predicciones seguidas se guardan para
#                         decidir por mayoría (estabilización).
#   COOLDOWN           -> segundos mínimos antes de repetir la misma
#                         palabra en el texto.
#   COOLDOWN_ESPACIO   -> segundos sin manos tras los que se añade un
#                         espacio, o sea, se da la palabra por acabada.
#   PREDICT_CADA       -> predice 1 de cada N frames, para no saturar la
#                         CPU llamando al modelo en todos.
#   UMBRAL_CONFIANZA   -> confianza mínima para aceptar una predicción.
#   UMBRAL_DIFERENCIA  -> distancia mínima entre la primera y la segunda
#                         opción; si están muy igualadas se descarta.
FRAMES_MODELO = 45
MIN_FRAMES_CON_MANOS = 20
HISTORIAL_LEN = 5
COOLDOWN = 2
COOLDOWN_ESPACIO = 2
PREDICT_CADA = 5
UMBRAL_CONFIANZA = 0.70
UMBRAL_DIFERENCIA = 0.15


# Caché del modelo: cargarlo tarda varios segundos, así que se hace una
# sola vez por ejecución y se reutiliza en cada arranque de la cámara.
_model_cache = {"model": None, "labels": None, "X_mean": None, "X_std": None}


def _get_model():
    """Carga (la primera vez) y devuelve el modelo y sus datos.

    El import de Keras está dentro de la función a propósito: es muy
    lento y solo debe pagarse cuando el usuario activa de verdad la
    cámara, no al abrir la pantalla.

    Returns:
        El diccionario _model_cache con:
            "model"  -> la red LSTM entrenada.
            "labels" -> array con el nombre de cada clase (las señas que
                        el modelo sabe reconocer).
            "X_mean" / "X_std" -> media y desviación típica calculadas
                        durante el entrenamiento. Hay que aplicar la
                        misma normalización a los datos nuevos o el
                        modelo predice cualquier cosa.

    Raises:
        Cualquier error de carga (archivo que falta, modelo corrupto) se
        propaga hacia arriba; quien llama lo convierte en un mensaje
        para el usuario.
    """
    if _model_cache["model"] is None:
        from keras.models import load_model

        _model_cache["model"] = load_model(MODEL_PATH)
        _model_cache["labels"] = np.load(LABELS_PATH, allow_pickle=True)
        _model_cache["X_mean"] = np.load(X_MEAN_PATH)
        _model_cache["X_std"] = np.load(X_STD_PATH)
    return _model_cache


class SignLanguageTranslator:
    """Motor del traductor: cámara + detección de manos + modelo LSTM.

    Todo el trabajo pesado corre en un HILO APARTE, porque leer frames y
    predecir bloquearía la interfaz de Flet si se hiciera en el hilo
    principal. La comunicación de vuelta hacia la interfaz se hace con
    callbacks (on_texto_cambia, on_prediccion_cambia, etc.), que la
    pantalla usa para refrescar sus textos.

    Ciclo de vida:
        t = SignLanguageTranslator(callbacks...)
        t.start()      # arranca el hilo; devuelve enseguida
        t.is_busy      # True mientras arranca o está en marcha
        t.stop()       # pide parar y espera a que el hilo termine

    El estado se lleva en banderas booleanas (_running, _starting,
    _stop_requested, _clear_requested) que el hilo consulta en cada
    vuelta del bucle: es la forma sencilla de pedirle cosas a un hilo
    sin tener que interrumpirlo.
    """

    def __init__(self, on_started=None, on_stopped=None, on_error=None,
                 on_text_change=None, on_prediction_change=None, get_camera_rect=None):
        """Guarda los callbacks y deja todo listo, sin arrancar nada.

        Args:
            on_started: se llama cuando la cámara ya está funcionando.
            on_stopped: se llama al terminar, salga bien o mal.
            on_error: se llama con un mensaje de error para mostrar.
            on_text_change: se llama con el texto acumulado cada vez que
                cambia.
            on_prediction_change: se llama con (seña, confianza) en cada
                predicción.
            get_camera_rect: función sin argumentos que devuelve dónde
                colocar la ventana de vídeo. Normalmente es una lambda
                que llama a compute_camera_screen_rect(page).

        Todos son opcionales: si alguno es None, simplemente no se
        avisa de ese evento.
        """
        self.on_started = on_started
        self.on_stopped = on_stopped
        self.on_error = on_error
        self.on_text_change = on_text_change
        self.on_prediction_change = on_prediction_change
        self.get_camera_rect = get_camera_rect

        self._cap = None
        self._detector = None
        self._thread = None
        self._running = False
        self._starting = False
        self._stop_requested = False
        self._clear_requested = False

    @property
    def is_running(self) -> bool:
        """True si la cámara está capturando ahora mismo."""
        return self._running

    @property
    def is_busy(self) -> bool:
        """True si está en marcha O todavía arrancando.

        Es la que hay que mirar antes de arrancar o parar: entre pulsar
        el botón y tener la cámara lista pasan varios segundos (cargar
        el modelo), y en ese hueco is_running todavía es False aunque no
        se deba arrancar otra vez.
        """
        return self._running or self._starting

    def clear_text(self):
        """Pide borrar el texto acumulado.

        No lo borra aquí: solo levanta una bandera que el hilo atiende
        en la siguiente vuelta del bucle. Así se evita tocar a la vez
        desde dos hilos la variable del texto.
        """
        self._clear_requested = True

    def start(self):
        """Arranca la cámara y el reconocimiento en un hilo aparte.

        Devuelve el control inmediatamente: cargar el modelo y abrir la
        webcam ocurre dentro del hilo. El hilo es `daemon`, así que no
        impide que la aplicación se cierre.

        Si ya estaba en marcha (o arrancando), no hace nada.
        """
        if self.is_busy:
            return
        self._starting = True
        self._stop_requested = False
        self._thread = threading.Thread(target=self._setup_and_run, daemon=True)
        self._thread.start()

    def stop(self):
        """Pide parar y espera a que el hilo termine de verdad.

        El `join` con 5 segundos de tope es importante: garantiza que la
        webcam quedó liberada antes de que la app siga (por ejemplo,
        antes de cambiar de pantalla o cerrarse). Si el hilo se quedara
        colgado, tras 5 segundos se continúa igualmente para no dejar la
        interfaz congelada.
        """
        self._stop_requested = True
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _fail(self, message: str):
        """Deja el motor parado y avisa del error a la interfaz.

        Args:
            message: texto que se mostrará en rojo en la pantalla.
        """
        self._starting = False
        self._running = False
        if self.on_error:
            self.on_error(message)

    def _setup_and_run(self):
        """Prepara todo y ejecuta el bucle. Es el cuerpo del hilo.

        Va en este orden, y cada paso puede fallar con su propio mensaje
        para el usuario:
            1. cargar el modelo LSTM,
            2. crear el detector de manos de MediaPipe,
            3. abrir la webcam (en Windows con el backend DSHOW, que
               arranca mucho más rápido que el que trae por defecto),
            4. avisar de que ya está en marcha y entrar en el bucle.

        El bloque `finally` es la parte crítica: pase lo que pase (error,
        parada normal o cierre de la ventana) suelta la cámara, cierra el
        detector y destruye la ventana de OpenCV. Sin eso, la webcam se
        quedaría ocupada hasta cerrar la aplicación.
        """
        try:
            _get_model()
        except Exception as ex:
            self._fail(f"Could not load the model: {ex}")
            return

        try:
            self._detector = crear_detector(HAND_LANDMARKER_PATH)
        except Exception as ex:
            self._fail(f"Could not load the hand detector: {ex}")
            return

        if platform.system() == "Windows":
            self._cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        else:
            self._cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self._cap.isOpened():
            self._cap = None
            self._fail("Could not open the camera. Check permissions or the camera index.")
            return

        self._starting = False
        self._running = True
        if self.on_started:
            self.on_started()

        try:
            self._loop()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            if self.on_error:
                self.on_error(f"Error during translation: {ex}")
        finally:
            if self._cap is not None:
                self._cap.release()
                self._cap = None
            if self._detector is not None:
                self._detector.close()
                self._detector = None
            try:
                cv2.destroyWindow(WINDOW_TITLE)
            except cv2.error:
                pass
            self._running = False
            if self.on_stopped:
                self.on_stopped()

    def _reposition_window(self):
        """Recoloca la ventana de OpenCV sobre el hueco de la interfaz.

        Se llama al arrancar y luego cada cierto número de frames
        (REPOSITION_EVERY_N_FRAMES), para que el vídeo siga en su sitio
        aunque el usuario mueva o redimensione la ventana de la app.

        Los errores se ignoran: si la ventana ya no existe o el sistema
        no deja moverla, es preferible seguir traduciendo.
        """
        if self.get_camera_rect is None:
            return
        try:
            x, y, w, h = self.get_camera_rect()
            cv2.resizeWindow(WINDOW_TITLE, w, h)
            cv2.moveWindow(WINDOW_TITLE, x, y)
        except Exception:
            pass

    def _loop(self):
        """Bucle principal: un frame, una vuelta. Corre en el hilo.

        Resumen de lo que hace en cada vuelta:
            1. lee un frame de la webcam y lo voltea (efecto espejo, que
               es como la gente espera verse);
            2. detecta manos con MediaPipe y las dibuja encima;
            3. calcula el vector de características y le añade el
               "delta" (la diferencia con el frame anterior), que es lo
               que le dice al modelo cómo se está moviendo la mano;
            4. cuando hay suficientes frames acumulados, normaliza la
               secuencia y se la pasa al modelo;
            5. estabiliza el resultado: una predicción solo se acepta si
               supera el umbral de confianza, le saca ventaja suficiente
               a la segunda opción y se repite al menos 3 veces en el
               historial. Esto es lo que evita que el texto se llene de
               palabras sueltas por un gesto a medias;
            6. añade la palabra al texto (respetando el cooldown para no
               repetirla), la dibuja sobre el vídeo y avisa a la
               interfaz;
            7. atiende el teclado: Q o ESC salen, R recoloca la ventana,
               retroceso borra un carácter y C borra todo el texto.

        Sale del bucle cuando se pide parar, cuando se pulsa Q/ESC o
        cuando el usuario cierra la ventana de vídeo a mano.
        """
        cache = _get_model()
        model = cache["model"]
        labels = cache["labels"]
        X_mean = cache["X_mean"]
        X_std = cache["X_std"]

        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
        self._reposition_window()
        try:
            cv2.setWindowProperty(WINDOW_TITLE, cv2.WND_PROP_TOPMOST, 1)
        except cv2.error:
            pass

        secuencia = deque(maxlen=FRAMES_MODELO)
        frames_con_manos = deque(maxlen=FRAMES_MODELO)
        historial = deque(maxlen=HISTORIAL_LEN)

        pred_estable = ""
        texto = ""
        ultima_palabra = ""
        ultimo_tiempo = 0.0
        confianza = 0.0

        ultimo_tiempo_mano = time.time()
        frame_count = 0
        ultimo_frame = None
        ultima_pred_raw = None
        texto_reportado = None

        loop_start = time.monotonic()
        last_timestamp_ms = -1

        while not self._stop_requested:
            ok, frame = self._cap.read()
            if not ok:
                continue

            if self._clear_requested:
                texto = ""
                ultima_palabra = ""
                self._clear_requested = False

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            timestamp_ms = int((time.monotonic() - loop_start) * 1000)
            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1
            last_timestamp_ms = timestamp_ms

            result = detectar(self._detector, rgb, timestamp_ms)

            hay_manos = tiene_manos(result)
            if hay_manos:
                ultimo_tiempo_mano = time.time()
                dibujar_manos(frame, result)
                frames_con_manos.append(1)
            else:
                frames_con_manos.append(0)
                pred_estable = ""
                confianza = 0.0
                historial.clear()
                ultima_pred_raw = None

                tiempo_sin_mano = time.time() - ultimo_tiempo_mano
                if tiempo_sin_mano > COOLDOWN_ESPACIO:
                    if texto != "" and not texto.endswith(" "):
                        texto += " "
                        ultima_palabra = ""

            frame_actual = extraer_coords_dinamicas(result)
            if ultimo_frame is None:
                delta = [0.0] * len(frame_actual)
            else:
                delta = np.array(frame_actual) - np.array(ultimo_frame)
            ultimo_frame = frame_actual.copy()

            frame_final = np.concatenate([frame_actual, delta])
            secuencia.append(frame_final)

            frame_count += 1
            if frame_count % REPOSITION_EVERY_N_FRAMES == 0:
                self._reposition_window()

            manos_en_buffer = sum(frames_con_manos)

            if manos_en_buffer < MIN_FRAMES_CON_MANOS:
                confianza = 0.0

            top_indices = None
            if (len(secuencia) >= FRAMES_MODELO
                    and manos_en_buffer >= MIN_FRAMES_CON_MANOS
                    and frame_count % PREDICT_CADA == 0):

                entrada = np.array(secuencia)
                entrada = (entrada - X_mean) / (X_std + 1e-7)
                entrada = np.expand_dims(entrada, axis=0)

                predicciones = model.predict(entrada, verbose=0)[0]
                top_indices = np.argsort(predicciones)[::-1]
                top1 = top_indices[0]
                top2 = top_indices[1] if len(top_indices) > 1 else top1

                confianza = float(predicciones[top1])
                diferencia = predicciones[top1] - predicciones[top2]
                pred = labels[top1]
                diferencia_ok = (diferencia > UMBRAL_DIFERENCIA) if len(labels) > 1 else True

                if confianza > UMBRAL_CONFIANZA and diferencia_ok:
                    historial.append(pred)
                else:
                    historial.append("__none__")

                if len(historial) == historial.maxlen:
                    conteo = Counter(historial)
                    palabra, cantidad = conteo.most_common(1)[0]

                    if cantidad >= 3 and palabra != "__none__":
                        pred_estable = palabra
                        tiempo_actual = time.time()

                        if pred_estable != ultima_pred_raw:
                            secuencia.clear()
                            historial.clear()
                            ultima_pred_raw = pred_estable

                        if (pred_estable != ultima_palabra
                                or tiempo_actual - ultimo_tiempo > COOLDOWN):
                            if pred_estable != "idle":
                                texto += pred_estable + " "
                                ultima_palabra = pred_estable
                                ultimo_tiempo = tiempo_actual

                if self.on_prediction_change:
                    self.on_prediction_change(pred_estable, confianza)

            if top_indices is not None:
                y_pos = 300
                for i in range(min(3, len(labels))):
                    idx = top_indices[i]
                    cv2.putText(frame, f"{labels[idx]}: {predicciones[idx]:.2f}",
                                (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    y_pos += 40

            cv2.putText(frame, f"Sign: {pred_estable}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(frame, f"Confidence: {confianza:.2f}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            texto_display = texto[-60:] if len(texto) > 60 else texto
            cv2.putText(frame, f"Text: {texto_display}", (10, 155),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            pct = int((manos_en_buffer / FRAMES_MODELO) * 100)
            color_barra = (0, 255, 0) if manos_en_buffer >= MIN_FRAMES_CON_MANOS else (0, 165, 255)
            cv2.putText(frame, f"Hand buffer: {pct}%", (10, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_barra, 2)

            cv2.imshow(WINDOW_TITLE, frame)

            if texto != texto_reportado:
                texto_reportado = texto
                if self.on_text_change:
                    self.on_text_change(texto)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
            elif key == ord("r"):
                self._reposition_window()
            elif key == 8:
                texto = texto[:-1]
            elif key == ord("c"):
                texto = ""

            if frame_count > 15:
                try:
                    if cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                        break
                except cv2.error:
                    break


# ------------------------------------------------------------------
# Registro global del traductor activo, para que main.py pueda apagar
# la cámara al cambiar de pantalla o al cerrar la app. Solo puede haber
# uno a la vez: cada visita a /scan sustituye al anterior.
# ------------------------------------------------------------------
_active_translator = {"instance": None}


def stop_active_translator():
    """Apaga el traductor que esté activo, si es que hay alguno.

    Es la función que llama el enrutador de main.py en cada cambio de
    ruta. Si nunca se abrió la pantalla, o ya estaba parado, no hace
    nada.
    """
    t = _active_translator["instance"]
    if t is not None and t.is_busy:
        t.stop()


def screen_translator(page: ft.Page):
    """Dibuja la pantalla del traductor sobre `page`.

    Monta la interfaz (cabecera, hueco de la cámara, botón de activar y
    panel de traducción en vivo), crea el motor SignLanguageTranslator y
    engancha sus callbacks a los textos de la pantalla.

    Ojo: montar la pantalla NO enciende la cámara. Eso ocurre cuando el
    usuario pulsa "Start Translation", así que abrir /scan es barato y
    seguro aunque no haya webcam.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    page.title = "Scan Signs"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    # ---------- Cabecera: botón de volver y títulos ----------
    back_button = ft.Container(
        content=ft.Icon(ft.Icons.ARROW_BACK, color=ft.Colors.WHITE, size=20),
        width=40,
        height=40,
        bgcolor=COLOR_BACK_BTN_BG,
        border_radius=16.5,
        alignment=ft.Alignment.CENTER,
        on_click=lambda e: page.go("/dashboard"),
    )

    header = ft.Row(
        controls=[
            back_button,
            ft.Column(
                controls=[
                    ft.Text("Scan Signs", size=26, weight=ft.FontWeight.NORMAL, color=ft.Colors.WHITE),
                    ft.Text("AI detects your sign in real time", size=15, color=COLOR_WHITE_TEXT),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    header_container = ft.Container(
        content=header,
        padding=ft.Padding.only(left=40, right=40, top=40, bottom=20),
        width=float("inf"),
    )

    # ---------- Hueco de la cámara (solo diseño) ----------
    # Esto es un recuadro azul vacío: el vídeo de verdad lo pinta OpenCV
    # en su propia ventana, colocada justo encima de este hueco.
    camera_icon = ft.Container(
        content=ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, color=COLOR_TURQUOISE, size=26),
        width=56,
        height=56,
        bgcolor=COLOR_CAM_ICON_BG,
        border=ft.Border.all(0.9, COLOR_CAM_ICON_BORDER),
        border_radius=999,
        alignment=ft.Alignment.CENTER,
    )
    camera_status_text = ft.Text(
        "AI detects your sign in real time",
        size=18, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER,
    )
    camera_card = ft.Container(
        content=ft.Column(
            controls=[camera_icon, camera_status_text],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=40),
        expand=True,
        bgcolor=COLOR_CARD_BLUE,
        border_radius=20,
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20,
                             color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
    )

    camera_error_text = ft.Text("", size=14, color=COLOR_RED, text_align=ft.TextAlign.CENTER, visible=False)

    activar_btn_text = ft.Text(
        "🎥 Start Translation", size=20, color=COLOR_CARD_BLUE,
        text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600,
    )

    # ---------- Panel de traducción en vivo ----------
    current_sign_text = ft.Text("Current sign: —", size=18, color=ft.Colors.WHITE)
    confidence_text = ft.Text("Confidence: 0%", size=15, color=COLOR_WHITE_TEXT)
    recognized_text_display = ft.Text("", size=20, color=ft.Colors.WHITE, selectable=True)
    recognized_text_box = ft.Container(
        content=ft.Column(controls=[recognized_text_display], scroll=ft.ScrollMode.AUTO, expand=True),
        padding=15,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.3, COLOR_BG_DARK),
        border_radius=10,
    )

    def clear_translation_text(e):
        """Borra el texto reconocido, en el motor y en la pantalla.

        Hay que hacerlo en los dos sitios: el motor guarda su propia
        copia del texto acumulado y seguiría añadiendo palabras al
        final del anterior.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        translator.clear_text()
        recognized_text_display.value = ""
        recognized_text_display.update()

    translation_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🗣️ Live Translation", size=18, color=COLOR_GOLD),
                current_sign_text,
                confidence_text,
                recognized_text_box,
                ft.TextButton("Clear text", on_click=clear_translation_text),
            ],
            spacing=12,
            expand=True,
        ),
        padding=20,
        bgcolor=COLOR_TIPS_BG,
        border=ft.Border.all(0.9, COLOR_TIPS_BORDER),
        border_radius=20,
        expand=3,
    )

    tips_items = [
        "• Place your hand inside the turquoise frame",
        "• Make sure you have good lighting",
        "• Hold the sign for 2-3 seconds",
    ]
    tips_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("💡 Tips for better results", size=16, color=COLOR_GOLD),
                ft.Column(
                    controls=[ft.Text(t, size=15, color=ft.Colors.WHITE) for t in tips_items],
                    spacing=10,
                ),
            ],
            spacing=15,
        ),
        padding=25,
        bgcolor=COLOR_TIPS_BG,
        border=ft.Border.all(0.9, COLOR_TIPS_BORDER),
        border_radius=20,
        expand=1,
    )

    right_column = ft.Column(
        controls=[translation_card, tips_card],
        spacing=20,
        expand=True,
    )

    def set_idle_state():
        """Deja la pantalla en estado de reposo (cámara apagada).

        Botón turquesa con "Start Translation". Es también el estado al
        que se vuelve después de un error o de parar la cámara.
        """
        activar_btn_text.value = "🎥 Start Translation"
        activar_btn.bgcolor = COLOR_TURQUOISE
        camera_status_text.value = "AI detects your sign in real time"
        activar_btn_text.update()
        activar_btn.update()
        camera_status_text.update()

    def set_loading_state():
        """Estado intermedio mientras se carga el modelo.

        Puede tardar varios segundos la primera vez. Sin este aviso
        parecería que el botón no hizo nada y el usuario lo pulsaría dos
        veces.
        """
        activar_btn_text.value = "⏳ Loading model..."
        activar_btn.bgcolor = ft.Colors.with_opacity(0.5, COLOR_TURQUOISE)
        camera_status_text.value = "Loading model, one moment..."
        activar_btn_text.update()
        activar_btn.update()
        camera_status_text.update()

    def set_active_state():
        """Estado de cámara encendida: botón rojo para parar.

        Lo llama el motor (callback on_started) cuando la webcam ya está
        capturando de verdad, no cuando se pulsó el botón.
        """
        activar_btn_text.value = "⏹ Stop Translation"
        activar_btn.bgcolor = COLOR_RED
        camera_status_text.value = "Translation active in a separate window"
        activar_btn_text.update()
        activar_btn.update()
        camera_status_text.update()

    def show_error(message: str):
        """Muestra un error en rojo y vuelve al estado de reposo.

        Args:
            message: texto del error, tal cual lo manda el motor
                (cámara ocupada, modelo que no carga, etc.).
        """
        camera_error_text.value = message
        camera_error_text.visible = True
        camera_error_text.update()
        set_idle_state()

    def handle_text_change(texto: str):
        """Refresca el texto reconocido en el panel derecho.

        Lo llama el motor desde SU hilo cada vez que el texto cambia.

        Args:
            texto: texto acumulado completo, no solo la palabra nueva.
        """
        recognized_text_display.value = texto
        recognized_text_display.update()

    def handle_prediction_change(pred_estable: str, confianza: float):
        """Refresca la seña actual y su porcentaje de confianza.

        Args:
            pred_estable: seña reconocida ya estabilizada, o cadena
                vacía si ahora mismo no hay ninguna clara (entonces se
                muestra un guion).
            confianza: valor de 0 a 1 que se muestra como porcentaje.
        """
        current_sign_text.value = f"Current sign: {pred_estable or '—'}"
        confidence_text.value = f"Confidence: {int(confianza * 100)}%"
        current_sign_text.update()
        confidence_text.update()

    def handle_stopped():
        """Devuelve la pantalla a reposo cuando el motor se para.

        Se dispara tanto si paró el usuario como si se cerró la ventana
        de vídeo a mano, que es justo el caso que hay que cubrir: si no,
        el botón seguiría diciendo "Stop Translation" con la cámara ya
        apagada.
        """
        set_idle_state()

    translator = SignLanguageTranslator(
        on_started=set_active_state,
        on_stopped=handle_stopped,
        on_error=show_error,
        on_text_change=handle_text_change,
        on_prediction_change=handle_prediction_change,
        get_camera_rect=lambda: compute_camera_screen_rect(page),
    )
    _active_translator["instance"] = translator

    def toggle_camera(e):
        """Enciende o apaga la cámara según el estado actual.

        Es el manejador del botón grande: hace de interruptor. Al
        encender, primero limpia el error anterior y pone el estado de
        "cargando", porque arrancar no es instantáneo.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        if translator.is_busy:
            translator.stop()
            set_idle_state()
        else:
            camera_error_text.visible = False
            camera_error_text.update()
            set_loading_state()
            translator.start()

    activar_btn = ft.Container(
        content=activar_btn_text,
        alignment=ft.Alignment.CENTER,
        bgcolor=COLOR_TURQUOISE,
        border_radius=20,
        padding=ft.Padding.symmetric(vertical=16),
        margin=ft.Margin.only(top=20),
        width=float("inf"),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=15,
                             color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), offset=ft.Offset(0, 4)),
        on_click=toggle_camera,
        ink=True,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    left_column = ft.Column(controls=[camera_card, activar_btn, camera_error_text], expand=3, spacing=8)

    main_row = ft.ResponsiveRow(
        controls=[
            ft.Container(content=left_column, col={"xs": 12, "md": 7}, expand=True),
            ft.Container(content=right_column, col={"xs": 12, "md": 5}, expand=True),
        ],
        expand=True,
        spacing=25,
        run_spacing=25,
    )
    main_row_container = ft.Container(
        content=main_row,
        padding=ft.Padding.only(left=40, right=40, top=0, bottom=40),
        expand=True,
    )

    scan_screen = ft.Container(
        content=ft.Column(controls=[header_container, main_row_container], spacing=0, expand=True),
        bgcolor=COLOR_BG_DARK,
        expand=True,
    )

    root_container = ft.Container(
        content=scan_screen,
        width=CONTENT_MAX_WIDTH,
        expand=True,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=50, color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)),
    )

    page.add(ft.Row(controls=[root_container], alignment=ft.MainAxisAlignment.CENTER, expand=True))


if __name__ == "__main__":
    def _standalone(page: ft.Page):
        """Arranque suelto de esta pantalla, para probar el traductor.

        Con `python screens/translator.py` se abre solo el traductor,
        sin pasar por el login. Útil para probar la cámara y el modelo.
        El botón de volver no funcionará: el enrutador está en main.py.

        Args:
            page: la página que crea Flet.
        """
        # Esta pantalla mantiene a propósito una tarjeta de ancho máximo
        # fijo y centrada (ver CONTENT_MAX_WIDTH y
        # compute_camera_screen_rect, que colocan la ventana de OpenCV
        # respecto a ella). Por eso se maximiza la ventana como en el
        # resto de la app, pero la tarjeta no se estira de lado a lado.
        page.window.maximized = True
        page.window.min_width = 1100
        page.window.min_height = 700
        page.update()
        screen_translator(page)

    ft.run(_standalone)