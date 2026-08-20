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


def iniciar_sesion(nivel):

    banco = preguntas[
        preguntas["nivel"] == nivel
    ].copy()

    cantidad = min(10, len(banco))

    seleccion = banco.sample(
        n=cantidad
    ).to_dict("records")

    st.session_state.preguntas_sesion = seleccion
    st.session_state.pregunta_actual = 0
    st.session_state.xp = 0
    st.session_state.racha = 0
    st.session_state.correctas = 0
    st.session_state.respondida = False
    st.session_state.finalizado = False
    st.session_state.respuesta_actual = None


# =========================================================
# ESTADO INICIAL
# =========================================================

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

    st.metric(
        "⭐ XP",
        st.session_state.xp
    )

    st.metric(
        "🔥 Racha",
        st.session_state.racha
    )


# =========================================================
# PÁGINA INICIO
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

    st.subheader("🚀 Tu objetivo")

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
# PÁGINA JUGAR
# =========================================================

elif pagina == "🎮 Jugar":

    st.title("🎮 Entrenamiento")

    # -----------------------------------------------------
    # SELECCIÓN DE NIVEL
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

    # -----------------------------------------------------
    # NUEVA SESIÓN
    # -----------------------------------------------------

    if st.button(
        "🎯 Nueva sesión"
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

        # PROGRESO

        st.progress(
            (numero + 1) / total
        )

        st.caption(
            f"Pregunta {numero + 1} de {total}"
        )

        # TIPO DE PREGUNTA

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
        # COMPROBAR RESPUESTA
        # -------------------------------------------------

        if not st.session_state.respondida:

            if st.button(
                "✅ Comprobar respuesta",
                type="primary"
            ):

                st.session_state.respuesta_actual = (
                    respuesta
                )

                st.session_state.respondida = True

                if (
                    respuesta
                    == pregunta["respuesta"]
                ):

                    st.session_state.xp += 10

                    st.session_state.racha += 1

                    st.session_state.correctas += 1

                else:

                    st.session_state.racha = 0

                st.rerun()

        # -------------------------------------------------
        # RESULTADO
        # -------------------------------------------------

        else:

            respuesta_usuario = (
                st.session_state.respuesta_actual
            )

            if (
                respuesta_usuario
                == pregunta["respuesta"]
            ):

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

            st.caption(
                f"🏷️ Término: "
                f"{pregunta['termino']} "
                f"| 📚 Módulo: "
                f"{pregunta['modulo']} "
                f"| 🎯 Dificultad: "
                f"{pregunta['dificultad']}"
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
    # SESIÓN FINALIZADA
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
            st.session_state.correctas
        )

        porcentaje = (
            correctas / total
        ) * 100

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "⭐ XP",
                st.session_state.xp
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

        st.success(
            obtener_nivel(
                st.session_state.xp
            )
        )

        if porcentaje >= 90:

            st.write(
                "🏅 Excelente dominio."
            )

        elif porcentaje >= 70:

            st.write(
                "👏 Buen trabajo. "
                "Continúa practicando."
            )

        else:

            st.write(
                "📚 Necesitas reforzar "
                "algunos conceptos."
            )

        if st.button(
            "🔄 Nueva sesión",
            type="primary"
        ):

            iniciar_sesion(
                nivel
            )

            st.rerun()


# =========================================================
# BANCO DE TÉRMINOS
# =========================================================

elif pagina == "📚 Banco de términos":

    st.title("📚 Banco de términos")

    st.write(
        "Explora los conceptos incluidos "
        "en VET-TERM."
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

    for _, fila in banco.iterrows():

        with st.expander(
            f"🐾 {fila['termino']}"
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


# =========================================================
# PROGRESO
# =========================================================

elif pagina == "🏆 Mi progreso":

    st.title("🏆 Mi progreso")

    xp = st.session_state.xp

    st.subheader(
        obtener_nivel(xp)
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⭐ XP",
            xp
        )

    with col2:

        st.metric(
            "🔥 Racha",
            st.session_state.racha
        )

    with col3:

        st.metric(
            "✅ Correctas",
            st.session_state.correctas
        )

    st.divider()

    st.subheader(
        "🎯 Próximo nivel"
    )

    if xp < 50:

        st.write(
            f"Te faltan **{50 - xp} XP**."
        )

    elif xp < 150:

        st.write(
            f"Te faltan **{150 - xp} XP**."
        )

    elif xp < 300:

        st.write(
            f"Te faltan **{300 - xp} XP**."
        )

    elif xp < 500:

        st.write(
            f"Te faltan **{500 - xp} XP**."
        )

    else:

        st.success(
            "🏆 ¡Nivel máximo alcanzado!"
        )
