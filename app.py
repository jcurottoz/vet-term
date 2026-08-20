import streamlit as st
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
# BANCO DE PREGUNTAS
# =========================================================

BANCO_PREGUNTAS = [

    # -------------------------
    # CONOCE
    # -------------------------

    {
        "tipo": "CONOCE",
        "pregunta": "¿Cuál es el término anatómico correcto para referirse a la extremidad posterior?",
        "opciones": [
            "Pata trasera",
            "Miembro pélvico",
            "Extremidad trasera",
            "Pierna"
        ],
        "respuesta": "Miembro pélvico",
        "explicacion": "En anatomía veterinaria, el término 'miembro pélvico' se utiliza para referirse a la extremidad posterior."
    },

    {
        "tipo": "CONOCE",
        "pregunta": "¿Qué término describe un aumento de la frecuencia respiratoria?",
        "opciones": [
            "Bradipnea",
            "Apnea",
            "Taquipnea",
            "Eupnea"
        ],
        "respuesta": "Taquipnea",
        "explicacion": "La taquipnea corresponde a un aumento de la frecuencia respiratoria."
    },

    {
        "tipo": "CONOCE",
        "pregunta": "¿Qué término describe la dificultad para respirar?",
        "opciones": [
            "Disnea",
            "Taquipnea",
            "Bradipnea",
            "Eupnea"
        ],
        "respuesta": "Disnea",
        "explicacion": "La disnea describe una respiración dificultosa."
    },

    {
        "tipo": "CONOCE",
        "pregunta": "¿Qué término indica una disminución de la frecuencia respiratoria?",
        "opciones": [
            "Taquipnea",
            "Disnea",
            "Bradipnea",
            "Apnea"
        ],
        "respuesta": "Bradipnea",
        "explicacion": "La bradipnea corresponde a una disminución de la frecuencia respiratoria."
    },

    {
        "tipo": "CONOCE",
        "pregunta": "¿Qué término significa ausencia de respiración?",
        "opciones": [
            "Apnea",
            "Disnea",
            "Eupnea",
            "Ortopnea"
        ],
        "respuesta": "Apnea",
        "explicacion": "La apnea corresponde a la ausencia de respiración."
    },

    # -------------------------
    # IDENTIFICA
    # -------------------------

    {
        "tipo": "IDENTIFICA",
        "pregunta": "Un estudiante escribe en una historia clínica: 'El perro tiene una herida en la pata trasera'. ¿Qué término sería más apropiado?",
        "opciones": [
            "Miembro pélvico",
            "Brazo",
            "Pata posterior",
            "Extremidad trasera"
        ],
        "respuesta": "Miembro pélvico",
        "explicacion": "En una descripción anatómica formal se recomienda utilizar 'miembro pélvico' en lugar de expresiones coloquiales como 'pata trasera'."
    },

    {
        "tipo": "IDENTIFICA",
        "pregunta": "Un canino presenta una frecuencia respiratoria superior a la esperada para su condición. ¿Qué término describe el hallazgo?",
        "opciones": [
            "Bradipnea",
            "Taquipnea",
            "Apnea",
            "Eupnea"
        ],
        "respuesta": "Taquipnea",
        "explicacion": "El aumento de la frecuencia respiratoria se denomina taquipnea."
    },

    {
        "tipo": "IDENTIFICA",
        "pregunta": "El veterinario registra que el paciente presenta dificultad evidente durante la respiración. ¿Qué término debe utilizar?",
        "opciones": [
            "Eupnea",
            "Bradipnea",
            "Disnea",
            "Apnea"
        ],
        "respuesta": "Disnea",
        "explicacion": "La dificultad respiratoria se describe mediante el término disnea."
    },

    {
        "tipo": "IDENTIFICA",
        "pregunta": "¿Cuál de las siguientes expresiones utiliza una terminología anatómica más precisa?",
        "opciones": [
            "Pata delantera",
            "Brazo del perro",
            "Miembro torácico",
            "Pata anterior"
        ],
        "respuesta": "Miembro torácico",
        "explicacion": "En anatomía veterinaria, 'miembro torácico' es el término técnico apropiado."
    },

    # -------------------------
    # APLICA
    # -------------------------

    {
        "tipo": "APLICA",
        "pregunta": "Durante el examen clínico de un canino, el estudiante observa respiración dificultosa. ¿Cómo debería registrar este hallazgo?",
        "opciones": [
            "El perro respira mal",
            "Tiene problemas para respirar",
            "Presenta disnea",
            "Respira feo"
        ],
        "respuesta": "Presenta disnea",
        "explicacion": "En una historia clínica se debe utilizar terminología médica precisa. 'Disnea' describe la dificultad respiratoria."
    },

    {
        "tipo": "APLICA",
        "pregunta": "Un paciente presenta disminución de la frecuencia respiratoria. ¿Cuál sería la descripción técnica adecuada?",
        "opciones": [
            "Respira lento",
            "Presenta bradipnea",
            "Respira poquito",
            "Tiene respiración baja"
        ],
        "respuesta": "Presenta bradipnea",
        "explicacion": "La disminución de la frecuencia respiratoria se denomina bradipnea."
    },

    {
        "tipo": "APLICA",
        "pregunta": "En una ficha clínica se describe una lesión localizada en la extremidad anterior derecha. ¿Cuál es la expresión anatómica más precisa?",
        "opciones": [
            "Pata derecha",
            "Pata delantera derecha",
            "Miembro torácico derecho",
            "Brazo derecho"
        ],
        "respuesta": "Miembro torácico derecho",
        "explicacion": "El término anatómico correcto es 'miembro torácico derecho'."
    },

    {
        "tipo": "APLICA",
        "pregunta": "Un estudiante escribe: 'El animal tiene una pata trasera lastimada'. ¿Cuál sería una redacción técnicamente más apropiada?",
        "opciones": [
            "El animal tiene una pata fea",
            "Presenta lesión en el miembro pélvico",
            "Tiene lastimada la pata",
            "Tiene daño atrás"
        ],
        "respuesta": "Presenta lesión en el miembro pélvico",
        "explicacion": "La expresión permite describir la localización utilizando terminología anatómica veterinaria."
    }
]


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


def iniciar_sesion():

    preguntas_sesion = random.sample(
        BANCO_PREGUNTAS,
        min(10, len(BANCO_PREGUNTAS))
    )

    st.session_state.preguntas_sesion = preguntas_sesion
    st.session_state.pregunta_actual = 0
    st.session_state.xp = 0
    st.session_state.racha = 0
    st.session_state.correctas = 0
    st.session_state.respondida = False
    st.session_state.finalizado = False


# =========================================================
# INICIALIZAR ESTADO
# =========================================================

if "preguntas_sesion" not in st.session_state:
    iniciar_sesion()


# =========================================================
# ENCABEZADO
# =========================================================

st.title("🐾 VET-TERM")

st.subheader(
    "Aprende terminología médico-veterinaria jugando"
)

st.caption(
    "Entrena tu lenguaje técnico desde los primeros ciclos."
)


# =========================================================
# ESTADÍSTICAS
# =========================================================

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


# =========================================================
# JUEGO
# =========================================================

if not st.session_state.finalizado:

    numero = st.session_state.pregunta_actual

    total = len(st.session_state.preguntas_sesion)

    pregunta = st.session_state.preguntas_sesion[numero]

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

    # RESPUESTA

    respuesta = st.radio(
        "Selecciona una respuesta:",
        pregunta["opciones"],
        key=f"respuesta_{numero}",
        disabled=st.session_state.respondida
    )

    # =====================================================
    # COMPROBAR
    # =====================================================

    if not st.session_state.respondida:

        if st.button(
            "✅ Comprobar respuesta",
            type="primary"
        ):

            st.session_state.respondida = True

            if respuesta == pregunta["respuesta"]:

                st.session_state.xp += 10

                st.session_state.racha += 1

                st.session_state.correctas += 1

                st.success(
                    "🎉 ¡Correcto! +10 XP"
                )

            else:

                st.session_state.racha = 0

                st.error(
                    "❌ Respuesta incorrecta"
                )

            st.info(
                "📚 " + pregunta["explicacion"]
            )

            st.rerun()

    # =====================================================
    # RESULTADO
    # =====================================================

    else:

        # Mostrar resultado después del rerun

        if respuesta == pregunta["respuesta"]:

            st.success(
                "🎉 ¡Respuesta correcta! +10 XP"
            )

        else:

            st.error(
                f"❌ La respuesta correcta es: "
                f"**{pregunta['respuesta']}**"
            )

        st.info(
            "📚 " + pregunta["explicacion"]
        )

        st.divider()

        # SIGUIENTE

        if st.button(
            "➡️ Siguiente pregunta",
            type="primary"
        ):

            if numero + 1 >= total:

                st.session_state.finalizado = True

            else:

                st.session_state.pregunta_actual += 1
                st.session_state.respondida = False

            st.rerun()


# =========================================================
# FINAL DE LA SESIÓN
# =========================================================

else:

    st.balloons()

    st.title("🎉 ¡Sesión completada!")

    total = len(
        st.session_state.preguntas_sesion
    )

    correctas = st.session_state.correctas

    porcentaje = (
        correctas / total
    ) * 100

    st.subheader(
        "🏆 Resultados"
    )

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
        f"Tu nivel: **{obtener_nivel(st.session_state.xp)}**"
    )

    if porcentaje >= 90:

        st.write(
            "🏅 ¡Excelente dominio de la terminología!"
        )

    elif porcentaje >= 70:

        st.write(
            "👏 ¡Buen trabajo! Sigue practicando."
        )

    else:

        st.write(
            "📚 Necesitas seguir entrenando. "
            "La práctica te ayudará a mejorar."
        )

    st.divider()

    if st.button(
        "🔄 Nueva sesión",
        type="primary"
    ):

        iniciar_sesion()

        st.rerun()
