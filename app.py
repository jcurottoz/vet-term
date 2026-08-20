import streamlit as st
import pandas as pd
import random


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

    return pd.read_csv(
        "data/preguntas.csv",
        sep="|",
        encoding="utf-8"
    )


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


def iniciar_sesion(nivel):

    banco = preguntas[
        preguntas["nivel"] == nivel
    ].copy()

    # -----------------------------------------------------
    # SELECCIÓN ADAPTATIVA
    # -----------------------------------------------------

    if (
        "estadisticas_terminos"
        in st.session_state
    ):

        estadisticas = (
            st.session_state
            .estadisticas_terminos
        )

        def peso_pregunta(fila):

            termino = fila["termino"]

            if termino not in estadisticas:
                return 5

            datos = estadisticas[termino]

            intentos = datos["intentos"]
            aciertos = datos["aciertos"]

            if intentos == 0:
                return 5

            precision = aciertos / intentos

            # Menor precisión = mayor probabilidad
            return max(
                1,
                int((1 - precision) * 10)
            )

        pesos = banco.apply(
            peso_pregunta,
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


def registrar_respuesta(
    termino,
    correcta
):

    estadisticas = (
        st.session_state
        .estadisticas_terminos
    )

    if termino not in estadisticas:

        estadisticas[termino] = {
            "intentos": 0,
            "aciertos": 0
        }

    estadisticas[termino]["intentos"] += 1

    if correcta:

        estadisticas[termino]["aciertos"] += 1


def porcentaje_termino(termino):

    datos = (
        st.session_state
        .estadisticas_terminos
        .get(
            termino,
            {
                "intentos": 0,
                "aciertos": 0
            }
        )
    )

    if datos["intentos"] == 0:

        return 0

    return (
        datos["aciertos"]
        / datos["intentos"]
    ) * 100


def dominio_termino(termino):

    porcentaje = porcentaje_termino(
        termino
    )

    intentos = (
        st.session_state
        .estadisticas_terminos
        .get(
            termino,
            {}
        )
        .get(
            "intentos",
            0
        )
    )

    if intentos < 2:

        return "⚪ Sin evaluar"

    if porcentaje >= 80:

        return "🟢 Dominado"

    elif porcentaje >= 60:

        return "🟡 En progreso"

    else:

        return "🔴 Reforzar"


def contar_terminos_dominados():

    total = 0

    for termino in (
        st.session_state
        .estadisticas_terminos
    ):

        if dominio_termino(termino) == "🟢 Dominado":

            total += 1

    return total


# =========================================================
# ESTADO INICIAL
# =========================================================

if "nombre_estudiante" not in st.session_state:

    st.session_state.nombre_estudiante = ""


if "estadisticas_terminos" not in st.session_state:

    st.session_state.estadisticas_terminos = {}


if "xp_total" not in st.session_state:

    st.session_state.xp_total = 0


if "racha_maxima" not in st.session_state:

    st.session_state.racha_maxima = 0


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

    if st.session_state.nombre_estudiante:

        st.write(
            f"👋 **{st.session_state.nombre_estudiante}**"
        )

    st.metric(
        "⭐ XP",
        st.session_state.xp_total
    )

    st.metric(
        "🔥 Racha máxima",
        st.session_state.racha_maxima
    )


# =========================================================
# INICIO
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
    # NOMBRE
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

    st.info(
        "👉 Ve a '🎮 Jugar' para comenzar."
    )


# =========================================================
# JUGAR
# =========================================================

elif pagina == "🎮 Jugar":

    st.title("🎮 Entrenamiento")

    if not st.session_state.nombre_estudiante:

        st.warning(
            "Primero escribe tu nombre "
            "en la página de Inicio."
        )

        st.stop()

    st.write(
        f"👋 ¡Vamos, "
        f"**{st.session_state.nombre_estudiante}**!"
    )

    # -----------------------------------------------------
    # NIVELES
    # -----------------------------------------------------

    niveles = sorted(
        preguntas["nivel"].unique()
    )

    nombres_niveles = {

        1: "🐣 Nivel 1 — Lenguaje veterinario básico",

        2: "🐾 Nivel 2 — Anatomía veterinaria",

        3: "🩺 Nivel 3 — Semiología"
    }

    opciones = [
        nombres_niveles[n]
        for n in niveles
    ]

    nivel_nombre = st.selectbox(
        "Selecciona tu nivel:",
        opciones
    )

    nivel = {
        valor: clave
        for clave, valor
        in nombres_niveles.items()
    }[nivel_nombre]

    if st.button(
        "🎯 Nueva sesión",
        type="secondary"
    ):

        iniciar_sesion(nivel)

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # JUEGO
    # -----------------------------------------------------

    if not st.session_state.finalizado:

        numero = (
            st.session_state.pregunta_actual
        )

        total = len(
            st.session_state.preguntas_sesion
        )

        pregunta = (
            st.session_state
            .preguntas_sesion[numero]
        )

        st.progress(
            (numero + 1) / total
        )

        st.caption(
            f"Pregunta {numero + 1} de {total}"
        )

        # TIPO

        tipo = pregunta["tipo"]

        if tipo == "CONOCE":

            st.info("🧠 CONOCE")

        elif tipo == "IDENTIFICA":

            st.warning("🔎 IDENTIFICA")

        else:

            st.success("🩺 APLICA")

        # PREGUNTA

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

        # -------------------------------------------------
        # COMPROBAR
        # -------------------------------------------------

        if not st.session_state.respondida:

            if st.button(
                "✅ Comprobar respuesta",
                type="primary"
            ):

                correcta = (
                    respuesta
                    == pregunta["respuesta"]
                )

                registrar_respuesta(
                    pregunta["termino"],
                    correcta
                )

                st.session_state.respuesta_actual = (
                    respuesta
                )

                st.session_state.respondida = True

                if correcta:

                    st.session_state.xp_total += 10

                    st.session_state.xp_sesion += 10

                    st.session_state.racha += 1

                    st.session_state.correctas_sesion += 1

                    if (
                        st.session_state.racha
                        > st.session_state.racha_maxima
                    ):

                        st.session_state.racha_maxima = (
                            st.session_state.racha
                        )

                else:

                    st.session_state.racha = 0

                st.rerun()

        # -------------------------------------------------
        # RESULTADO
        # -------------------------------------------------

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
                    f"Respuesta correcta: "
                    f"**{pregunta['respuesta']}**"
                )

            st.info(
                "📚 "
                + pregunta["explicacion"]
            )

            # DOMINIO

            porcentaje = porcentaje_termino(
                pregunta["termino"]
            )

            estado = dominio_termino(
                pregunta["termino"]
            )

            st.write(
                f"🧠 **Dominio de "
                f"{pregunta['termino']}:** "
                f"{estado}"
            )

            st.progress(
                porcentaje / 100
            )

            st.caption(
                f"Precisión: "
                f"{porcentaje:.0f}%"
            )

            st.divider()

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

    # -----------------------------------------------------
    # FINAL
    # -----------------------------------------------------

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

        porcentaje = (
            correctas / total
        ) * 100

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

        dominados = contar_terminos_dominados()

        st.subheader(
            "🧠 Tu dominio"
        )

        st.write(
            f"Has dominado "
            f"**{dominados} términos**."
        )

        if porcentaje >= 90:

            st.success(
                "🏅 Excelente rendimiento."
            )

        elif porcentaje >= 70:

            st.info(
                "👏 Buen rendimiento. "
                "Continúa entrenando."
            )

        else:

            st.warning(
                "📚 Hay conceptos que "
                "necesitan refuerzo."
            )

        if st.button(
            "🔄 Nueva sesión",
            type="primary"
        ):

            iniciar_sesion(nivel)

            st.rerun()


# =========================================================
# BANCO DE TÉRMINOS
# =========================================================

elif pagina == "📚 Banco de términos":

    st.title("📚 Banco de términos")

    st.write(
        "Explora y revisa los conceptos "
        "incluidos en VET-TERM."
    )

    modulo = st.selectbox(
        "Filtrar por módulo:",
        [
            "Todos"
        ]
        + sorted(
            preguntas["modulo"].unique()
        )
    )

    if modulo != "Todos":

        banco = preguntas[
            preguntas["modulo"] == modulo
        ]

    else:

        banco = preguntas

    terminos = banco["termino"].unique()

    for termino in terminos:

        fila = banco[
            banco["termino"] == termino
        ].iloc[0]

        with st.expander(
            f"🐾 {termino}"
        ):

            st.write(
                f"**Módulo:** "
                f"{fila['modulo']}"
            )

            st.write(
                f"**Nivel:** "
                f"{fila['nivel']}"
            )

            st.write(
                f"**Categoría:** "
                f"{fila['categoria']}"
            )

            st.write(
                f"**Explicación:** "
                f"{fila['explicacion']}"
            )

            if termino in (
                st.session_state
                .estadisticas_terminos
            ):

                st.write(
                    f"**Dominio actual:** "
                    f"{dominio_termino(termino)}"
                )

                st.progress(
                    porcentaje_termino(
                        termino
                    ) / 100
                )


# =========================================================
# MI PROGRESO
# =========================================================

elif pagina == "🏆 Mi progreso":

    st.title("🏆 Mi progreso")

    if not st.session_state.nombre_estudiante:

        st.info(
            "Escribe primero tu nombre "
            "en la página de Inicio."
        )

    else:

        st.subheader(
            f"👤 "
            f"{st.session_state.nombre_estudiante}"
        )

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

        st.subheader(
            "🎖️ Nivel actual"
        )

        st.success(
            obtener_nivel(
                st.session_state.xp_total
            )
        )

        st.divider()

        st.subheader(
            "📊 Dominio por término"
        )

        if not st.session_state.estadisticas_terminos:

            st.info(
                "Todavía no tienes suficientes "
                "respuestas registradas."
            )

        else:

            for termino in sorted(
                st.session_state
                .estadisticas_terminos
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
                    f"**{termino}** — {estado}"
                )

                st.progress(
                    porcentaje / 100
                )

                st.caption(
                    f"{porcentaje:.0f}% de precisión"
                )

        st.divider()

        st.subheader(
            "🏅 Insignias"
        )

        if st.session_state.xp_total >= 10:

            st.write(
                "🐣 **Primer paso** — "
                "Completaste tu primera pregunta."
            )

        if st.session_state.racha_maxima >= 5:

            st.write(
                "🔥 **Racha de 5** — "
                "Cinco respuestas correctas consecutivas."
            )

        if contar_terminos_dominados() >= 10:

            st.write(
                "🧠 **Terminólogo** — "
                "Dominaste 10 términos."
            )

        if (
            st.session_state.xp_total < 10
            and st.session_state.racha_maxima < 5
        ):

            st.caption(
                "Sigue jugando para desbloquear "
                "tus primeras insignias."
            )
