# SignScan — Traductor de Lenguaje de Señas

Sistema de reconocimiento de lenguaje de señas en tiempo real usando visión por
computadora ([MediaPipe](https://developers.google.com/mediapipe)) y machine learning.
Detecta las manos por webcam, extrae los *landmarks* y los traduce a texto.

El proyecto tiene **dos módulos**:

| Módulo | Carpeta | Señas | Modelo |
|--------|---------|-------|--------|
| **Estático** | [`static/`](static/) | Letras / señas sin movimiento | RandomForest |
| **Dinámico** | [`lstm/`](lstm/) | Palabras con movimiento | BiLSTM (secuencias de 45 frames) |

---

## Requisitos

- Python 3.12
- Webcam

Instalación (recomendado un entorno virtual por módulo):

```bash
# Módulo dinámico (LSTM)
cd lstm
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Módulo estático
cd static
pip install -r requirements.txt
```

### Modelo de detección de manos (solo módulo LSTM)

El módulo dinámico usa el *Hand Landmarker* de MediaPipe (Tasks API). Descargalo una vez:

```bash
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
```

(El archivo `hand_landmarker.task` no se incluye en el repo; se descarga aparte.)

---

## Módulo estático (`static/`)

| Script | Función |
|--------|---------|
| `capturar_estaticas.py` | Captura muestras de una seña por webcam |
| `limpiar_datos.py` | Limpia el dataset (filas incompletas) |
| `train_estaticas.py` | Entrena el RandomForest |
| `predict_estaticas.py` | Reconocimiento en vivo (ESC salir · `c` limpiar · `v` voz · ⌫ borrar) |
| `main.py` | Interfaz gráfica (Flet) |

Flujo: `capturar_estaticas.py` → `limpiar_datos.py` → `train_estaticas.py` → `predict_estaticas.py`

---

## Módulo dinámico (`lstm/`)

| Script | Función |
|--------|---------|
| `capturar_lstm.py` | Captura secuencias de 45 frames de una seña |
| `train_lstm.py` | Entrena la red BiLSTM |
| `predict_lstm.py` | Reconocimiento en vivo (ESC salir · `f` pantalla completa · `c` limpiar · ⌫ borrar) |
| `hand_detector.py` | Wrapper de detección de manos (MediaPipe Tasks API) |
| `preprocesar_lsa64.py` | Convierte videos del dataset LSA64 al formato del pipeline |
| `verificar_multiclase.py` | Verifica que el modelo distingue las clases |

**Formato de los datos:** cada muestra es una secuencia `(45, 504)`:
`504 = 252 features actuales + 252 deltas`, donde `252 = mano_izq(126) + mano_der(126)`,
y cada mano son 21 landmarks × `[abs_x, abs_y, abs_z, rel_x, rel_y, rel_z]`.

### Modelo incluido

El repo trae un modelo de **demostración** (`modelo_lstm.keras`) entrenado con **3 señas**
del dataset LSA64 (*Green*, *Bright*, *Food*), con ~95% de accuracy en validación.
Para tu propio vocabulario, capturá señas con `capturar_lstm.py` y reentrená con `train_lstm.py`.

---

## Dataset LSA64 (opcional)

El módulo dinámico puede entrenarse con [LSA64](https://midusi.github.io/lsa64/), un dataset
público de Lengua de Señas Argentina (64 señas, 10 personas, 3200 videos).

> **Nota:** Los videos de LSA64 **no** se incluyen en este repo (tienen su propia licencia).
> Descargá el dataset desde su [sitio oficial](https://midusi.github.io/lsa64/) y procesalo con
> `preprocesar_lsa64.py`.

**Cita:** Ronchetti, F., Quiroga, F., Estrebou, C., Lanzarini, L., Rosete, A.
*LSA64: An Argentinian Sign Language Dataset* (2016). [arXiv:2310.17429](https://arxiv.org/abs/2310.17429)

---

## Licencia

Código bajo licencia MIT. El dataset LSA64 y el modelo de MediaPipe mantienen sus
respectivas licencias.
