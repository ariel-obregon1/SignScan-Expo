# SignScan — Plataforma Inteligente de Traducción de Lenguaje de Señas

Sistema de reconocimiento de lenguaje de señas en tiempo real utilizando visión por computadora e inteligencia artificial. SignScan detecta las manos mediante webcam, extrae los *landmarks* utilizando MediaPipe y traduce las señas a texto mediante modelos de Machine Learning y Deep Learning.

El proyecto integra reconocimiento de señas estáticas y dinámicas, además de una aplicación completa desarrollada en Flet para facilitar la comunicación, el aprendizaje y la accesibilidad para personas sordas y oyentes.

---

## Objetivo

SignScan busca facilitar la comunicación entre personas sordas y oyentes mediante la traducción automática de lenguaje de señas, combinando tecnologías de visión por computadora, aprendizaje automático e interfaces accesibles.

---

## Características principales

- Reconocimiento de señas estáticas en tiempo real.
- Reconocimiento de señas dinámicas mediante secuencias de movimiento.
- Traducción automática de señas a texto.
- Detección de manos con MediaPipe.
- Interfaz gráfica desarrollada con Flet.
- Sistema de aprendizaje de lenguaje de señas.
- Historial de traducciones.
- Gestión de perfiles de usuario.
- Base de datos local SQLite.
- Arquitectura modular para futuras ampliaciones.

---

## Arquitectura general

| Módulo | Función | Tecnología principal |
|---------|----------|----------|
| **static/** | Reconocimiento de señas estáticas | Random Forest |
| **lstm/** | Reconocimiento de señas dinámicas | BiLSTM |
| **Aplicación principal** | Interfaz, aprendizaje, historial y traducción | Flet + SQLite |

---

## Requisitos

- Python 3.12
- Webcam
- Windows 10/11 (recomendado)

Instalación:

```bash
# Módulo dinámico (LSTM)
cd lstm
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Módulo estático
cd static
pip install -r requirements.txt
```

---

## Modelo de detección de manos (solo módulo LSTM)

El módulo dinámico utiliza el Hand Landmarker de MediaPipe (Tasks API).

Descargar una única vez:

```bash
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
```

El archivo `hand_landmarker.task` no se incluye en el repositorio.

---

# Módulo Estático (`static/`)

Reconoce letras y señas que no requieren movimiento.

| Script | Función |
|----------|----------|
| `capturar_estaticas.py` | Captura muestras por webcam |
| `limpiar_datos.py` | Limpieza del dataset |
| `train_estaticas.py` | Entrenamiento del modelo Random Forest |
| `predict_estaticas.py` | Reconocimiento en tiempo real |
| `main.py` | Interfaz gráfica |

### Flujo de trabajo

```text
capturar_estaticas.py
        ↓
limpiar_datos.py
        ↓
train_estaticas.py
        ↓
predict_estaticas.py
```

---

# Módulo Dinámico (`lstm/`)

Reconoce palabras y señas que requieren movimiento.

| Script | Función |
|----------|----------|
| `capturar_lstm.py` | Captura secuencias de 45 frames |
| `train_lstm.py` | Entrenamiento de la red BiLSTM |
| `predict_lstm.py` | Reconocimiento en tiempo real |
| `hand_detector.py` | Detección de manos con MediaPipe |
| `preprocesar_lsa64.py` | Conversión del dataset LSA64 |
| `verificar_multiclase.py` | Verificación de clasificación |

### Formato de los datos

Cada muestra corresponde a una secuencia:

```text
(45, 504)
```

donde:

```text
504 = 252 características actuales + 252 deltas
```

Cada mano utiliza:

```text
21 landmarks ×
(abs_x, abs_y, abs_z,
 rel_x, rel_y, rel_z)
```

---

## Modelo incluido

El repositorio incluye un modelo de demostración entrenado sobre el dataset LSA64.

Este modelo se proporciona únicamente como ejemplo de funcionamiento.

Para entrenar vocabulario personalizado se deben capturar nuevas muestras utilizando:

```text
capturar_lstm.py
```

y posteriormente reentrenar mediante:

```text
train_lstm.py
```

---

## Dataset LSA64 (opcional)

El módulo dinámico puede entrenarse utilizando el dataset público LSA64.

Características:

- 64 señas.
- 10 participantes.
- Más de 3200 videos.

Los videos originales no se incluyen en este repositorio.

---

## Tecnologías utilizadas

- Python 3.12
- Flet
- OpenCV
- MediaPipe
- TensorFlow
- Keras
- Scikit-Learn
- NumPy
- Pandas
- SQLite

---

## Estado actual del proyecto

Actualmente SignScan cuenta con:

- Reconocimiento de señas estáticas funcional.
- Reconocimiento de señas dinámicas funcional.
- Captura y entrenamiento de nuevas señas.
- Traducción en tiempo real mediante webcam.
- Interfaz gráfica moderna.
- Sistema de aprendizaje integrado.
- Historial de traducciones.
- Base de datos local.

El proyecto continúa en desarrollo con el objetivo de ampliar el vocabulario reconocido y mejorar la precisión del sistema.

---

## Futuras mejoras

- Ampliación del vocabulario.
- Mayor cantidad de señas dinámicas.
- Traducción bidireccional.
- Compatibilidad móvil.
- Soporte para más variantes de lengua de señas.
- Mejoras de precisión y rendimiento.

---

## Licencia

Código bajo licencia MIT.

El dataset LSA64 y los modelos de MediaPipe mantienen sus respectivas licencias.
