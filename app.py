import streamlit as st
import pandas as pd


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="VET-TERM",
    page_icon="🐾",
    layout="centered"
)


# =========================================================
# CARGAR BANCO DE PREGUNTAS
# =========================================================

@st.cache_data
def cargar_preguntas():

    datos = pd.read_csv(
        "data/preguntas.csv",
        sep="|",
        encoding="utf-8"
    )

    return datos


preguntas = cargar_preguntas()


# =========================================================
# FUNCIONES
# =========================================================

def obtener_nivel(xp):

    if xp < 50:
        return "🐣 Aprendiz veterinario"

    elif xp < 150:
        return "🐾 Estudiante inicial"

    elif xp < 300:
        return "🩺 Estudiante clínico"

    elif xp < 500:
        return "🔬 Estudiante avanzado"

    else:
        return "🧑‍⚕️ Veterinario en formación"


# ---------------------------------------------------------
# INICIAR SESIÓN DE JUEGO
# ---------------------------------------------------------

def iniciar_sesion(nivel):

    banco = preguntas[
        preguntas["nivel"] == nivel
    ].copy()

    if banco.empty:
        st.error(
            "No hay preguntas disponibles para este nivel."
        )
        return

    # -----------------------------------------------------
    # SELECCIÓN ADAPTATIVA
    # -----------------------------------------------------

    estadisticas = st.session_state.get(
        "estadisticas_terminos",
        {}
    )

    if estadisticas:

        def calcular_peso(fila):

            termino = fila["termino"]

            if termino not in estadisticas:
                return 5

            datos = estadisticas[termino]

            intentos = datos.get("intentos", 0)
            aciertos = datos.get("aciertos", 0)

            if intentos == 0:
                return 5

            precision = aciertos / intentos

            # Los términos con menor precisión
            # tienen mayor probabilidad de aparecer.
            peso = int(
                (1 - precision) * 10
            )

            return max(1, peso)

        pesos = banco.apply(
            calcular_peso,
            axis=1
        )

        seleccion = banco.sample(
            n=min(10, len(banco)),
            weights=pesos
        )

    else:

        seleccion = banco.sample(
            n=min(10, len(banco))
        )

    # -----------------------------------------------------
    # REINICIAR ESTADO DE LA SESIÓN
    # -----------------------------------------------------

    st.session_state.preguntas_sesion = (
        seleccion.to_dict("records")
    )

    st.session_state.pregunta_actual = 0

    st.session_state.xp_sesion = 0

    st.session_state.racha = 0

    st.session_state.correctas_sesion = 0

    st.session_state.respondida = False

    st.session_state.finalizado = False

    st.session_state.respuesta_actual = None

    st.session_state.nivel_actual = nivel


# ---------------------------------------------------------
# REGISTRAR RESPUESTA
# ---------------------------------------------------------

def registrar_respuesta(
    termino,
    correcta
):

    if "estadisticas_terminos" not in st.session_state:

        st.session_state.estadisticas_terminos = {}

    estadisticas = (
        st.session_state.estadisticas_terminos
    )

    if termino not in estadisticas:

        estadisticas[termino] = {
            "intentos": 0,
            "aciertos": 0
        }

    estadisticas[termino]["intentos"] += 1

    if correcta:

        estadisticas[termino]["aciertos"] += 1


# ---------------------------------------------------------
# PORCENTAJE DE DOMINIO
# ---------------------------------------------------------

def porcentaje_termino(termino):

    estadisticas = (
        st.session_state.get(
            "estadisticas_terminos",
            {}
        )
    )

    datos = estadisticas.get(
        termino,
        {
            "intentos": 0,
            "aciertos": 0
        }
    )

    intentos = datos.get(
        "intentos",
        0
    )

    aciertos = datos.get(
        "aciertos",
        0
    )

    if intentos == 0:
        return 0

    return (
        aciertos / intentos
    ) * 100


# ---------------------------------------------------------
# ESTADO DE DOMINIO
# ---------------------------------------------------------

def dominio_termino(termino):

    porcentaje = porcentaje_termino(
        termino
    )

    estadisticas = (
        st.session_state.get(
            "estadisticas_terminos",
            {}
        )
    )

    datos = estadisticas.get(
        termino,
        {}
    )

    intentos = datos.get(
        "intentos",
        0
    )

    if intentos < 2:

        return "⚪ Sin evaluar"

    elif porcentaje >= 80:

        return "🟢 Dominado"

    elif porcentaje >= 60:

        return "🟡 En progreso"

    else:

        return "🔴 Reforzar"


# ---------------------------------------------------------
# CONTAR TÉRMINOS DOMINADOS
# ---------------------------------------------------------

def contar_terminos_dominados():

    estadisticas = (
        st.session_state.get(
            "estadisticas_terminos",
            {}
        )
    )

    total = 0

    for termino in estadisticas:

        if (
            dominio_termino(termino)
            == "🟢 Dominado"
        ):

            total += 1

    return total


# =========================================================
# INICIALIZAR SESSION STATE
# =========================================================

# ---------------------------------------------------------
# DATOS DEL ESTUDIANTE
# ---------------------------------------------------------

if "nombre_estudiante" not in st.session_state:

    st.session_state.nombre_estudiante = ""


# ---------------------------------------------------------
# ESTADÍSTICAS DE TÉRMINOS
# ---------------------------------------------------------

if "estadisticas_terminos" not in st.session_state:

    st.session_state.estadisticas_terminos = {}


# ---------------------------------------------------------
# XP TOTAL
# ---------------------------------------------------------

if "xp_total" not in st.session_state:

    st.session_state.xp_total = 0


# ---------------------------------------------------------
# RACHA MÁXIMA
# ---------------------------------------------------------

if "racha_maxima" not in st.session_state:

    st.session_state.racha_maxima = 0


# ---------------------------------------------------------
# ESTADÍSTICAS DE SESIÓN
# ---------------------------------------------------------

if "xp_sesion" not in st.session_state:

    st.session_state.xp_sesion = 0


if "racha" not in st.session_state:

    st.session_state.racha = 0


if "correctas_sesion" not in st.session_state:

    st.session_state.correctas_sesion = 0


# ---------------------------------------------------------
# CONTROL DE PREGUNTAS
# ---------------------------------------------------------

if "pregunta_actual" not in st.session_state:

    st.session_state.pregunta_actual = 0


if "respondida" not in st.session_state:

    st.session_state.respondida = False


if "finalizado" not in st.session_state:

    st.session_state.finalizado = False


if "respuesta_actual" not in st.session_state:

    st.session_state.respuesta_actual = None


if "nivel_actual" not in st.session_state:

    st.session_state.nivel_actual = 1


# ---------------------------------------------------------
# CREAR PRIMERA SESIÓN
# ---------------------------------------------------------

if "preguntas_sesion" not in st.session_state:

    iniciar_sesion(1)


# =========================================================
# MENÚ LATERAL
# =========================================================

with st.sidebar:

    st.title("🐾 VET-TERM")

    st.caption(
        "Terminología médico-veterinaria"
    )

    st.divider()

    pagina = st.radio(
        "Navegación",
        [
            "🏠 Inicio",
            "🎮 Jugar",
            "📚 Banco de términos",
            "🏆 Mi progreso"
        ]
    )

    st.divider()

    # -----------------------------------------------------
    # ESTUDIANTE
    # -----------------------------------------------------

    if st.session_state.nombre_estudiante:

        st.write(
            "👋 "
            + st.session_state.nombre_estudiante
        )

    # -----------------------------------------------------
    # ESTADÍSTICAS
    # -----------------------------------------------------

    st.metric(
        "⭐ XP",
        st.session_state.xp_total
    )

    st.metric(
        "🔥 Racha máxima",
        st.session_state.racha_maxima
    )


# =========================================================
# 🏠 INICIO
# =========================================================

if pagina == "🏠 Inicio":

    st.title("🐾 VET-TERM")

    st.header(
        "Aprende terminología "
        "médico-veterinaria jugando"
    )

    st.write(
        "Entrena tu lenguaje técnico "
        "desde los primeros ciclos."
    )

    st.divider()

    # -----------------------------------------------------
    # NOMBRE DEL ESTUDIANTE
    # -----------------------------------------------------

    st.subheader(
        "👤 Antes de comenzar"
    )

    nombre = st.text_input(
        "Escribe tu nombre:",
        value=st.session_state.nombre_estudiante
    )

    if nombre:

        st.session_state.nombre_estudiante = nombre

        st.success(
            f"¡Bienvenido/a, {nombre}! 🐾"
        )

    st.divider()

    # -----------------------------------------------------
    # TRES MODALIDADES
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("🧠 CONOCE")

        st.write(
            "Aprende términos y conceptos."
        )

    with col2:

        st.subheader("🔎 IDENTIFICA")

        st.write(
            "Reconoce la terminología correcta."
        )

    with col3:

        st.subheader("🩺 APLICA")

        st.write(
            "Utiliza los términos "
            "en situaciones clínicas."
        )

    st.divider()

    st.subheader(
        "🚀 Tu objetivo"
    )

    st.write(
        """
        No se trata solamente de memorizar palabras.

        VET-TERM busca que aprendas a utilizar
        la terminología veterinaria de manera
        precisa y profesional.
        """
    )

    st.info(
        "👉 Selecciona '🎮 Jugar' para comenzar."
    )


# =========================================================
# 🎮 JUGAR
# =========================================================

elif pagina == "🎮 Jugar":

    st.title("🎮 Entrenamiento")

    # -----------------------------------------------------
    # VERIFICAR NOMBRE
    # -----------------------------------------------------

    if not st.session_state.nombre_estudiante:

        st.warning(
            "Primero escribe tu nombre "
            "en la página de Inicio."
        )

        st.stop()

    st.write(
        "👋 ¡Vamos, "
        + st.session_state.nombre_estudiante
        + "!"
    )

    # -----------------------------------------------------
    # SELECCIONAR NIVEL
    # -----------------------------------------------------

    niveles = sorted(
        preguntas["nivel"]
        .unique()
        .tolist()
    )

    nombres_niveles = {

        1: "🐣 Nivel 1 — Lenguaje veterinario básico",

        2: "🐾 Nivel 2 — Anatomía veterinaria",

        3: "🩺 Nivel 3 — Semiología"
    }

    opciones_nivel = []

    for nivel in niveles:

        if nivel in nombres_niveles:

            opciones_nivel.append(
                nombres_niveles[nivel]
            )

    nivel_nombre = st.selectbox(
        "Selecciona tu nivel:",
        opciones_nivel
    )

    # Obtener número del nivel
    nivel = None

    for numero_nivel, nombre_nivel in nombres_niveles.items():

        if nombre_nivel == nivel_nombre:

            nivel = numero_nivel
            break

    # -----------------------------------------------------
    # NUEVA SESIÓN
    # -----------------------------------------------------

    if st.button(
        "🎯 Nueva sesión",
        type="secondary"
    ):

        iniciar_sesion(nivel)

        st.rerun()

    st.divider()

    # =====================================================
    # JUEGO
    # =====================================================

    if not st.session_state.finalizado:

        numero = (
            st.session_state.pregunta_actual
        )

        total = len(
            st.session_state.preguntas_sesion
        )

        # -------------------------------------------------
        # SEGURIDAD
        # -------------------------------------------------

        if numero >= total:

            st.session_state.finalizado = True

            st.rerun()

        pregunta = (
            st.session_state
            .preguntas_sesion[numero]
        )

        # -------------------------------------------------
        # BARRA DE PROGRESO
        # -------------------------------------------------

        st.progress(
            (numero + 1) / total
        )

        st.caption(
            f"Pregunta {numero + 1} de {total}"
        )

        # -------------------------------------------------
        # TIPO DE PREGUNTA
        # -------------------------------------------------

        tipo = pregunta["tipo"]

        if tipo == "CONOCE":

            st.info(
                "🧠 CONOCE"
            )

        elif tipo == "IDENTIFICA":

            st.warning(
                "🔎 IDENTIFICA"
            )

        else:

            st.success(
                "🩺 APLICA"
            )

        # -------------------------------------------------
        # PREGUNTA
        # -------------------------------------------------

        st.header(
            pregunta["pregunta"]
        )

        opciones_respuesta = [

            pregunta["opcion_a"],

            pregunta["opcion_b"],

            pregunta["opcion_c"],

            pregunta["opcion_d"]
        ]

        respuesta = st.radio(
            "Selecciona una respuesta:",
            opciones_respuesta,
            key=f"respuesta_{numero}",
            disabled=st.session_state.respondida
        )

        # =================================================
        # COMPROBAR RESPUESTA
        # =================================================

        if not st.session_state.respondida:

            if st.button(
                "✅ Comprobar respuesta",
                type="primary"
            ):

                correcta = (
                    respuesta
                    == pregunta["respuesta"]
                )

                # Registrar término
                registrar_respuesta(
                    pregunta["termino"],
                    correcta
                )

                # Guardar respuesta
                st.session_state.respuesta_actual = (
                    respuesta
                )

                st.session_state.respondida = True

                # -----------------------------------------
                # RESPUESTA CORRECTA
                # -----------------------------------------

                if correcta:

                    st.session_state.xp_total += 10

                    st.session_state.xp_sesion += 10

                    st.session_state.racha += 1

                    st.session_state.correctas_sesion += 1

                    # Actualizar récord de racha

                    if (
                        st.session_state.racha
                        > st.session_state.racha_maxima
                    ):

                        st.session_state.racha_maxima = (
                            st.session_state.racha
                        )

                # -----------------------------------------
                # RESPUESTA INCORRECTA
                # -----------------------------------------

                else:

                    st.session_state.racha = 0

                st.rerun()

        # =================================================
        # MOSTRAR RESULTADO
        # =================================================

        else:

            correcta = (
                st.session_state.respuesta_actual
                == pregunta["respuesta"]
            )

            if correcta:

                st.success(
                    "🎉 ¡Correcto! +10 XP"
                )

            else:

                st.error(
                    "❌ Respuesta incorrecta"
                )

                st.write(
                    "Respuesta correcta: "
                    + "**"
                    + pregunta["respuesta"]
                    + "**"
                )

            # -------------------------------------------------
            # EXPLICACIÓN
            # -------------------------------------------------

            st.info(
                "📚 "
                + pregunta["explicacion"]
            )

            # -------------------------------------------------
            # DOMINIO DEL TÉRMINO
            # -------------------------------------------------

            porcentaje = porcentaje_termino(
                pregunta["termino"]
            )

            estado = dominio_termino(
                pregunta["termino"]
            )

            st.write(
                "🧠 **Dominio de "
                + pregunta["termino"]
                + ":** "
                + estado
            )

            st.progress(
                porcentaje / 100
            )

            st.caption(
                f"Precisión: {porcentaje:.0f}%"
            )

            st.caption(
                "📚 Módulo: "
                + pregunta["modulo"]
                + " | "
                + "🎯 Dificultad: "
                + pregunta["dificultad"]
            )

            st.divider()

            # -------------------------------------------------
            # SIGUIENTE
            # -------------------------------------------------

            if st.button(
                "➡️ Siguiente pregunta",
                type="primary"
            ):

                if numero + 1 >= total:

                    st.session_state.finalizado = True

                else:

                    st.session_state.pregunta_actual += 1

                    st.session_state.respondida = False

                    st.session_state.respuesta_actual = None

                st.rerun()

    # =====================================================
    # SESIÓN COMPLETADA
    # =====================================================

    else:

        st.balloons()

        st.title(
            "🎉 ¡Sesión completada!"
        )

        total = len(
            st.session_state.preguntas_sesion
        )

        correctas = (
            st.session_state.correctas_sesion
        )

        if total > 0:

            porcentaje = (
                correctas / total
            ) * 100

        else:

            porcentaje = 0

        # -------------------------------------------------
        # RESUMEN
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "⭐ XP ganada",
                st.session_state.xp_sesion
            )

        with col2:

            st.metric(
                "✅ Correctas",
                f"{correctas}/{total}"
            )

        with col3:

            st.metric(
                "📊 Rendimiento",
                f"{porcentaje:.0f}%"
            )

        st.divider()

        # -------------------------------------------------
        # NIVEL
        # -------------------------------------------------

        st.subheader(
            "🏆 Tu nivel"
        )

        st.success(
            obtener_nivel(
                st.session_state.xp_total
            )
        )

        # -------------------------------------------------
        # TÉRMINOS DOMINADOS
        # -------------------------------------------------

        dominados = (
            contar_terminos_dominados()
        )

        st.subheader(
            "🧠 Tu dominio"
        )

        st.write(
            f"Has dominado **{dominados} términos**."
        )

        # -------------------------------------------------
        # MENSAJE
        # -------------------------------------------------

        if porcentaje >= 90:

            st.success(
                "🏅 Excelente rendimiento. "
                "¡Tu dominio terminológico está avanzando!"
            )

        elif porcentaje >= 70:

            st.info(
                "👏 Buen rendimiento. "
                "Continúa entrenando."
            )

        else:

            st.warning(
                "📚 Algunos conceptos necesitan "
                "mayor refuerzo."
            )

        st.divider()

        # -------------------------------------------------
        # NUEVA SESIÓN
        # -------------------------------------------------

        if st.button(
            "🔄 Nueva sesión",
            type="primary"
        ):

            iniciar_sesion(
                st.session_state.nivel_actual
            )

            st.rerun()


# =========================================================
# 📚 BANCO DE TÉRMINOS
# =========================================================

elif pagina == "📚 Banco de términos":

    st.title(
        "📚 Banco de términos"
    )

    st.write(
        "Explora y revisa los conceptos "
        "incluidos en VET-TERM."
    )

    st.divider()

    # -----------------------------------------------------
    # FILTRO POR MÓDULO
    # -----------------------------------------------------

    modulos = [
        "Todos"
    ] + sorted(
        preguntas["modulo"]
        .unique()
        .tolist()
    )

    modulo = st.selectbox(
        "Filtrar por módulo:",
        modulos
    )

    if modulo == "Todos":

        banco = preguntas.copy()

    else:

        banco = preguntas[
            preguntas["modulo"] == modulo
        ].copy()

    # -----------------------------------------------------
    # TÉRMINOS ÚNICOS
    # -----------------------------------------------------

    terminos = sorted(
        banco["termino"]
        .unique()
        .tolist()
    )

    st.caption(
        f"{len(terminos)} términos disponibles"
    )

    # -----------------------------------------------------
    # MOSTRAR TÉRMINOS
    # -----------------------------------------------------

    for termino in terminos:

        fila = banco[
            banco["termino"] == termino
        ].iloc[0]

        with st.expander(
            "🐾 " + termino
        ):

            st.write(
                "**Módulo:** "
                + fila["modulo"]
            )

            st.write(
                "**Nivel:** "
                + str(fila["nivel"])
            )

            st.write(
                "**Categoría:** "
                + fila["categoria"]
            )

            st.write(
                "**Explicación:** "
                + fila["explicacion"]
            )

            # ---------------------------------------------
            # PROGRESO
            # ---------------------------------------------

            estadisticas = (
                st.session_state
                .estadisticas_terminos
            )

            if termino in estadisticas:

                st.write(
                    "**Dominio actual:** "
                    + dominio_termino(
                        termino
                    )
                )

                porcentaje = (
                    porcentaje_termino(
                        termino
                    )
                )

                st.progress(
                    porcentaje / 100
                )

                st.caption(
                    f"Precisión: {porcentaje:.0f}%"
                )

            else:

                st.caption(
                    "⚪ Todavía no has evaluado "
                    "este término."
                )


# =========================================================
# 🏆 MI PROGRESO
# =========================================================

elif pagina == "🏆 Mi progreso":

    st.title(
        "🏆 Mi progreso"
    )

    # -----------------------------------------------------
    # NOMBRE
    # -----------------------------------------------------

    if not st.session_state.nombre_estudiante:

        st.info(
            "Escribe primero tu nombre "
            "en la página de Inicio."
        )

    else:

        st.subheader(
            "👤 "
            + st.session_state.nombre_estudiante
        )

        # -------------------------------------------------
        # INDICADORES
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "⭐ XP",
                st.session_state.xp_total
            )

        with col2:

            st.metric(
                "🔥 Racha máxima",
                st.session_state.racha_maxima
            )

        with col3:

            st.metric(
                "🧠 Dominados",
                contar_terminos_dominados()
            )

        st.divider()

        # -------------------------------------------------
        # NIVEL
        # -------------------------------------------------

        st.subheader(
            "🎖️ Nivel actual"
        )

        st.success(
            obtener_nivel(
                st.session_state.xp_total
            )
        )

        st.divider()

        # -------------------------------------------------
        # DOMINIO POR TÉRMINO
        # -------------------------------------------------

        st.subheader(
            "📊 Dominio por término"
        )

        estadisticas = (
            st.session_state
            .estadisticas_terminos
        )

        if not estadisticas:

            st.info(
                "Todavía no tienes respuestas "
                "registradas."
            )

        else:

            for termino in sorted(
                estadisticas.keys()
            ):

                porcentaje = (
                    porcentaje_termino(
                        termino
                    )
                )

                estado = dominio_termino(
                    termino
                )

                st.write(
                    "**"
                    + termino
                    + "** — "
                    + estado
                )

                st.progress(
                    porcentaje / 100
                )

                datos = estadisticas[termino]

                st.caption(
                    f"Intentos: {datos['intentos']} | "
                    f"Aciertos: {datos['aciertos']} | "
                    f"Precisión: {porcentaje:.0f}%"
                )

        st.divider()

        # -------------------------------------------------
        # INSIGNIAS
        # -------------------------------------------------

        st.subheader(
            "🏅 Insignias"
        )

        insignia_obtenida = False

        # Primera pregunta

        if st.session_state.xp_total >= 10:

            st.success(
                "🐣 **Primer paso** — "
                "Completaste tu primera pregunta."
            )

            insignia_obtenida = True

        # Racha de 5

        if st.session_state.racha_maxima >= 5:

            st.success(
                "🔥 **Racha de 5** — "
                "Cinco respuestas correctas consecutivas."
            )

            insignia_obtenida = True

        # 10 términos dominados

        if contar_terminos_dominados() >= 10:

            st.success(
                "🧠 **Terminólogo** — "
                "Dominaste 10 términos."
            )

            insignia_obtenida = True

        if not insignia_obtenida:

            st.caption(
                "🎯 Sigue jugando para desbloquear "
                "tus primeras insignias."
            )

        st.divider()

        # -------------------------------------------------
        # TÉRMINOS PARA REFORZAR
        # -------------------------------------------------

        st.subheader(
            "🔴 Términos que necesitas reforzar"
        )

        terminos_refuerzo = []

        for termino in estadisticas:

            if (
                dominio_termino(termino)
                == "🔴 Reforzar"
            ):

                terminos_refuerzo.append(
                    termino
                )

        if terminos_refuerzo:

            for termino in sorted(
                terminos_refuerzo
            ):

                st.warning(
                    "📚 "
                    + termino
                    + " — "
                    + f"{porcentaje_termino(termino):.0f}% de precisión"
                )

        else:

            st.success(
                "🎉 No tienes términos "
                "pendientes de refuerzo."
            )
