"""
Pantalla de traducción de lenguaje de señas (screens/translator.py).

El video de la cámara se muestra en su propia ventana de OpenCV, con
la lógica de predict_lstm.py corriendo encima: detección de manos con
MediaPipe + modelo LSTM + estabilización de la predicción. El texto
reconocido también se refleja en vivo dentro del panel derecho de la
app de Flet.
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
# Hacer que "from hand_detector import ..." funcione sin importar
# desde qué carpeta se ejecute la app (screens/ o main/).
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
WINDOW_TITLE = "SignScan LSTM (Q: salir | R: re-sincronizar)"

# ---- Geometría estimada del recuadro de cámara ----
HEADER_HEIGHT = 117
MAIN_ROW_SIDE_PADDING = 40
MAIN_ROW_BOTTOM_PADDING = 40
COLUMN_SPACING = 25
LEFT_COLUMN_FRACTION = 7 / 12
ACTIVAR_BTN_HEIGHT = 82
ERROR_TEXT_RESERVED = 20
LEFT_COLUMN_INNER_SPACING = 16

# La app corre en full_screen (main.py), así que no hay barra de
# título ni borde de ventana nativos que restar.
TITLE_BAR_HEIGHT = 0
WINDOW_BORDER = 0

CALIBRATION_OFFSET_X = 0
CALIBRATION_OFFSET_Y = 0

REPOSITION_EVERY_N_FRAMES = 20


def compute_camera_screen_rect(page: ft.Page):
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


FRAMES_MODELO = 45
MIN_FRAMES_CON_MANOS = 20
HISTORIAL_LEN = 5
COOLDOWN = 2
COOLDOWN_ESPACIO = 2
PREDICT_CADA = 5
UMBRAL_CONFIANZA = 0.70
UMBRAL_DIFERENCIA = 0.15


_model_cache = {"model": None, "labels": None, "X_mean": None, "X_std": None}


def _get_model():
    if _model_cache["model"] is None:
        from keras.models import load_model

        _model_cache["model"] = load_model(MODEL_PATH)
        _model_cache["labels"] = np.load(LABELS_PATH, allow_pickle=True)
        _model_cache["X_mean"] = np.load(X_MEAN_PATH)
        _model_cache["X_std"] = np.load(X_STD_PATH)
    return _model_cache


class SignLanguageTranslator:
    """Corre la cámara + detección de manos + modelo LSTM en un hilo
    aparte, mostrando el video en su propia ventana de OpenCV y
    reportando texto/predicciones a la UI de Flet vía callbacks."""

    def __init__(self, on_started=None, on_stopped=None, on_error=None,
                 on_text_change=None, on_prediction_change=None, get_camera_rect=None):
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
        return self._running

    @property
    def is_busy(self) -> bool:
        return self._running or self._starting

    def clear_text(self):
        self._clear_requested = True

    def start(self):
        if self.is_busy:
            return
        self._starting = True
        self._stop_requested = False
        self._thread = threading.Thread(target=self._setup_and_run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_requested = True
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _fail(self, message: str):
        self._starting = False
        self._running = False
        if self.on_error:
            self.on_error(message)

    def _setup_and_run(self):
        try:
            _get_model()
        except Exception as ex:
            self._fail(f"No se pudo cargar el modelo: {ex}")
            return

        try:
            self._detector = crear_detector(HAND_LANDMARKER_PATH)
        except Exception as ex:
            self._fail(f"No se pudo cargar el detector de manos: {ex}")
            return

        if platform.system() == "Windows":
            self._cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        else:
            self._cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self._cap.isOpened():
            self._cap = None
            self._fail("No se pudo abrir la cámara. Revisa permisos o el índice de cámara.")
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
                self.on_error(f"Error durante la traducción: {ex}")
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
        if self.get_camera_rect is None:
            return
        try:
            x, y, w, h = self.get_camera_rect()
            cv2.resizeWindow(WINDOW_TITLE, w, h)
            cv2.moveWindow(WINDOW_TITLE, x, y)
        except Exception:
            pass

    def _loop(self):
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

            cv2.putText(frame, f"Dinamica: {pred_estable}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(frame, f"Confianza: {confianza:.2f}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            texto_display = texto[-60:] if len(texto) > 60 else texto
            cv2.putText(frame, f"Texto: {texto_display}", (10, 155),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            pct = int((manos_en_buffer / FRAMES_MODELO) * 100)
            color_barra = (0, 255, 0) if manos_en_buffer >= MIN_FRAMES_CON_MANOS else (0, 165, 255)
            cv2.putText(frame, f"Buffer manos: {pct}%", (10, 210),
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
# Registro global del traductor activo (para que main.py pueda
# apagar la cámara al cambiar de pantalla o cerrar la app).
# ------------------------------------------------------------------
_active_translator = {"instance": None}


def stop_active_translator():
    t = _active_translator["instance"]
    if t is not None and t.is_busy:
        t.stop()


def screen_translator(page: ft.Page):
    page.title = "Escanear Señas"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    # ---------- Header ----------
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
                    ft.Text("Escanear Señas", size=26, weight=ft.FontWeight.NORMAL, color=ft.Colors.WHITE),
                    ft.Text("IA detecta tu seña en tiempo real", size=15, color=COLOR_WHITE_TEXT),
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

    # ---------- Recuadro de cámara (sólo diseño) ----------
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
        "IA detecta tu seña en tiempo real",
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
        "🎥 Iniciar Traducción", size=20, color=COLOR_CARD_BLUE,
        text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600,
    )

    # ---------- Panel de traducción en vivo ----------
    current_sign_text = ft.Text("Seña actual: —", size=18, color=ft.Colors.WHITE)
    confidence_text = ft.Text("Confianza: 0%", size=15, color=COLOR_WHITE_TEXT)
    recognized_text_display = ft.Text("", size=20, color=ft.Colors.WHITE, selectable=True)
    recognized_text_box = ft.Container(
        content=ft.Column(controls=[recognized_text_display], scroll=ft.ScrollMode.AUTO, expand=True),
        padding=15,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.3, COLOR_BG_DARK),
        border_radius=10,
    )

    def clear_translation_text(e):
        translator.clear_text()
        recognized_text_display.value = ""
        recognized_text_display.update()

    translation_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🗣️ Traducción en vivo", size=18, color=COLOR_GOLD),
                current_sign_text,
                confidence_text,
                recognized_text_box,
                ft.TextButton("Limpiar texto", on_click=clear_translation_text),
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
        "• Coloca tu mano dentro del recuadro turquesa",
        "• Asegúrate de tener buena iluminación",
        "• Mantén la seña por 2–3 segundos",
    ]
    tips_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("💡 Consejos para mejores resultados", size=16, color=COLOR_GOLD),
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
        activar_btn_text.value = "🎥 Iniciar Traducción"
        activar_btn.bgcolor = COLOR_TURQUOISE
        camera_status_text.value = "IA detecta tu seña en tiempo real"
        activar_btn_text.update()
        activar_btn.update()
        camera_status_text.update()

    def set_loading_state():
        activar_btn_text.value = "⏳ Cargando modelo..."
        activar_btn.bgcolor = ft.Colors.with_opacity(0.5, COLOR_TURQUOISE)
        camera_status_text.value = "Cargando modelo, un momento..."
        activar_btn_text.update()
        activar_btn.update()
        camera_status_text.update()

    def set_active_state():
        activar_btn_text.value = "⏹ Detener Traducción"
        activar_btn.bgcolor = COLOR_RED
        camera_status_text.value = "Traducción activa en una ventana aparte"
        activar_btn_text.update()
        activar_btn.update()
        camera_status_text.update()

    def show_error(message: str):
        camera_error_text.value = message
        camera_error_text.visible = True
        camera_error_text.update()
        set_idle_state()

    def handle_text_change(texto: str):
        recognized_text_display.value = texto
        recognized_text_display.update()

    def handle_prediction_change(pred_estable: str, confianza: float):
        current_sign_text.value = f"Seña actual: {pred_estable or '—'}"
        confidence_text.value = f"Confianza: {int(confianza * 100)}%"
        current_sign_text.update()
        confidence_text.update()

    def handle_stopped():
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
        page.window.width = 1280
        page.window.height = 820
        page.run_task(page.window.center)
        screen_translator(page)

    ft.run(_standalone)