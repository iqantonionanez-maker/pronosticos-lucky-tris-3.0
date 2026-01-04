import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🍀",
    layout="centered"
)

# --------------------------------------------------
# LOGO Y ENCABEZADO
# --------------------------------------------------
st.image("logolucky.jpg", width=200)

st.markdown(
    "<h1 style='text-align:center;'>🎲 Pronósticos Lucky</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align:center;'>Análisis estadístico del TRIS</h4>",
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df.columns = df.columns.str.lower()

    # Ajusta si tus columnas tienen otros nombres
    df["numero"] = df["numero"].astype(str).str.zfill(5)
    df["fecha"] = pd.to_datetime(df["fecha"])

    return df

df = cargar_datos()

st.success(f"📊 Sorteos cargados: {len(df)}")

# --------------------------------------------------
# SECCIÓN DE ANÁLISIS
# --------------------------------------------------
st.subheader("🔍 Analizar número")

numero_usuario = st.text_input(
    "Ingresa el número que deseas analizar",
    max_chars=5
)

# --------------------------------------------------
# DETECCIÓN DE FORMA DE JUEGO
# --------------------------------------------------
forma_detectada = "Forma manual"

if numero_usuario.isdigit():
    if len(numero_usuario) == 5:
        forma_detectada = "Directa 5"
    elif len(numero_usuario) == 4:
        forma_detectada = "Directa 4 (últimos 4 números del ganador)"
    elif len(numero_usuario) == 3:
        forma_detectada = "Directa 3 (últimos 3 números del ganador)"
    elif len(numero_usuario) <= 2:
        forma_detectada = "Par / Número"

st.info(f"Forma de juego detectada: **{forma_detectada}**")

# --------------------------------------------------
# SELECCIÓN DE FORMA (PAR / NÚMERO)
# --------------------------------------------------
forma = None

if numero_usuario.isdigit() and len(numero_usuario) <= 2:
    forma = st.selectbox(
        "¿Cómo deseas analizar este número?",
        ["Par final", "Par inicial", "Número final", "Número inicial"],
        index=0,
        key="forma_juego"
    )

    st.caption("""
    **¿Qué significa cada forma?**
    - **Par final**: Coincide con los últimos 2 dígitos del número ganador  
    - **Par inicial**: Coincide con los primeros 2 dígitos  
    - **Número final**: Coincide con el último dígito  
    - **Número inicial**: Coincide con el primer dígito
    """)

# --------------------------------------------------
# DATOS DE LA JUGADA
# --------------------------------------------------
st.subheader("💰 Datos de la jugada")

monto = st.number_input(
    "Cantidad a jugar (pesos)",
    min_value=1,
    value=1
)

multiplicador = st.radio(
    "¿Jugar con multiplicador?",
    ["No", "Sí"],
    horizontal=True
)

factor = 1
if multiplicador == "Sí":
    factor = st.selectbox(
        "Selecciona multiplicador",
        [2, 3, 4]
    )

# --------------------------------------------------
# FUNCIÓN DE ANÁLISIS
# --------------------------------------------------
def analizar_numero(df, numero, forma):
    if forma == "Par final":
        coincidencias = df[df["numero"].str.endswith(numero)]
    elif forma == "Par inicial":
        coincidencias = df[df["numero"].str.startswith(numero)]
    elif forma == "Número final":
        coincidencias = df[df["numero"].str.endswith(numero[-1])]
    elif forma == "Número inicial":
        coincidencias = df[df["numero"].str.startswith(numero[0])]
    else:
        coincidencias = df[df["numero"] == numero]

    total = len(coincidencias)
    ultima = coincidencias["fecha"].max() if total > 0 else None
    return total, ultima

# --------------------------------------------------
# MOSTRAR RESULTADOS
# --------------------------------------------------
if numero_usuario.isdigit():

    apariciones, ultima_fecha = analizar_numero(df, numero_usuario, forma)

    st.subheader("📊 Análisis básico")

    st.write(f"**Apariciones históricas:** {apariciones}")

    if ultima_fecha:
        st.write(f"**Última aparición:** {ultima_fecha.date()}")
    else:
        st.write("**Última aparición:** Nunca ha salido")

    # --------------------------------------------------
    # INDICADOR HISTÓRICO (SEMÁFORO)
    # --------------------------------------------------
    promedio = df.shape[0] / 1000  # referencia simple

    st.subheader("🚦 Indicador histórico")

    if apariciones == 0:
        st.error("🔴 Frecuencia muy baja — No hay registros históricos.")
    elif apariciones < promedio:
        st.warning("🟡 Frecuencia baja — Ha salido menos que el promedio.")
    else:
        st.success("🟢 Frecuencia alta — Número activo históricamente.")

    st.caption("""
    **Semáforo estadístico**
    - 🔴 Bajo: Muy pocas apariciones  
    - 🟡 Medio: Dentro del rango normal  
    - 🟢 Alto: Número activo en historial
    """)

    # --------------------------------------------------
    # GANANCIA MÁXIMA (REFERENCIAL)
    # --------------------------------------------------
    st.subheader("💵 Ganancia máxima posible")

    premios = {
        "Directa 5": 50000,
        "Directa 4": 5000,
        "Directa 3": 500,
        "Par final": 50,
        "Par inicial": 50,
        "Número final": 5,
        "Número inicial": 5
    }

    premio_base = premios.get(forma_detectada, premios.get(forma, 0))
    ganancia = monto * premio_base * factor

    st.write(f"Ganancia máxima posible según reglas oficiales: **${ganancia:,.2f}**")

    # --------------------------------------------------
    # GRÁFICA SIMPLE
    # --------------------------------------------------
    st.subheader("📈 Tendencia visual")

    ultimos = df.tail(100)
    conteo = ultimos["numero"].value_counts().head(10)

    fig, ax = plt.subplots()
    conteo.plot(kind="bar", ax=ax)
    ax.set_title("Números más frecuentes (últimos 100 sorteos)")
    ax.set_ylabel("Apariciones")

    st.pyplot(fig)

# --------------------------------------------------
# CIERRE
# --------------------------------------------------
st.divider()
st.caption("Este análisis se basa en comportamiento estadístico histórico.")
st.markdown(
    "<h4 style='text-align:center;'>🍀 Pronósticos Lucky te desea buena suerte</h4>",
    unsafe_allow_html=True
)
