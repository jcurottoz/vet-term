import streamlit as st

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="VET-TERM",
    page_icon="🐾",
    layout="centered"
)


# ==========================================
# ESTADO DEL JUEGO
# ==========================================

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "racha" not in st.session_state:
    st.session_state.racha = 0

if "pregunta" not in st.session_state:
    st.session_state.pregunta = 0

if "respondida" not in st.session_state:
    st.session_state.respondida = False


# ==========================================
# BANCO DE PREGUNTAS
# ==========================================

preguntas = [

    {
        "pregunta": "¿Cuál es el término anatómico correcto para referirse a la extremidad posterior de un animal?",

        "opciones": [
            "Pata trasera",
            "Miembro pélvico",
            "Extremidad trasera",
            "Pierna"
        ],

        "respuesta": "Miembro pélvico",

        "explicacion":
        "En anatomía veterinaria se utiliza el término "
        "'miembro pélvico' para referirse a la extremidad posterior."
    },


    {
        "pregunta":
        "¿Cuál es el término correcto para describir un aumento de la frecuencia respiratoria?",

        "opciones": [
            "Bradipnea",
            "Apnea",
            "Taquipnea",
            "Disnea"
        ],

        "respuesta": "Taquipnea",

        "explicacion":
        "La taquipnea corresponde al aumento de la frecuencia respiratoria."
    },


    {
        "pregunta":
        "¿Qué término describe la dificultad para respirar?",

        "opciones": [
            "Disnea",
            "Taquipnea",
            "Bradipnea",
            "Eupnea"
        ],

        "respuesta": "Disnea",

        "explicacion":
        "La disnea describe una respiración dificultosa o la sensación "
        "de dificultad respiratoria."
    }

]


# ==========================================
# FUNCIÓN: NIVEL
# ==========================================

def obtener_nivel(xp):

    if xp < 100:
        return "🐣 Aprendiz veterinario"

    elif xp < 300:
        return "🐾 Estudiante inicial"

    elif xp < 600:
        return "🩺 Estudiante clínico"

    elif xp < 1000:
        return "🔬 Estudiante avanzado"

    else:
        return "🧑‍⚕️ Veterinario en formación"


# ==========================================
# ENCABEZADO
# ==========================================

st.title("🐾 VET-TERM")

st.subheader(
    "Aprende terminología médico-veterinaria jugando"
)

st.write(
    "Entrena tu lenguaje técnico desde los primeros ciclos."
)


# ==========================================
# PANEL DE ESTADÍSTICAS
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "⭐ XP",
        st.session_state.xp
    )

with col2:
    st.metric(
        "🔥 Racha",
        st.session_state.racha
    )

with col3:
    st.metric(
        "🏆 Nivel",
        obtener_nivel(st.session_state.xp)
    )


st.divider()


# ==========================================
# JUEGO
# ==========================================

numero = st.session_state.pregunta

if numero < len(preguntas):

    pregunta_actual = preguntas[numero]


    # PROGRESO

    progreso = (numero + 1) / len(preguntas)

    st.progress(progreso)

    st.caption(
        f"Pregunta {numero + 1} de {len(preguntas)}"
    )


    # PREGUNTA

    st.header(
        pregunta_actual["pregunta"]
    )


    # RESPUESTAS

    respuesta = st.radio(
        "Selecciona una respuesta:",
        pregunta_actual["opciones"],
        key=f"respuesta_{numero}"
    )


    # BOTÓN

    if st.button(
        "✅ Comprobar respuesta",
        type="primary"
    ):

        if respuesta == pregunta_actual["respuesta"]:

            st.session_state.xp += 10

            st.session_state.racha += 1

            st.session_state.respondida = True

            st.success(
                "🎉 ¡Correcto! +10 XP"
            )

            st.info(
                "📚 " + pregunta_actual["explicacion"]
            )

        else:

            st.session_state.racha = 0

            st.session_state.respondida = True

            st.error(
                "❌ Respuesta incorrecta"
            )

            st.warning(
                "La respuesta correcta es: "
                + pregunta_actual["respuesta"]
            )

            st.info(
                "📚 " + pregunta_actual["explicacion"]
            )


    # SIGUIENTE

    if st.session_state.respondida:

        if st.button(
            "➡️ Siguiente pregunta"
        ):

            st.session_state.pregunta += 1

            st.session_state.respondida = False

            st.rerun()


# ==========================================
# FINAL
# ==========================================

else:

    st.balloons()

    st.success(
        "🎉 ¡Has terminado la sesión!"
    )

    st.header("Resultados")

    st.metric(
        "⭐ XP obtenida",
        st.session_state.xp
    )

    st.write(
        f"### 🏆 {obtener_nivel(st.session_state.xp)}"
    )


    if st.button(
        "🔄 Volver a jugar"
    ):

        st.session_state.xp = 0

        st.session_state.racha = 0

        st.session_state.pregunta = 0

        st.session_state.respondida = False

        st.rerun()
