# Documentación técnica de SignScan

Documento de referencia de la aplicación: cómo está montada, qué hace cada
archivo y cada función, cómo se ejecuta y qué falta por hacer.

El [README.md](README.md) explica el proyecto de cara al público (objetivo,
datasets, modelos). Este documento es para quien va a tocar el código.

---

## 1. Qué se ejecuta y desde dónde

El repositorio tiene varias carpetas y solo una es la aplicación:

| Carpeta | Qué es | ¿Se ejecuta? |
|---|---|---|
| `main/` | **La aplicación.** Interfaz, base de datos y traductor en vivo. | Sí: `python main.py` |
| `lstm/` | Módulo de captura y entrenamiento del modelo de señas dinámicas. | Sí, scripts sueltos |
| `static/` | Módulo de señas estáticas (Random Forest). | Sí, scripts sueltos |
| `signscan/` | Versión anterior de la app. | No, se conserva como histórico |

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

Versiones fijadas hoy en `main/requirements.txt`: flet 0.86.5, keras 3.15.1
(sin TensorFlow: Keras 3 va por su cuenta), mediapipe 1.0.1, numpy 2.5.2 y
opencv 4.11.

Para que el traductor funcione hace falta además el modelo de manos de
MediaPipe, que **no está en el repositorio**. Hay que descargarlo una vez
dentro de `main/`:

```
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
```

Si solo se quiere ver la interfaz (login, perfil, dashboard, comunidad), basta
con instalar `flet`: la pantalla `/scan` detecta que faltan los paquetes de
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
├── assets/
│   ├── logo.png            imágenes de la interfaz
│   └── avatars/            fotos de perfil que sube el usuario
└── screens/
    ├── welcome_screen.py       "/"                bienvenida
    ├── sign_up.py              "/create-account"  alta de cuenta
    ├── sign_in.py              "/login"           inicio de sesión
    ├── personalize_profile.py  "/profile"         perfil, avatar y foto
    ├── dashboard.py            "/dashboard"       pantalla principal
    ├── community.py            "/community"       muro de la comunidad
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
| `/profile` | `personalize_profile.screen_personalizeprofile` | Completa |
| `/dashboard` | `dashboard.screen_dashboard` | Interfaz completa, datos de maqueta |
| `/community` | `community.screen_community` | Funciona, pero nada se guarda |
| `/scan` | `translator.screen_translator` | Funcional, requiere modelo y webcam |
| `/learn`, `/video` | Aviso "Coming soon" | Sin implementar |
| Cualquier otra | Bienvenida | Reserva de seguridad |

Las rutas "Coming soon" están listadas a propósito. Antes caían en la pantalla
de bienvenida y parecía que la app cerraba la sesión sola.

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

**Foto de perfil** (cómo viaja por la app)

```
/profile ──elegir foto──> se copia a assets/avatars/user_<id>_<hash>.png
                                    │
                    ruta relativa ──┼──> columna `photo` en la BD
                                    └──> session.current_user["photo"]
                                                  │
                          session.get_avatar_control() ──> dashboard,
                                                           comunidad,
                                                           perfil
```

La foto se **copia** dentro de `assets/` en lugar de guardar la ruta original
del disco: Flet sirve las imágenes desde esa carpeta, y así sigue funcionando
aunque el usuario mueva o borre el archivo original.

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
| `_add_missing_columns(conn)` | Migración: añade a `users` las columnas que le falten. |
| `init_db()` | Crea la tabla si no existe y la migra si se quedó vieja. |
| `_hash_password(password, salt)` | Hash PBKDF2-HMAC-SHA256, 100.000 iteraciones. |
| `_verify_password(...)` | Recifra con la sal guardada y compara. |
| `get_user_by_email(email)` | Busca por correo, normalizando a minúsculas. |
| `get_user_by_id(user_id)` | Busca por clave primaria. |
| `email_exists(email)` | Atajo para saber si un correo ya está registrado. |
| `create_user(name, email, password)` | Valida, cifra e inserta. Devuelve `(ok, mensaje, usuario)`. |
| `authenticate_user(email, password)` | Comprueba credenciales. Mismo formato de retorno. |
| `update_profile(user_id, name, avatar, photo)` | Actualiza solo los campos que se pasen. |

Convención: nada lanza excepciones por errores del usuario. Todo se devuelve
como `(ok, mensaje, usuario)` y la pantalla muestra `mensaje` tal cual.

### `session.py` — sesión en memoria

| Función | Qué hace |
|---|---|
| `set_current_user(user)` | Marca a un usuario como el activo. |
| `clear_current_user()` | Cierra sesión (no toca la base de datos). |
| `is_logged_in()` | True si hay alguien dentro. |
| `get_avatar_control(size, container_size)` | Devuelve la foto o el emoji del usuario. |

`get_avatar_control()` es la única fuente de verdad del avatar: **ninguna
pantalla debe construir el avatar a mano**, o la foto dejará de aparecer en
algún sitio cuando alguien la cambie.

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
| `_feature_card(icon, text)` | Una de las tarjetas de características. |
| `open_create_account(page)` | Navega a `/create-account`. |
| `screen_welcome(page)` | Dibuja la pantalla completa. |

### `screens/sign_up.py`

| Función | Qué hace |
|---|---|
| `go_back_home(page)` | Vuelve a `/`. |
| `screen_signup(page)` | Dibuja la pantalla completa. |
| `show_error(message)` | Muestra el error bajo el formulario. |
| `handle_signup(e)` | Comprueba que las contraseñas coincidan, crea la cuenta y va a `/profile`. |

El resto de validaciones las hace `database.create_user`.

### `screens/sign_in.py`

| Función | Qué hace |
|---|---|
| `go_back_home(page)` | Vuelve a `/`. |
| `screen_signin(page)` | Dibuja la pantalla completa. |
| `handle_login(e)` | Valida credenciales y entra al dashboard. |
| `social_slot(text, size, color)` | Botón cuadrado de red social (decorativo). |
| `go_to_signup(e)` | Navega a `/create-account`. |

Los botones de Google, Apple y Facebook no hacen nada: son maqueta.

### `screens/personalize_profile.py`

| Función | Qué hace |
|---|---|
| `_section_divider()` | La línea gris que separa secciones. |
| `screen_personalizeprofile(page)` | Dibuja la pantalla completa. |
| `build_avatar_content()` | Decide si en el círculo va la foto o el emoji. |
| `pick_photo(e)` | Abre el selector, copia la imagen a `assets/avatars/` y la aplica. |
| `close_setup(e)` | Cierra sin guardar y va al dashboard. |
| `style_avatar_button(container, is_selected)` | Pinta un emoji como elegido o normal. |
| `select_avatar(emoji)` | Fabrica el manejador de clic de cada emoji. |
| `save_and_continue(e)` | Guarda en base de datos y sesión, y va al dashboard. |

`select_avatar` devuelve una función en vez de ser el manejador directamente
porque los botones se crean en un bucle: así cada uno se queda con su emoji.

### `screens/dashboard.py`

| Función | Qué hace |
|---|---|
| `screen_dashboard(page)` | Dibuja la pantalla completa. |
| `nav_button(icon, label, active, route)` | Botón del menú lateral. |
| `handle_logout(e)` | Cierra sesión y vuelve a `/`. |
| `stat_card(emoji, value, label, accent_color)` | Tarjeta de estadística. |
| `simple_progress_bar(percent, color, height)` | Barra de progreso hecha a mano con dos contenedores. |
| `category_label(text)` | Título pequeño de categoría. |
| `category_card(label, content)` | Envuelve una categoría en tarjeta blanca. |
| `topic_row(...)` | Fila de tema, formato horizontal. |
| `topic_row_stacked(...)` | Fila de tema, formato vertical y estrecho. |
| `module_card(...)` | Tarjeta grande de módulo. |

**Todas las cifras son maqueta**: racha, señas aprendidas, nivel y los
porcentajes de cada tema. No hay nada que las calcule ni tabla donde
guardarlas.

### `screens/community.py`

| Función | Qué hace |
|---|---|
| `screen_community(page)` | Dibuja la pantalla completa. |
| `nav_button(...)` | Botón del menú lateral (igual que el del dashboard). |
| `handle_logout(e)` | Cierra sesión y vuelve a `/`. |
| `handle_input_change(e)` | Contador de caracteres y activar/desactivar el botón Post. |
| `handle_post_click(e)` | Publica: mete la tarjeta arriba del muro y limpia la caja. |
| `_circle_avatar(...)` | Avatar redondo, de foto o de emoji. |
| `build_reply(...)` | Una respuesta dentro de una publicación. |
| `build_post_card(...)` | Una publicación entera, con sus "me gusta" y respuestas. |
| `toggle_like(e)` | Marca o desmarca el "me gusta" de esa publicación. |
| `send_reply(e)` | Añade una respuesta a esa publicación. |
| `toggle_reply_composer(e)` | Muestra u oculta el cuadro de responder. |

**Nada se guarda.** No hay tabla de publicaciones: todo vive en memoria y
desaparece al cambiar de pantalla. Las publicaciones de Maria, Carlos y Ana
están escritas a mano (`seed_posts`) para que el muro no se vea vacío.

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
| `photo` | TEXT | Ruta de la foto relativa a `assets/`, o NULL |
| `created_at` | TEXT | Fecha de alta en ISO |

Las contraseñas nunca se guardan en texto plano y nunca se descifran: para
verificar se recifra lo que escribe el usuario con su misma sal.

**Migraciones**: `CREATE TABLE IF NOT EXISTS` no toca una tabla que ya existe,
así que las columnas nuevas se añaden en `_add_missing_columns()`, que se
ejecuta en cada arranque y solo añade lo que falta. Al añadir una columna al
esquema hay que añadir ahí su `ALTER TABLE`, o las bases de datos existentes se
quedarán sin ella.

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
2. **La comunidad no guarda nada.** Publicaciones, "me gusta" y respuestas
   viven en memoria y desaparecen al cambiar de pantalla. No hay tabla ni
   usuarios reales detrás: las tres publicaciones iniciales son de ejemplo.
3. **Los botones de redes sociales no hacen nada.** Google, Apple y Facebook
   son cuadros sin evento de clic.
4. **"Forgot your password?" no hace nada.** Es texto, no un botón.
5. **`/learn` y `/video` no existen**: muestran un aviso.
6. **`hand_landmarker.task` no está en el repositorio.** Sin él, el traductor
   abre pero da error al activar la cámara.
7. **`page.go()` está en desuso** desde Flet 0.80 y desaparece en 0.90. Hay
   unas 20 llamadas en `screens/`. Funcionan hoy; migrarlas a `page.navigate()`
   es trabajo pendiente.
8. **Una sola sesión.** `session.py` es un diccionario global: sirve para una
   app de escritorio, pero no para varios usuarios simultáneos en modo web.
9. **Las fotos de perfil se acumulan.** Cada cambio de foto copia un archivo
   nuevo a `assets/avatars/` y nunca se borra el anterior.

---

## 10. Errores frecuentes y qué significan

| Lo que se ve | Causa | Solución |
|---|---|---|
| `AttributeError: module 'flet' has no attribute 'run'` | Flet 0.28 instalado | `pip install -U "flet>=0.80"` |
| Ventana negra al arrancar | Enrutado: la primera pantalla no se dibujaba | Ya corregido; no volver a poner `page.go()` en el arranque |
| `No se encontró el modelo: hand_landmarker.task` | Falta el modelo de manos | Descargarlo en `main/` (sección 2) |
| `Could not open the camera` | Webcam ocupada o sin permisos | Cerrar la otra app que la use; revisar permisos de Windows |
| `Could not load the model` | Falta `modelo_lstm.keras` o Keras | Comprobar los `.npy` y el `.keras` en `main/`; reinstalar requirements |
| La pantalla `/scan` muestra "The translator needs the camera and AI packages" | Falta OpenCV o MediaPipe | `pip install -r requirements.txt` |
| El vídeo aparece descuadrado | Cambió el diseño de la pantalla | Ajustar la geometría en `translator.py` o pulsar `R` |
| La foto de perfil no aparece en otra pantalla | Esa pantalla construye el avatar a mano | Usar `session.get_avatar_control()` |

---

## 11. Cómo comprobar que sigue funcionando

No hay tests automáticos en el repositorio todavía. La comprobación mínima
antes de dar por bueno un cambio en el enrutado o en las pantallas:

1. `python main.py` abre la bienvenida (no una ventana negra).
2. Crear una cuenta lleva a `/profile` y de ahí a `/dashboard`.
3. Poner una foto de perfil y comprobar que aparece también en el dashboard y
   en la comunidad.
4. Cerrar sesión vuelve a la bienvenida.
5. Iniciar sesión con esa cuenta lleva al dashboard con el nombre correcto.
6. Los botones del menú lateral llevan a algún sitio (pantalla o aviso), nunca
   de vuelta a la bienvenida.
7. Publicar en la comunidad, dar "me gusta" y responder.
8. Entrar y salir de `/scan` no deja la webcam encendida.

El arreglo de la ventana negra se validó con una batería de comprobaciones
automáticas sobre el cliente real de Flet (arranque, navegación entre
pantallas, alta y login contra la base de datos, rutas del menú, ruta
inexistente, cierre de sesión y diez navegaciones seguidas comprobando que no
se acumulan controles). Ese banco de pruebas todavía no está en el
repositorio; convertirlo en algo ejecutable por cualquiera es trabajo
pendiente.
