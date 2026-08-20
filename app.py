import streamlit as st
import pandas as pd
import random
from supabase import create_client
# =========================================================
# CONEXIÓN CON SUPABASE
# =========================================================

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="VET-TERM",
    page_icon="🐾",
    layout="wide"
)


# =========================================================
# CARGAR BANCO DE PREGUNTAS
# =========================================================

@st.cache_data
def cargar_preguntas():

    df = pd.read_csv(
        "data/preguntas.csv",
        sep="|",
        encoding="utf-8"
    )

    # Limpiar nombres de columnas
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # Limpiar textos
    columnas_texto = [
        "modulo",
        "categoria",
        "tipo",
        "termino",
        "pregunta",
        "opcion_a",
        "opcion_b",
        "opcion_c",
        "opcion_d",
        "respuesta",
        "explicacion",
        "dificultad"
    ]

    for columna in columnas_texto:

        if columna in df.columns:

            df[columna] = (
                df[columna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # Asegurar que nivel sea numérico
    df["nivel"] = pd.to_numeric(
        df["nivel"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["nivel"]
    )

    df["nivel"] = df["nivel"].astype(int)

    return df


preguntas = cargar_preguntas()


# =========================================================
# FUNCIONES GENERALES
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


# =========================================================
# ESTADO DEL TÉRMINO
# =========================================================

def obtener_estadistica_termino(termino):

    estadisticas = (
        st.session_state
        .estadisticas_terminos
    )

    if termino not in estadisticas:

        return {
            "intentos": 0,
            "aciertos": 0,
            "errores": 0
        }

    return estadisticas[termino]


# =========================================================
# PRECISIÓN DE UN TÉRMINO
# =========================================================
# =========================================================
# SUPABASE — ESTUDIANTE
# =========================================================

def obtener_o_crear_estudiante(nombre):

    nombre = nombre.strip()

    if not nombre:
        return None

    try:

        # Buscar estudiante existente
        resultado = (
            supabase
            .table("estudiantes")
            .select("*")
            .eq("nombre", nombre)
            .execute()
        )

        if resultado.data:

            estudiante = resultado.data[0]

            return estudiante

        # Si no existe, crear uno nuevo
        nuevo_estudiante = {

            "nombre": nombre,

            "xp": 0,

            "racha": 0,

            "nivel": 1,

            "preguntas_respondidas": 0,

            "respuestas_correctas": 0,

            "terminos_dominados": 0
        }

        resultado = (
            supabase
            .table("estudiantes")
            .insert(nuevo_estudiante)
            .execute()
        )

        if resultado.data:

            return resultado.data[0]

        return None

    except Exception as e:

        st.error(
            "No se pudo conectar con la base "
            "de datos: "
            + str(e)
        )

        return None
def porcentaje_termino(termino):

    datos = obtener_estadistica_termino(
        termino
    )

    intentos = datos["intentos"]

    aciertos = datos["aciertos"]

    if intentos == 0:
        return 0.0

    return (
        aciertos / intentos
    ) * 100


# =========================================================
# CLASIFICACIÓN DEL DOMINIO
# =========================================================

def dominio_termino(termino):

    datos = obtener_estadistica_termino(
        termino
    )

    intentos = datos["intentos"]

    porcentaje = porcentaje_termino(
        termino
    )

    # Todavía no ha sido evaluado
    if intentos == 0:

        return "⚪ Sin evaluar"

    # Un error debe detectarse inmediatamente
    if porcentaje < 60:

        return "🔴 Reforzar"

    # Entre 60 y 79 %
    if porcentaje < 80:

        return "🟡 En progreso"

    # 80 % o más
    return "🟢 Dominado"


# =========================================================
# REGISTRAR RESPUESTA
# =========================================================

# =========================================================
# REGISTRAR RESPUESTA Y GUARDAR PROGRESO
# =========================================================

def registrar_respuesta(
    termino,
    correcta
):

    # -----------------------------------------------------
    # ACTUALIZAR ESTADÍSTICAS LOCALES
    # -----------------------------------------------------

    estadisticas = (
        st.session_state
        .estadisticas_terminos
    )

    if termino not in estadisticas:

        estadisticas[termino] = {
            "intentos": 0,
            "aciertos": 0,
            "errores": 0
        }

    estadisticas[termino]["intentos"] += 1

    if correcta:

        estadisticas[termino]["aciertos"] += 1

    else:

        estadisticas[termino]["errores"] += 1


    # -----------------------------------------------------
    # COMPROBAR ESTUDIANTE
    # -----------------------------------------------------

    estudiante_id = (
        st.session_state.get(
            "estudiante_id"
        )
    )

    if not estudiante_id:

        return


    # -----------------------------------------------------
    # DATOS DEL TÉRMINO
    # -----------------------------------------------------

    datos = estadisticas[termino]

    intentos = datos["intentos"]
    aciertos = datos["aciertos"]
    errores = datos["errores"]

    dominio = (
        aciertos / intentos * 100
        if intentos > 0
        else 0
    )


    # -----------------------------------------------------
    # GUARDAR RESPUESTA INDIVIDUAL
    # -----------------------------------------------------

    try:

        supabase.table(
            "respuestas"
        ).insert({

            "estudiante_id": estudiante_id,

            "termino_id": termino,

            "nivel": st.session_state.get(
                "nivel_actual",
                1
            ),

            "tipo": None,

            "correcta": correcta,

            "xp_obtenido": (
                10 if correcta else 0
            )

        }).execute()
                # -------------------------------------------------
        # ACTUALIZAR XP ACUMULADO DEL ESTUDIANTE
        # -------------------------------------------------

        historial_xp = (
            supabase
            .table("respuestas")
            .select("xp_obtenido")
            .eq("estudiante_id", estudiante_id)
            .execute()
        )

        xp_acumulado = sum(
            fila.get("xp_obtenido", 0) or 0
            for fila in historial_xp.data
        )

        supabase.table(
            "estudiantes"
        ).update({
            "xp": xp_acumulado
        }).eq(
            "id",
            estudiante_id
        ).execute()

        # -------------------------------------------------
        # GUARDAR / ACTUALIZAR PROGRESO DEL TÉRMINO
        # -------------------------------------------------

        supabase.table(
            "progreso_terminos"
        ).upsert(

            {
                "estudiante_id": estudiante_id,

                "termino_id": termino,

                "correctas": aciertos,

                "incorrectas": errores,

                "dominio": dominio

            },

            on_conflict=(
                "estudiante_id,termino_id"
            )

        ).execute()


    except Exception as e:

        st.error(
            "No se pudo guardar el progreso "
            "en la base de datos: "
            + str(e)
        )


# =========================================================
# PESO ADAPTATIVO
# =========================================================

def calcular_peso_termino(termino):

    datos = obtener_estadistica_termino(
        termino
    )

    intentos = datos["intentos"]

    aciertos = datos["aciertos"]

    errores = datos["errores"]

    # -----------------------------------------------------
    # TÉRMINO NUEVO
    # -----------------------------------------------------

    if intentos == 0:

        return 3.0

    precision = (
        aciertos / intentos
    ) * 100

    # -----------------------------------------------------
    # TÉRMINO CON ERRORES
    # -----------------------------------------------------

    if precision < 40:

        return 10.0

    elif precision < 60:

        return 8.0

    elif precision < 80:

        return 5.0

    elif precision < 90:

        return 2.5

    else:

        return 1.0


# =========================================================
# SELECCIÓN ADAPTATIVA
# =========================================================

def seleccionar_preguntas_adaptativas(
    banco,
    cantidad=10
):

    banco = banco.copy()

    cantidad = min(
        cantidad,
        len(banco)
    )

    seleccionadas = []

    # -----------------------------------------------------
    # SELECCIONAR UNA POR UNA
    #
    # No utilizamos pandas.sample(weights=...)
    # para evitar el error que teníamos en Nivel 2.
    # -----------------------------------------------------

    while (
        len(seleccionadas) < cantidad
        and len(banco) > 0
    ):

        pesos = []

        for _, fila in banco.iterrows():

            termino = fila["termino"]

            peso = calcular_peso_termino(
                termino
            )

            # Pequeña variación aleatoria para
            # evitar que siempre aparezca exactamente
            # la misma secuencia.
            peso *= random.uniform(
                0.90,
                1.10
            )

            pesos.append(
                max(peso, 0.1)
            )

        indices = list(
            range(len(banco))
        )

        indice_elegido = random.choices(
            indices,
            weights=pesos,
            k=1
        )[0]

        fila_elegida = banco.iloc[
            indice_elegido
        ]

        seleccionadas.append(
            fila_elegida.to_dict()
        )

        # Eliminar pregunta para evitar
        # repetirla dentro de la misma sesión
        banco = banco.drop(
            banco.index[indice_elegido]
        )

        banco = banco.reset_index(
            drop=True
        )

    return seleccionadas


# =========================================================
# INICIAR SESIÓN
# =========================================================

def iniciar_sesion(nivel):

    banco = preguntas[
        preguntas["nivel"] == nivel
    ].copy()

    # -----------------------------------------------------
    # COMPROBAR PREGUNTAS
    # -----------------------------------------------------

    if banco.empty:

        st.error(
            f"No existen preguntas para el nivel {nivel}."
        )

        return False

    # -----------------------------------------------------
    # SELECCIÓN ADAPTATIVA
    # -----------------------------------------------------

    seleccion = (
        seleccionar_preguntas_adaptativas(
            banco,
            cantidad=10
        )
    )

    # -----------------------------------------------------
    # GUARDAR SESIÓN
    # -----------------------------------------------------

    st.session_state.preguntas_sesion = (
        seleccion
    )

    st.session_state.pregunta_actual = 0

    st.session_state.xp_sesion = 0

    st.session_state.racha = 0

    st.session_state.correctas_sesion = 0

    st.session_state.errores_sesion = 0

    st.session_state.respondida = False

    st.session_state.finalizado = False

    st.session_state.respuesta_actual = None

    st.session_state.nivel_actual = nivel

    return True


# =========================================================
# CONTAR TÉRMINOS DOMINADOS
# =========================================================

def contar_terminos_dominados():

    estadisticas = (
        st.session_state
        .estadisticas_terminos
    )

    total = 0

    for termino in estadisticas:

        if dominio_termino(
            termino
        ) == "🟢 Dominado":

            total += 1

    return total


# =========================================================
# CONTAR TÉRMINOS QUE NECESITAN REFUERZO
# =========================================================

def contar_terminos_refuerzo():

    estadisticas = (
        st.session_state
        .estadisticas_terminos
    )

    total = 0

    for termino in estadisticas:

        if dominio_termino(
            termino
        ) == "🔴 Reforzar":

            total += 1

    return total


# =========================================================
# INICIALIZAR SESSION STATE
# =========================================================

if "nombre_estudiante" not in st.session_state:

    st.session_state.nombre_estudiante = ""


if "estadisticas_terminos" not in st.session_state:

    st.session_state.estadisticas_terminos = {}


if "xp_total" not in st.session_state:

    st.session_state.xp_total = 0


if "xp_sesion" not in st.session_state:

    st.session_state.xp_sesion = 0


if "racha" not in st.session_state:

    st.session_state.racha = 0


if "racha_maxima" not in st.session_state:

    st.session_state.racha_maxima = 0


if "correctas_sesion" not in st.session_state:

    st.session_state.correctas_sesion = 0


if "errores_sesion" not in st.session_state:

    st.session_state.errores_sesion = 0


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


if "nivel_seleccionado" not in st.session_state:

    st.session_state.nivel_seleccionado = 1


# =========================================================
# CREAR PRIMERA SESIÓN
# =========================================================

if "preguntas_sesion" not in st.session_state:

    iniciar_sesion(1)


# =========================================================
# NOMBRES DE NIVELES
# =========================================================

nombres_niveles = {

    1: "🐣 Nivel 1 — Lenguaje veterinario básico",

    2: "🐾 Nivel 2 — Anatomía veterinaria",

    3: "🩺 Nivel 3 — Semiología"
}


# =========================================================
# MENÚ LATERAL
# =========================================================

with st.sidebar:

    st.title(
        "🐾 VET-TERM"
    )

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
            "👋 "
            + st.session_state.nombre_estudiante
        )

    st.metric(
        "⭐ XP",
        st.session_state.xp_total
    )

    st.metric(
        "🔥 Racha máxima",
        st.session_state.racha_maxima
    )

    st.metric(
        "🧠 Dominados",
        contar_terminos_dominados()
    )


# =========================================================
# 🏠 INICIO
# =========================================================

if pagina == "🏠 Inicio":

    st.title(
        "🐾 VET-TERM"
    )

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
        value=st.session_state.nombre_estudiante,
        key="nombre_input"
    )

    if nombre:

        nombre_limpio = nombre.strip()

        if nombre_limpio:

            estudiante = obtener_o_crear_estudiante(
                nombre_limpio
            )

            if estudiante:

                st.session_state.nombre_estudiante = (
                    estudiante["nombre"]
                )

                st.session_state.estudiante_id = (
                    estudiante["id"]
                )

                st.session_state.xp_total = (
                    estudiante["xp"]
                )

                st.session_state.racha_maxima = (
                    estudiante["racha"]
                )

                st.session_state.nivel_actual = (
                    estudiante["nivel"]
                )

                st.success(
                    "¡Bienvenido/a, "
                    + estudiante["nombre"]
                    + "! 🐾"
                )
    st.divider()

    # -----------------------------------------------------
    # MODALIDADES
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader(
            "🧠 CONOCE"
        )

        st.write(
            "Aprende términos y conceptos."
        )

    with col2:

        st.subheader(
            "🔎 IDENTIFICA"
        )

        st.write(
            "Reconoce la terminología correcta."
        )

    with col3:

        st.subheader(
            "🩺 APLICA"
        )

        st.write(
            "Utiliza los términos en "
            "situaciones clínicas."
        )

    st.divider()

    st.subheader(
        "🚀 Tu objetivo"
    )

    st.write(
        """
        VET-TERM no busca solamente que memorices
        palabras.

        El objetivo es que desarrolles progresivamente
        un lenguaje técnico médico-veterinario preciso.
        """
    )

    st.info(
        "👉 Selecciona 🎮 Jugar para comenzar."
    )


# =========================================================
# 🎮 JUGAR
# =========================================================

elif pagina == "🎮 Jugar":

    st.title(
        "🎮 Entrenamiento"
    )

    # -----------------------------------------------------
    # NOMBRE
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
    # SELECCIÓN DEL NIVEL
    # -----------------------------------------------------

    niveles_disponibles = sorted(
        preguntas["nivel"]
        .unique()
        .tolist()
    )

    nombres_disponibles = []

    for nivel in niveles_disponibles:

        if nivel in nombres_niveles:

            nombres_disponibles.append(
                nombres_niveles[nivel]
            )

    nivel_actual_nombre = nombres_niveles.get(
        st.session_state.nivel_seleccionado,
        nombres_disponibles[0]
    )

    indice_inicial = 0

    if nivel_actual_nombre in nombres_disponibles:

        indice_inicial = (
            nombres_disponibles.index(
                nivel_actual_nombre
            )
        )

    nivel_nombre = st.selectbox(
        "Selecciona tu nivel:",
        nombres_disponibles,
        index=indice_inicial,
        key="selector_nivel"
    )

    # -----------------------------------------------------
    # CONVERTIR NOMBRE A NÚMERO
    # -----------------------------------------------------

    nivel = None

    for numero, nombre_nivel in nombres_niveles.items():

        if nombre_nivel == nivel_nombre:

            nivel = numero

            break

    # Guardar nivel seleccionado
    st.session_state.nivel_seleccionado = nivel

    # -----------------------------------------------------
    # INFORMACIÓN DEL NIVEL
    # -----------------------------------------------------

    banco_nivel = preguntas[
        preguntas["nivel"] == nivel
    ]

    st.caption(
        f"📚 Este nivel contiene "
        f"{len(banco_nivel)} preguntas disponibles."
    )

    # -----------------------------------------------------
    # BOTÓN NUEVA SESIÓN
    # -----------------------------------------------------

    if st.button(
        "🎯 Nueva sesión",
        type="secondary"
    ):

        exito = iniciar_sesion(
            nivel
        )

        if exito:

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

        if total == 0:

            st.error(
                "No hay preguntas disponibles."
            )

            st.stop()

        if numero >= total:

            st.session_state.finalizado = True

            st.rerun()

        pregunta = (
            st.session_state
            .preguntas_sesion[numero]
        )

        # -------------------------------------------------
        # PROGRESO
        # -------------------------------------------------

        st.progress(
            (numero + 1) / total
        )

        st.caption(
            f"Pregunta {numero + 1} de {total}"
        )

        # -------------------------------------------------
        # TIPO
        # -------------------------------------------------

        tipo = pregunta["tipo"].upper()

        if tipo == "CONOCE":

            st.info(
                "🧠 CONOCE"
            )

        elif tipo == "IDENTIFICA":

            st.warning(
                "🔎 IDENTIFICA"
            )

        elif tipo == "APLICA":

            st.success(
                "🩺 APLICA"
            )

        else:

            st.info(
                "📚 ENTRENAMIENTO"
            )

        # -------------------------------------------------
        # TÉRMINO
        # -------------------------------------------------

        st.caption(
            "Término objetivo: "
            + pregunta["termino"]
        )

        # -------------------------------------------------
        # PREGUNTA
        # -------------------------------------------------

        st.header(
            pregunta["pregunta"]
        )

        opciones = [

            pregunta["opcion_a"],

            pregunta["opcion_b"],

            pregunta["opcion_c"],

            pregunta["opcion_d"]
        ]

        respuesta = st.radio(
            "Selecciona una respuesta:",
            opciones,
            key=f"respuesta_{numero}",
            disabled=st.session_state.respondida
        )

        # =================================================
        # COMPROBAR
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

                # -----------------------------------------
                # REGISTRAR
                # -----------------------------------------

                registrar_respuesta(
                    pregunta["termino"],
                    correcta
                )

                # -----------------------------------------
                # GUARDAR RESPUESTA
                # -----------------------------------------

                st.session_state.respuesta_actual = (
                    respuesta
                )

                st.session_state.respondida = True

                # -----------------------------------------
                # CORRECTA
                # -----------------------------------------

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
               
                # -----------------------------------------
                # INCORRECTA
                # -----------------------------------------

                else:

                    st.session_state.racha = 0

                    st.session_state.errores_sesion += 1

                st.rerun()

        # =================================================
        # RESULTADO
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
                    "**Respuesta correcta:** "
                    + pregunta["respuesta"]
                )

            # -------------------------------------------------
            # EXPLICACIÓN
            # -------------------------------------------------

            st.info(
                "📚 "
                + pregunta["explicacion"]
            )

            # -------------------------------------------------
            # ESTADO DEL TÉRMINO
            # -------------------------------------------------

            termino = pregunta["termino"]

            porcentaje = porcentaje_termino(
                termino
            )

            estado = dominio_termino(
                termino
            )

            datos = obtener_estadistica_termino(
                termino
            )

            st.write(
                "### 🧠 Estado del término"
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

            st.caption(
                f"Intentos: {datos['intentos']} | "
                f"Aciertos: {datos['aciertos']} | "
                f"Errores: {datos['errores']} | "
                f"Precisión: {porcentaje:.0f}%"
            )

            # -------------------------------------------------
            # MENSAJE ADAPTATIVO
            # -------------------------------------------------

            if estado == "🔴 Reforzar":

                st.warning(
                    "📚 Este término necesita "
                    "refuerzo. Volverá a aparecer "
                    "con mayor frecuencia."
                )

            elif estado == "🟡 En progreso":

                st.info(
                    "👍 Vas progresando. "
                    "Continúa practicando este término."
                )

            elif estado == "🟢 Dominado":

                st.success(
                    "🏆 ¡Término dominado!"
                )

            # -------------------------------------------------
            # INFORMACIÓN
            # -------------------------------------------------

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

                if (
                    numero + 1
                    >= total
                ):

                    st.session_state.finalizado = True

                else:

                    st.session_state.pregunta_actual += 1

                    st.session_state.respondida = False

                    st.session_state.respuesta_actual = None

                st.rerun()

    # =====================================================
    # SESIÓN TERMINADA
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

        errores = (
            st.session_state.errores_sesion
        )

        if total > 0:

            porcentaje = (
                correctas / total
            ) * 100

        else:

            porcentaje = 0

        # -------------------------------------------------
        # RESULTADOS
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "⭐ XP ganada",
                st.session_state.xp_sesion
            )

        with col2:

            st.metric(
                "✅ Correctas",
                correctas
            )

        with col3:

            st.metric(
                "❌ Errores",
                errores
            )

        with col4:

            st.metric(
                "📊 Rendimiento",
                f"{porcentaje:.0f}%"
            )

        st.divider()

        # -------------------------------------------------
        # INTERPRETACIÓN
        # -------------------------------------------------

        if porcentaje >= 90:

            st.success(
                "🏆 Excelente rendimiento. "
                "Tu dominio terminológico está "
                "avanzando muy bien."
            )

        elif porcentaje >= 70:

            st.info(
                "👏 Buen rendimiento. "
                "Continúa entrenando."
            )

        elif porcentaje >= 50:

            st.warning(
                "📚 Rendimiento intermedio. "
                "Hay términos que necesitan refuerzo."
            )

        else:

            st.error(
                "🔴 Necesitas reforzar varios "
                "conceptos. No te preocupes: "
                "VET-TERM los volverá a presentar."
            )

        st.divider()

        # -------------------------------------------------
        # PROGRESO GLOBAL
        # -------------------------------------------------

        st.subheader(
            "🏆 Tu progreso global"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "⭐ XP total",
                st.session_state.xp_total
            )

        with col2:

            st.metric(
                "🧠 Términos dominados",
                contar_terminos_dominados()
            )

        with col3:

            st.metric(
                "🔴 Para reforzar",
                contar_terminos_refuerzo()
            )

        st.success(
            obtener_nivel(
                st.session_state.xp_total
            )
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
        "Explora los conceptos disponibles "
        "en VET-TERM."
    )

    st.divider()

    # -----------------------------------------------------
    # FILTRO DE NIVEL
    # -----------------------------------------------------

    niveles = sorted(
        preguntas["nivel"]
        .unique()
        .tolist()
    )

    opciones_nivel = [
        "Todos"
    ]

    for nivel in niveles:

        if nivel in nombres_niveles:

            opciones_nivel.append(
                nombres_niveles[nivel]
            )

    filtro_nivel = st.selectbox(
        "🎯 Nivel:",
        opciones_nivel
    )

    if filtro_nivel == "Todos":

        banco = preguntas.copy()

    else:

        nivel_filtro = None

        for numero, nombre_nivel in nombres_niveles.items():

            if nombre_nivel == filtro_nivel:

                nivel_filtro = numero

        banco = preguntas[
            preguntas["nivel"] == nivel_filtro
        ].copy()

    # -----------------------------------------------------
    # FILTRO DE MÓDULO
    # -----------------------------------------------------

    modulos = [
        "Todos"
    ] + sorted(
        banco["modulo"]
        .unique()
        .tolist()
    )

    modulo = st.selectbox(
        "📚 Módulo:",
        modulos
    )

    if modulo != "Todos":

        banco = banco[
            banco["modulo"] == modulo
        ]

    # -----------------------------------------------------
    # LISTA DE TÉRMINOS
    # -----------------------------------------------------

    terminos = sorted(
        banco["termino"]
        .unique()
        .tolist()
    )

    st.caption(
        f"{len(terminos)} términos disponibles"
    )

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
                "**Categoría:** "
                + fila["categoria"]
            )

            st.write(
                "**Nivel:** "
                + str(fila["nivel"])
            )

            st.write(
                "**Tipo:** "
                + fila["tipo"]
            )

            st.write(
                "**Explicación:** "
                + fila["explicacion"]
            )

            # ---------------------------------------------
            # ESTADÍSTICA
            # ---------------------------------------------

            datos = obtener_estadistica_termino(
                termino
            )

            if datos["intentos"] > 0:

                porcentaje = porcentaje_termino(
                    termino
                )

                st.write(
                    "**Tu dominio:** "
                    + dominio_termino(
                        termino
                    )
                )

                st.progress(
                    porcentaje / 100
                )

                st.caption(
                    f"Intentos: {datos['intentos']} | "
                    f"Aciertos: {datos['aciertos']} | "
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

    if not st.session_state.nombre_estudiante:

        st.info(
            "Escribe primero tu nombre "
            "en Inicio."
        )

    else:

        st.subheader(
            "👤 "
            + st.session_state.nombre_estudiante
        )

        st.divider()

        # -------------------------------------------------
        # INDICADORES
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

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
                "🟢 Dominados",
                contar_terminos_dominados()
            )

        with col4:

            st.metric(
                "🔴 Reforzar",
                contar_terminos_refuerzo()
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
        # DOMINIO DE TÉRMINOS
        # -------------------------------------------------

        st.subheader(
            "🧠 Dominio de terminología"
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

                datos = estadisticas[
                    termino
                ]

                porcentaje = porcentaje_termino(
                    termino
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

                st.caption(
                    f"Intentos: {datos['intentos']} | "
                    f"Aciertos: {datos['aciertos']} | "
                    f"Errores: {datos['errores']} | "
                    f"Precisión: {porcentaje:.0f}%"
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

                porcentaje = porcentaje_termino(
                    termino
                )

                st.warning(
                    "📚 "
                    + termino
                    + " — "
                    + f"{porcentaje:.0f}% de precisión"
                )

        else:

            st.success(
                "🎉 No tienes términos "
                "pendientes de refuerzo."
            )

        st.divider()

        # -------------------------------------------------
        # INSIGNIAS
        # -------------------------------------------------

        st.subheader(
            "🏅 Insignias"
        )

        tiene_insignia = False

        if st.session_state.xp_total >= 10:

            st.success(
                "🐣 **Primer paso** — "
                "Completaste tu primera pregunta."
            )

            tiene_insignia = True

        if st.session_state.racha_maxima >= 5:

            st.success(
                "🔥 **Racha de 5** — "
                "Cinco respuestas correctas consecutivas."
            )

            tiene_insignia = True

        if contar_terminos_dominados() >= 5:

            st.success(
                "🧠 **Terminólogo inicial** — "
                "Dominaste 5 términos."
            )

            tiene_insignia = True

        if contar_terminos_dominados() >= 10:

            st.success(
                "🏆 **Terminólogo** — "
                "Dominaste 10 términos."
            )

            tiene_insignia = True

        if not tiene_insignia:

            st.caption(
                "🎯 Sigue jugando para desbloquear "
                "tus primeras insignias."
            )

        st.divider()

        # -------------------------------------------------
        # CÓMO FUNCIONA LA ADAPTACIÓN
        # -------------------------------------------------

        with st.expander(
            "🧠 ¿Cómo decide VET-TERM qué preguntarte?"
        ):

            st.write(
                """
                VET-TERM analiza tu desempeño en cada
                término.

                🔴 Los términos con baja precisión
                reciben mayor prioridad.

                🟡 Los términos en progreso continúan
                apareciendo para consolidar el aprendizaje.

                🟢 Los términos dominados aparecen con
                menor frecuencia.

                ⚪ Los términos nuevos reciben una
                prioridad intermedia para ampliar
                progresivamente tu vocabulario.

                De esta manera, las sesiones no son
                completamente aleatorias: se adaptan
                progresivamente al desempeño del estudiante.
                """
            )
