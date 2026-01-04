import streamlit as st
import pandas as pd

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🍀",
    layout="centered"
)

# =========================
# ESTILOS VISUALES (CASINO / SUERTE)
# =========================
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #1e1b3a, #0f1025);
    color: #ffffff;
}

.card {
    background: linear-gradient(135deg, #ffffff, #f3f3ff);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
    color: #ffd700;
    text-shadow: 0 0 10px rgba(255,215,0,0.6);
}

.subtitle {
    text-align: center;
    font-size: 16px;
    color: #dddddd;
}

.big-number {
    font-size: 34px;
    font-weight: bold;
    color: #27ae60;
}

.footer {
    text-align: center;
    font-size: 14px;
    color: #cccccc;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ENCABEZADO CON LOGO
# =========================
st.image("logolucky.jpg", width=240)

st.markdown("""
<div class="title">🎲 Pronósticos Lucky 🍀</div>
<div class="subtitle">
🧙‍♂️ Análisis estadístico del TRIS • Números • Tendencias • Suerte
</div>
""", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df["NUMERO"] = (
        df["R1"].astype(str)
        + df["R2"].astype(str)
        + df["R3"].astype(str)
        + df["R4"].astype(str)
        + df["R5"].astype(str)
    )
    return df

df = cargar_datos()

st.markdown(f"""
<div class="card">
    <div class="subtitle">📊 Sorteos analizados</div>
    <div class="big-number">{len(df):,}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# ENTRADA DE NÚMERO
# =========================
st.markdown("## 🔍 Analizar número")

numero_usuario = st.text_input(
    "Ingresa el número que deseas analizar",
    placeholder="Ej. 21, 569, 4583, 59862"
)

if numero_usuario:
    numero_usuario = numero_usuario.strip()

    if not numero_usuario.isdigit():
        st.error("❌ Solo se permiten números.")
        st.stop()

    longitud = len(numero_usuario)

    # =========================
    # FORMA DE JUEGO
    # =========================
    if longitud >= 3:
        forma_manual = f"Directa {longitud}"
        st.success(f"🎯 Forma detectada automáticamente: {forma_manual}")
        st.caption("En Directa 3 y 4 se consideran los últimos dígitos del número ganador.")
    else:
        forma_manual = st.selectbox(
            "¿Cómo deseas jugar este número?",
            ["Par inicial", "Par final", "Número inicial", "Número final"]
        )
        st.info(f"📌 Forma seleccionada: {forma_manual}")

    # =========================
    # DATOS DE JUGADA
    # =========================
    st.markdown("## 💰 Datos de la jugada")

    cantidad = st.number_input(
        "Cantidad a jugar (pesos)",
        min_value=1,
        value=1,
        step=1
    )

    usar_multiplicador = st.radio(
        "¿Jugar con multiplicador?",
        ["No", "Sí"]
    )

    multiplicador = 1
    if usar_multiplicador == "Sí":
        multiplicador = st.selectbox(
            "Selecciona multiplicador",
            [2, 3, 4, 5]
        )

    # =========================
    # FILTRO SEGÚN FORMA
    # =========================
    if longitud >= 3:
        filtro = df["NUMERO"].str.endswith(numero_usuario)
    else:
        if forma_manual == "Par final":
            filtro = (df["R4"].astype(str) + df["R5"].astype(str)) == numero_usuario
        elif forma_manual == "Par inicial":
            filtro = (df["R1"].astype(str) + df["R2"].astype(str)) == numero_usuario
        elif forma_manual == "Número final":
            filtro = df["R5"].astype(str) == numero_usuario
        elif forma_manual == "Número inicial":
            filtro = df["R1"].astype(str) == numero_usuario
        else:
            filtro = pd.Series([False] * len(df))

    total_apariciones = filtro.sum()
    ultima_fecha = df.loc[filtro, "FECHA"].max()

    # =========================
    # RESULTADOS
    # =========================
    st.markdown("## 📊 Resultados")

    st.markdown(f"""
    <div class="card">
        <div class="subtitle">🍀 Apariciones históricas</div>
        <div class="big-number">{total_apariciones}</div>
    </div>
    """, unsafe_allow_html=True)

    ultima_texto = "Nunca ha salido" if pd.isna(ultima_fecha) else ultima_fecha

    st.markdown(f"""
    <div class="card">
        <div class="subtitle">🗓 Última aparición</div>
        <div class="big-number">{ultima_texto}</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # SEMÁFORO ESTADÍSTICO
    # =========================
    st.markdown("## 🚦 Semáforo estadístico")

    promedio = len(df) / 100

    if total_apariciones < promedio * 0.5:
        st.error("🔴 Frecuencia baja — Ha salido muy pocas veces.")
    elif total_apariciones < promedio * 1.5:
        st.warning("🟡 Frecuencia media — Comportamiento normal.")
    else:
        st.success("🟢 Frecuencia alta — Número activo.")

    st.caption("""
    🔴 Bajo: pocas apariciones históricas  
    🟡 Medio: comportamiento normal  
    🟢 Alto: alta presencia en sorteos
    """)

    # =========================
    # GANANCIA MÁXIMA
    # =========================
    premios_oficiales = {
        "Directa 5": 50000,
        "Directa 4": 5000,
        "Directa 3": 500
    }

    premio_base = premios_oficiales.get(forma_manual, 0)
    ganancia_maxima = cantidad * premio_base * multiplicador

    st.markdown(f"""
    <div class="card">
        <div class="subtitle">💰 Ganancia máxima posible</div>
        <div class="big-number">${ganancia_maxima:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# PIE DE PÁGINA
# =========================
st.markdown("""
<div class="footer">
🎲 Este análisis se basa únicamente en comportamiento estadístico histórico.<br>
🧙‍♂️🍀 <b>Pronósticos Lucky te desea buena suerte</b> 🍀💰
</div>
""", unsafe_allow_html=True)
