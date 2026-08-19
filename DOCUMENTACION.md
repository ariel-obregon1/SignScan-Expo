# Documentación técnica de SignScan

Documento de referencia de la aplicación: cómo está montada, qué hace cada
archivo y cada función, cómo se ejecuta y qué falta por hacer.

El [README.md](README.md) explica el proyecto de cara al público (objetivo,
datasets, modelos). Este documento es para quien va a tocar el código.

---

## 1. Qué se ejecuta y desde dónde

El repositorio tiene tres carpetas y solo una es la aplicación:

| Carpeta | Qué es | ¿Se ejecuta? |
|---|---|---|
| `main/` | **La aplicación.** Interfaz, base de datos y traductor en vivo. | Sí: `python main.py` |
| `lstm/` | Módulo de captura y entrenamiento del modelo de señas dinámicas. | Sí, scripts sueltos |
| `signscan/` | Versión anterior de la app, de hace meses. | No, se conserva como histórico |

Para abrir la aplicación:

```
cd main
python main.py
```

Se abre a pantalla completa. Se cierra con Alt+F4 (la ventana no tiene barra
de título porque `page.window.full_screen` está activo).

---

## 2. Instalación

Requiere **Python 3.12** y **flet 0.80 o superior**. Con flet 0.28 la app no
arranca: `ft.run()` no existe en esa versión.

```
cd main
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Para que el traductor funcione hace falta además el modelo de manos de
MediaPipe, que **no está en el repositorio**. Hay que descargarlo una vez
dentro de `main/`:

```
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
```

Si solo se quiere ver la interfaz (login, perfil, dashboard), basta con
instalar `flet`: la pantalla `/scan` detecta que faltan los paquetes de
cámara e IA y muestra un aviso en vez de romperse.

Para entrenar o capturar señas nuevas, la carpeta `lstm/` tiene su propio
`requirements.txt` (incluye scikit-learn y no necesita flet).

---

## 3. Cómo está organizada la aplicación

```
main/
├── main.py                 punto de entrada y enrutador
├── database.py             capa SQLite (tabla users)
├── session.py              usuario logueado, en memoria
├── hand_detector.py        envoltorio de MediaPipe
├── signscan.db             base de datos (se crea sola)
├── modelo_lstm.keras       modelo entrenado
├── clases.npy              nombres de las señas que reconoce
├── X_mean.npy / X_std.npy  normalización usada al entrenar
├── assets/logo.png         imágenes de la interfaz
└── screens/
    ├── welcome_screen.py       "/"                bienvenida
    ├── sign_up.py              "/create-account"  alta de cuenta
    ├── sign_in.py              "/login"           inicio de sesión
    ├── personalize_profile.py  "/profile"         perfil y avatar
    ├── dashboard.py            "/dashboard"       pantalla principal
    ├── translator.py           "/scan"            traductor en vivo
    └── ___.py                  utilidad suelta (no es una pantalla)
```

### La regla que sostiene todo

Cada pantalla es **una función que recibe la `page` de Flet y le añade
controles**. No devuelve nada, no sabe qué pantalla venía antes ni cuál va
después, y para navegar solo llama a `page.go("/otra-ruta")`.

Quien decide qué se dibuja es el enrutador de `main.py`. Eso permite abrir
cualquier pantalla por separado para trabajar su diseño:

```
python screens/dashboard.py
```

(En ese modo la navegación no funciona, porque el enrutador vive en `main.py`.)

### El enrutado, y por qué se hace así

Este es el punto que más conviene entender antes de tocar `main.py`.

En **Flet 0.80+**, `page.go(ruta)` ya no llama al manejador `on_route_change`.
Le pide al cliente que empuje la ruta, y el cliente solo devuelve el evento
`route_change` **si la ruta cambia de verdad**. Como la app arranca ya en `"/"`,
llamar a `page.go("/")` al inicio no cambiaba nada, no se disparaba ningún
evento y no se dibujaba ninguna pantalla: **la ventana se quedaba en negro**.

Por eso la primera pantalla se dibuja llamando directamente a `render_route()`,
y `on_route_change` se encarga solo de las navegaciones posteriores.

```
arranque  ──> render_route(page.route or "/")   ← directo, sin evento
                      │
pantalla ──page.go()──> cliente ──route_change──> render_route(...)
```

`render_route()` hace siempre tres cosas, en este orden:

1. apagar la cámara si venía del traductor (`stop_active_translator`),
2. vaciar `page.controls`,
3. llamar a la función de la pantalla nueva.

---

## 4. Mapa de rutas

| Ruta | Pantalla | Estado |
|---|---|---|
| `/` | `welcome_screen.screen_welcome` | Completa |
| `/create-account` | `sign_up.screen_signup` | Completa |
| `/login` | `sign_in.screen_signin` | Completa |
| `/profile` | `personalize_profile.screen_personalizeprofile` | Completa (la foto no se guarda) |
| `/dashboard` | `dashboard.screen_dashboard` | Interfaz completa, datos de maqueta |
| `/scan` | `translator.screen_translator` | Funcional, requiere modelo y webcam |
| `/learn`, `/community`, `/video` | Aviso "Coming soon" | Sin implementar |
| Cualquier otra | Bienvenida | Reserva de seguridad |

Las tres rutas "Coming soon" están listadas a propósito. Antes caían en la
pantalla de bienvenida y parecía que la app cerraba la sesión sola.

---

## 5. Flujos de usuario

**Alta de cuenta**

```
/  ──"Create free account"──> /create-account
                                   │ database.create_user()
                                   │ session.set_current_user()
                                   ▼
                              /profile  ──"Save and continue"──> /dashboard
```

**Inicio de sesión**

```
/  ──"Log in"──> /login
                    │ database.authenticate_user()
                    │ session.set_current_user()
                    ▼
                /dashboard
```

**Traducción**

```
/dashboard ──"Scan Signs"──> /scan ──"Start Translation"──> cámara encendida
                                                                  │
                              texto reconocido en el panel derecho ┘
```

Al salir de `/scan` por cualquier vía (botón atrás, cerrar la app), el
enrutador apaga la cámara.

---

## 6. Referencia por archivo

Todas las funciones tienen su explicación completa en el propio código
(docstring). Esta tabla es el índice para saber dónde mirar.

### `main.py` — enrutador

| Función | Qué hace |
|---|---|
| `_load_translator()` | Importa `translator.py` bajo demanda y cachea el resultado, incluido el error si falla. |
| `stop_active_translator()` | Apaga la cámara si quedó encendida. No hace nada si el traductor nunca se abrió. |
| `_screen_notice(page, title, message, detail)` | Pantalla genérica de aviso con título, mensaje y botón de volver. |
| `screen_scan(page)` | Ruta `/scan`: dibuja el traductor, o el aviso de paquetes que faltan. |
| `screen_coming_soon(page)` | Marcador para las secciones sin implementar. |
| `main(page)` | Arranca la app: base de datos, ventana, manejadores y primera pantalla. |
| `render_route(route)` | Única vía para cambiar de pantalla: apaga cámara, limpia y dibuja. |
| `route_change(e)` | Responde al evento de cambio de ruta del cliente. |
| `window_event(e)` | Cierra la ventana a mano (hace falta por `prevent_close`). |

### `database.py` — SQLite

| Función | Qué hace |
|---|---|
| `get_connection()` | Abre una conexión nueva, con filas accesibles por nombre. |
| `init_db()` | Crea la tabla `users` si no existe. Idempotente. |
| `_hash_password(password, salt)` | Hash PBKDF2-HMAC-SHA256, 100.000 iteraciones. |
| `_verify_password(...)` | Recifra con la sal guardada y compara. |
| `get_user_by_email(email)` | Busca por correo, normalizando a minúsculas. |
| `get_user_by_id(user_id)` | Busca por clave primaria. |
| `email_exists(email)` | Atajo para saber si un correo ya está registrado. |
| `create_user(name, email, password)` | Valida, cifra e inserta. Devuelve `(ok, mensaje, usuario)`. |
| `authenticate_user(email, password)` | Comprueba credenciales. Mismo formato de retorno. |
| `update_profile(user_id, name, avatar)` | Actualiza nombre y/o avatar. |

Convención: nada lanza excepciones por errores del usuario. Todo se devuelve
como `(ok, mensaje, usuario)` y la pantalla muestra `mensaje` tal cual.

### `session.py` — sesión en memoria

| Función | Qué hace |
|---|---|
| `set_current_user(user)` | Marca a un usuario como el activo. |
| `clear_current_user()` | Cierra sesión (no toca la base de datos). |
| `is_logged_in()` | True si hay alguien dentro. |

Se borra al cerrar la app; no persiste entre ejecuciones.

### `hand_detector.py` — MediaPipe

| Función | Qué hace |
|---|---|
| `crear_detector(model_path, ...)` | Crea el Hand Landmarker en modo VIDEO. |
| `detectar(detector, rgb_frame, ts)` | Procesa un frame. El timestamp debe crecer siempre. |
| `dibujar_manos(frame, result)` | Pinta el esqueleto sobre el frame. |
| `tiene_manos(result)` | True si se vio al menos una mano. |
| `extraer_coords_estaticas(result)` | Vector de 126 valores (solo forma de la mano). |
| `extraer_coords_dinamicas(result)` | Vector de 252 valores (forma + posición). El que usa el traductor. |

Las dos funciones de extracción devuelven siempre el mismo tamaño, con la mano
izquierda primero y la derecha después, rellenando con ceros la que falte.

### `screens/welcome_screen.py`

| Función | Qué hace |
|---|---|
| `_feature_card(icon, text)` | Una de las tres tarjetas de características. |
| `open_create_account(page)` | Navega a `/create-account`. |
| `screen_welcome(page)` | Dibuja la pantalla completa. |

### `screens/sign_up.py`

| Función | Qué hace |
|---|---|
| `go_back_home(page)` | Vuelve a `/`. |
| `screen_signup(page)` | Dibuja la pantalla completa. |
| `show_error(message)` | Muestra el error en rojo bajo el formulario. |
| `handle_signup(e)` | Comprueba que las contraseñas coincidan, crea la cuenta y va a `/profile`. |

El resto de validaciones las hace `database.create_user`.

### `screens/sign_in.py`

| Función | Qué hace |
|---|---|
| `go_back_home(page)` | Vuelve a `/`. |
| `screen_signin(page)` | Dibuja la pantalla completa. |
| `handle_login(e)` | Valida credenciales y entra al dashboard. |
| `social_slot(text, size)` | Botón cuadrado de red social (decorativo). |
| `go_to_signup(e)` | Navega a `/create-account`. |

Los botones de Google, Apple y Facebook no hacen nada: son maqueta.

### `screens/personalize_profile.py`

| Función | Qué hace |
|---|---|
| `screen_personalizeprofile(page)` | Dibuja la pantalla completa. |
| `build_avatar_content()` | Decide si en el círculo va la foto o el emoji. |
| `pick_photo(e)` | Abre el selector de archivos (asíncrono). |
| `close_setup(e)` | Cierra sin guardar y va al dashboard. |
| `style_avatar_button(container, is_selected)` | Pinta un emoji como elegido o normal. |
| `select_avatar(emoji)` | Fabrica el manejador de clic de cada emoji. |
| `save_and_continue(e)` | Guarda en base de datos y sesión, y va al dashboard. |

`select_avatar` devuelve una función en vez de ser el manejador directamente
porque los 20 botones se crean en un bucle: así cada uno se queda con su emoji.

### `screens/dashboard.py`

| Función | Qué hace |
|---|---|
| `screen_dashboard(page)` | Dibuja la pantalla completa. |
| `nav_button(icon, label, active, route)` | Botón del menú lateral. |
| `handle_logout(e)` | Cierra sesión y vuelve a `/`. |
| `stat_card(emoji, value, label)` | Tarjeta de estadística. |
| `simple_progress_bar(percent, color, height)` | Barra de progreso hecha a mano con dos contenedores. |
| `category_label(text)` | Título pequeño de categoría. |
| `topic_row(...)` | Fila de tema, formato horizontal. |
| `topic_row_stacked(...)` | Fila de tema, formato vertical y estrecho. |
| `module_card(...)` | Tarjeta grande de módulo. |

**Todas las cifras son maqueta**: racha de 3 días, 0/259 señas, 0 % en cada
tema. No hay nada que las calcule ni tabla donde guardarlas.

### `screens/translator.py`

| Función / clase | Qué hace |
|---|---|
| `compute_camera_screen_rect(page)` | Calcula dónde poner la ventana de vídeo de OpenCV. |
| `_get_model()` | Carga el modelo y su normalización una sola vez. |
| `SignLanguageTranslator` | Motor: cámara + detección + modelo, en un hilo aparte. |
| `.start()` / `.stop()` | Arranca el hilo / pide parar y espera a que termine. |
| `.is_running` / `.is_busy` | En marcha / en marcha o arrancando. |
| `.clear_text()` | Pide borrar el texto acumulado. |
| `._setup_and_run()` | Cuerpo del hilo: carga, abre cámara, ejecuta y limpia. |
| `._loop()` | Bucle principal, un frame por vuelta. |
| `._reposition_window()` | Recoloca la ventana de vídeo sobre el hueco de la interfaz. |
| `stop_active_translator()` | Apaga el traductor activo (lo llama `main.py`). |
| `screen_translator(page)` | Monta la pantalla y conecta los callbacks. |
| `toggle_camera(e)` | Interruptor del botón grande. |
| `set_idle_state()` / `set_loading_state()` / `set_active_state()` | Los tres estados visuales del botón. |
| `handle_text_change(texto)` | Refresca el texto reconocido. |
| `handle_prediction_change(seña, confianza)` | Refresca la seña actual y su confianza. |

### `screens/___.py`

No es una pantalla: es una utilidad que junta todo el código en
`todos_los_codigos.txt`. Nadie la importa. Su sitio natural sería una carpeta
`tools/`.

---

## 7. Base de datos

Un solo archivo, `main/signscan.db`, con una sola tabla:

| Columna | Tipo | Notas |
|---|---|---|
| `id` | INTEGER | Clave primaria autoincremental |
| `name` | TEXT | Nombre visible |
| `email` | TEXT | Único, siempre en minúsculas |
| `password_hash` | TEXT | PBKDF2-HMAC-SHA256 en hexadecimal |
| `salt` | TEXT | Sal aleatoria de 16 bytes, distinta por usuario |
| `avatar` | TEXT | Emoji del perfil |
| `created_at` | TEXT | Fecha de alta en ISO |

Las contraseñas nunca se guardan en texto plano y nunca se descifran: para
verificar se recifra lo que escribe el usuario con su misma sal.

`init_db()` **no hace migraciones**. Si se añade una columna, hay que escribir
el `ALTER TABLE`; a las bases de datos ya creadas no les aparece sola.

---

## 8. Cómo funciona el traductor

```
webcam ──> frame ──> MediaPipe ──> 252 valores ──┐
                                                 ├──> 504 por frame
                     frame anterior ──> delta ───┘
                                                 │
                              45 frames acumulados
                                                 │
                                normalizar (X_mean, X_std)
                                                 │
                                          modelo LSTM
                                                 │
                                       estabilización
                                                 │
                                        texto en pantalla
```

**Estabilización**: una predicción solo se acepta si supera el 70 % de
confianza, le saca al menos 0,15 de ventaja a la segunda opción y se repite
3 veces seguidas en el historial. Es lo que evita que el texto se llene de
palabras sueltas por un gesto a medio hacer.

**Espacios**: cuando pasan más de 2 segundos sin manos a la vista, se da la
palabra por terminada y se añade un espacio.

Todos estos números están reunidos y comentados al principio de
`translator.py` (`FRAMES_MODELO`, `UMBRAL_CONFIANZA`, `COOLDOWN`, etc.).
`FRAMES_MODELO` es el único que no se puede cambiar a la ligera: tiene que
coincidir con el valor usado al entrenar.

**Atajos de teclado** dentro de la ventana de vídeo:

| Tecla | Acción |
|---|---|
| `Q` o `ESC` | Cerrar la traducción |
| `R` | Recolocar la ventana sobre el hueco |
| Retroceso | Borrar el último carácter |
| `C` | Borrar todo el texto |

**Por qué el vídeo va en una ventana aparte**: Flet no tiene un control de
vídeo en vivo desde OpenCV, así que el vídeo se muestra en la ventana propia
de OpenCV, colocada encima del hueco azul de la interfaz. Los valores de
`# ---- Geometría estimada de la caja de la cámara ----` son los que calculan
esa posición: **si se cambia el diseño de la pantalla, hay que ajustarlos** o
el vídeo quedará descuadrado.

---

## 9. Limitaciones conocidas

Lo que hoy **no** hace, aunque lo parezca:

1. **Los datos del dashboard son maqueta.** Racha, señas aprendidas, nivel y
   todos los porcentajes están escritos a mano.
2. **La foto de perfil no se guarda.** `database.update_profile` no tiene
   columna para ella; solo vive en la sesión hasta cerrar la app. El nombre y
   el emoji sí se guardan.
3. **Los botones de redes sociales no hacen nada.** Google, Apple y Facebook
   son cuadros sin evento de clic.
4. **"Forgot your password?" no hace nada.** Es texto, no un botón.
5. **`/learn`, `/community` y `/video` no existen**: muestran un aviso.
6. **`hand_landmarker.task` no está en el repositorio.** Sin él, el traductor
   abre pero da error al activar la cámara.
7. **`page.go()` está en desuso** desde Flet 0.80 y desaparece en 0.90. Hay
   unas 15 llamadas en `screens/`. Funcionan hoy; migrarlas a `page.navigate()`
   es trabajo pendiente.
8. **Una sola sesión.** `session.py` es un diccionario global: sirve para una
   app de escritorio, pero no para varios usuarios simultáneos en modo web.

---

## 10. Errores frecuentes y qué significan

| Lo que se ve | Causa | Solución |
|---|---|---|
| `AttributeError: module 'flet' has no attribute 'run'` | Flet 0.28 instalado | `pip install -U "flet>=0.80"` |
| Ventana negra al arrancar | Enrutado: la primera pantalla no se dibujaba | Ya corregido; no volver a poner `page.go()` en el arranque |
| `No se encontró el modelo: hand_landmarker.task` | Falta el modelo de manos | Descargarlo en `main/` (sección 2) |
| `Could not open the camera` | Webcam ocupada o sin permisos | Cerrar la otra app que la use; revisar permisos de Windows |
| `Could not load the model` | Falta `modelo_lstm.keras` o TensorFlow | Comprobar los `.npy` y el `.keras` en `main/`; reinstalar requirements |
| La pantalla `/scan` muestra "The translator needs the camera and AI packages" | Falta OpenCV o MediaPipe | `pip install -r requirements.txt` |
| El vídeo aparece descuadrado | Cambió el diseño de la pantalla | Ajustar la geometría en `translator.py` o pulsar `R` |

---

## 11. Cómo comprobar que sigue funcionando

No hay tests automáticos en el repositorio todavía. La comprobación mínima
antes de dar por bueno un cambio en el enrutado o en las pantallas:

1. `python main.py` abre la bienvenida (no una ventana negra).
2. Crear una cuenta lleva a `/profile` y de ahí a `/dashboard`.
3. Cerrar sesión vuelve a la bienvenida.
4. Iniciar sesión con esa cuenta lleva al dashboard con el nombre correcto.
5. Los seis botones del menú lateral llevan a algún sitio (pantalla o aviso),
   nunca de vuelta a la bienvenida.
6. Entrar y salir de `/scan` no deja la webcam encendida.

El arreglo de la ventana negra se validó con una batería de 42 comprobaciones
automáticas sobre el cliente real de Flet (arranque, navegación entre las seis
pantallas, alta y login contra la base de datos, rutas del menú, ruta
inexistente, cierre de sesión y diez navegaciones seguidas comprobando que no
se acumulan controles). Ese banco de pruebas todavía no está en el
repositorio; convertirlo en algo ejecutable por cualquiera es trabajo
pendiente.
