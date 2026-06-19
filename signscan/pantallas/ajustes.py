# pantallas/ajustes.py

import flet as ft

from componentes.colores import (
    AZUL,
    TURQUESA,
    AMARILLO,
    MORADO,
    ROJO,
    VERDE,
    BLANCO,
    FONDO_CLARO,
    GRIS_BORDE,
    TEXTO_GRIS,
    TEXTO_SUAVE,
)

from componentes.sidebar import estructura_app
from componentes.tarjetas import tarjeta_base
from componentes.botones import boton_secundario, boton_principal
from componentes.base_datos import (
    obtener_configuracion,
    actualizar_configuracion,
    guardar_historial,
)


def titulo_pantalla(nombre, subtitulo, ir):
    return ft.Column(
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    ft.TextButton(
                        "← Volver",
                        on_click=lambda e: ir("perfil"),
                        style=ft.ButtonStyle(color=AZUL),
                    ),
                    ft.Text(
                        nombre,
                        size=34,
                        color=AZUL,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
            ft.Text(
                subtitulo,
                size=17,
                color=TEXTO_GRIS,
            ),
        ],
    )


def fila_switch(icono, titulo, subtitulo, valor, accion):
    return ft.Container(
        bgcolor=BLANCO,
        border_radius=20,
        padding=20,
        border=ft.border.all(1, GRIS_BORDE),
        shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
        content=ft.Row(
            spacing=16,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    bgcolor="#F1F5F9",
                    border_radius=16,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(icono, size=24),
                ),
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(titulo, size=18, color=AZUL, weight=ft.FontWeight.BOLD),
                        ft.Text(subtitulo, size=13, color=TEXTO_GRIS),
                    ],
                ),
                ft.Switch(value=bool(valor), active_color=TURQUESA, on_change=accion),
            ],
        ),
    )


def opcion_selector(titulo, subtitulo, seleccionado, accion):
    return ft.Container(
        height=82,
        bgcolor=BLANCO,
        border_radius=18,
        padding=18,
        border=ft.border.all(2 if seleccionado else 1, TURQUESA if seleccionado else GRIS_BORDE),
        on_click=accion,
        content=ft.Row(
            spacing=15,
            controls=[
                ft.Container(
                    width=50,
                    height=50,
                    bgcolor="#F1F5F9",
                    border_radius=15,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("✓" if seleccionado else "", size=22, color=TURQUESA, weight=ft.FontWeight.BOLD),
                ),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(titulo, size=18, color=AZUL, weight=ft.FontWeight.BOLD),
                        ft.Text(subtitulo, size=13, color=TEXTO_GRIS),
                    ],
                ),
            ],
        ),
    )


def pantalla_notificaciones(page, ir, usuario, estado, mensaje):
    config = obtener_configuracion(usuario["correo"])

    def cambiar(campo, titulo):
        def accion(e):
            actualizar_configuracion(usuario["correo"], campo, 1 if e.control.value else 0)
            guardar_historial(usuario["correo"], "Configuración", f"Cambió {titulo}")
            mensaje("Preferencia actualizada.")
        return accion

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                titulo_pantalla("Notificaciones", "Gestiona alertas y recordatorios", ir),
                ft.Container(height=25),

                fila_switch(
                    "🔔",
                    "Notificaciones generales",
                    "Recibe avisos importantes de SignScan",
                    config["notificaciones"],
                    cambiar("notificaciones", "notificaciones generales"),
                ),

                ft.Container(height=14),

                fila_switch(
                    "📚",
                    "Recordatorios de aprendizaje",
                    "Te recordaremos practicar tus cursos",
                    config["notificaciones"],
                    cambiar("notificaciones", "recordatorios de aprendizaje"),
                ),

                ft.Container(height=14),

                fila_switch(
                    "👥",
                    "Actividad de comunidad",
                    "Avisos sobre likes, respuestas y publicaciones",
                    config["mensajes"],
                    cambiar("mensajes", "actividad de comunidad"),
                ),

                ft.Container(height=25),

                tarjeta_base(
                    padding=22,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("Vista previa", size=22, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=14),
                            ft.Container(
                                bgcolor="#F8FAFC",
                                border_radius=18,
                                padding=18,
                                content=ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Text("🔔", size=28),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text("Hora de practicar", size=17, color=AZUL, weight=ft.FontWeight.BOLD),
                                                ft.Text("Tienes una lección pendiente en SignScan", size=14, color=TEXTO_GRIS),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    return estructura_app("perfil", ir, usuario, contenido, FONDO_CLARO)


IDIOMAS = [
    ("PA", "Español (Panamá)", "Lengua de Señas Panameña"),
    ("ES", "Español", "LSE"),
    ("MX", "Español (México)", "LSM"),
    ("US", "English", "ASL"),
    ("BR", "Português", "Libras"),
]


def pantalla_idioma(page, ir, usuario, estado, mensaje):
    config = obtener_configuracion(usuario["correo"])

    def tarjeta_idioma(codigo, nombre, descripcion):
        seleccionado = config["idioma"] == nombre

        def seleccionar(e):
            actualizar_configuracion(usuario["correo"], "idioma", nombre)
            guardar_historial(usuario["correo"], "Configuración", f"Cambió idioma a {nombre}")
            mensaje(f"Idioma cambiado a {nombre}")
            ir("idioma")

        return ft.Container(
            height=82,
            bgcolor=BLANCO,
            border_radius=18,
            padding=18,
            border=ft.border.all(2 if seleccionado else 1, TURQUESA if seleccionado else GRIS_BORDE),
            on_click=seleccionar,
            content=ft.Row(
                spacing=16,
                controls=[
                    ft.Container(
                        width=52,
                        height=52,
                        bgcolor="#F1F5F9",
                        border_radius=16,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(codigo, size=16, color=AZUL, weight=ft.FontWeight.BOLD),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(nombre, size=18, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Text(descripcion, size=13, color=TEXTO_GRIS),
                        ],
                    ),
                    ft.Text("✓" if seleccionado else "", size=22, color=TURQUESA, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                titulo_pantalla("Idioma", "Selecciona el idioma principal", ir),
                ft.Container(height=25),
                *[
                    ft.Column(
                        controls=[
                            tarjeta_idioma(codigo, nombre, desc),
                            ft.Container(height=12),
                        ]
                    )
                    for codigo, nombre, desc in IDIOMAS
                ],
            ],
        ),
    )

    return estructura_app("perfil", ir, usuario, contenido, FONDO_CLARO)


def pantalla_apariencia(page, ir, usuario, estado, mensaje):
    config = obtener_configuracion(usuario["correo"])

    def seleccionar(campo, valor):
        def accion(e):
            actualizar_configuracion(usuario["correo"], campo, valor)
            guardar_historial(usuario["correo"], "Configuración", f"Cambió {campo} a {valor}")
            ir("apariencia")
        return accion

    def circulo_color(color):
        seleccionado = config["color_acento"] == color

        return ft.Container(
            width=52,
            height=52,
            bgcolor=color,
            border_radius=30,
            border=ft.border.all(4 if seleccionado else 2, AZUL if seleccionado else BLANCO),
            on_click=seleccionar("color_acento", color),
        )

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                titulo_pantalla("Apariencia", "Personaliza el estilo visual", ir),
                ft.Container(height=25),

                tarjeta_base(
                    padding=24,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("Tema", size=23, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=15),
                            opcion_selector("Claro", "Fondo claro y limpio", config["tema"] == "Claro", seleccionar("tema", "Claro")),
                            ft.Container(height=12),
                            opcion_selector("Oscuro", "Diseño oscuro para baja iluminación", config["tema"] == "Oscuro", seleccionar("tema", "Oscuro")),
                        ],
                    ),
                ),

                ft.Container(height=24),

                tarjeta_base(
                    padding=24,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("Color de acento", size=23, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=15),
                            ft.Row(
                                spacing=14,
                                controls=[
                                    circulo_color(TURQUESA),
                                    circulo_color(AZUL),
                                    circulo_color(AMARILLO),
                                    circulo_color(MORADO),
                                    circulo_color(ROJO),
                                    circulo_color(VERDE),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(height=24),

                tarjeta_base(
                    padding=24,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("Racha", size=23, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=15),
                            opcion_selector("🔥 Fuego Clásico", "Motivación diaria", config["racha"] == "🔥 Fuego Clásico", seleccionar("racha", "🔥 Fuego Clásico")),
                            ft.Container(height=12),
                            opcion_selector("⚡ Rayo", "Energía y velocidad", config["racha"] == "⚡ Rayo", seleccionar("racha", "⚡ Rayo")),
                            ft.Container(height=12),
                            opcion_selector("🚀 Cohete", "Progreso rápido", config["racha"] == "🚀 Cohete", seleccionar("racha", "🚀 Cohete")),
                        ],
                    ),
                ),

                ft.Container(height=24),

                tarjeta_base(
                    padding=24,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("Tamaño de fuente", size=23, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=15),
                            opcion_selector("Pequeño", "Texto compacto", config["tamano_fuente"] == "Pequeño", seleccionar("tamano_fuente", "Pequeño")),
                            ft.Container(height=12),
                            opcion_selector("Medio", "Tamaño recomendado", config["tamano_fuente"] == "Medio", seleccionar("tamano_fuente", "Medio")),
                            ft.Container(height=12),
                            opcion_selector("Grande", "Texto más accesible", config["tamano_fuente"] == "Grande", seleccionar("tamano_fuente", "Grande")),
                        ],
                    ),
                ),
            ],
        ),
    )

    return estructura_app("perfil", ir, usuario, contenido, FONDO_CLARO)


def pantalla_privacidad(page, ir, usuario, estado, mensaje):
    config = obtener_configuracion(usuario["correo"])

    def cambiar(campo, titulo):
        def accion(e):
            actualizar_configuracion(usuario["correo"], campo, 1 if e.control.value else 0)
            guardar_historial(usuario["correo"], "Privacidad", f"Cambió {titulo}")
            mensaje("Privacidad actualizada.")
        return accion

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                titulo_pantalla("Privacidad", "Controla tus permisos y seguridad", ir),
                ft.Container(height=25),

                fila_switch("👤", "Perfil público", "Permite que otros vean tu perfil", config["perfil_publico"], cambiar("perfil_publico", "perfil público")),
                ft.Container(height=14),
                fila_switch("💬", "Permitir mensajes", "Otros usuarios pueden contactarte", config["mensajes"], cambiar("mensajes", "mensajes")),
                ft.Container(height=14),
                fila_switch("📷", "Permiso de cámara", "Usar cámara para escanear señas", config["camara"], cambiar("camara", "cámara")),
                ft.Container(height=14),
                fila_switch("📍", "Compartir ubicación", "Conectar con usuarios cercanos", config["ubicacion"], cambiar("ubicacion", "ubicación")),

                ft.Container(height=25),

                tarjeta_base(
                    padding=24,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("Datos y seguridad", size=23, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=16),
                            boton_secundario("Descargar mis datos", lambda e: mensaje("Preparando descarga de datos..."), 360, 55),
                            ft.Container(height=12),
                            boton_principal("Eliminar cuenta", lambda e: mensaje("Acción protegida próximamente."), 360, 55, "#FFF1F2", ROJO),
                        ],
                    ),
                ),
            ],
        ),
    )

    return estructura_app("perfil", ir, usuario, contenido, FONDO_CLARO)


def pregunta_frecuente(pregunta, respuesta, page):
    abierto = {"valor": False}
    texto_respuesta = ft.Text("", size=14, color=TEXTO_GRIS)

    def alternar(e):
        abierto["valor"] = not abierto["valor"]
        texto_respuesta.value = respuesta if abierto["valor"] else ""
        page.update()

    return ft.Container(
        bgcolor=BLANCO,
        border_radius=18,
        padding=18,
        border=ft.border.all(1, GRIS_BORDE),
        on_click=alternar,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(pregunta, size=18, color=AZUL, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Text("⌄", size=22, color=TEXTO_SUAVE),
                    ],
                ),
                texto_respuesta,
            ],
        ),
    )


def pantalla_soporte(page, ir, usuario, estado, mensaje):
    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                titulo_pantalla("Ayuda y soporte", "Estamos aquí para ayudarte", ir),
                ft.Container(height=25),

                ft.Row(
                    spacing=18,
                    controls=[
                        tarjeta_base(ft.Column([ft.Text("💬", size=30), ft.Text("Chat en vivo", size=18, color=AZUL, weight=ft.FontWeight.BOLD), ft.Text("Habla con soporte", color=TEXTO_GRIS)]), alto=120),
                        tarjeta_base(ft.Column([ft.Text("📧", size=30), ft.Text("Correo", size=18, color=AZUL, weight=ft.FontWeight.BOLD), ft.Text("Envíanos un email", color=TEXTO_GRIS)]), alto=120),
                        tarjeta_base(ft.Column([ft.Text("📞", size=30), ft.Text("Teléfono", size=18, color=AZUL, weight=ft.FontWeight.BOLD), ft.Text("Línea de ayuda", color=TEXTO_GRIS)]), alto=120),
                    ],
                ),

                ft.Container(height=30),

                ft.Text("Preguntas frecuentes", size=24, color=AZUL, weight=ft.FontWeight.BOLD),
                ft.Container(height=15),

                pregunta_frecuente("¿Cómo funciona SignScan?", "SignScan ayuda a aprender, practicar y traducir señas con herramientas visuales e IA.", page),
                ft.Container(height=14),
                pregunta_frecuente("¿Mis avances se guardan?", "Sí. El progreso, historial y configuración se guardan en SQLite.", page),
                ft.Container(height=14),
                pregunta_frecuente("¿La cámara funciona?", "La pantalla está preparada para conectar el modelo de IA y cámara.", page),
            ],
        ),
    )

    return estructura_app("perfil", ir, usuario, contenido, FONDO_CLARO)