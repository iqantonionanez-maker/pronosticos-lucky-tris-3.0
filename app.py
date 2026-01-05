import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    layout="centered"
)

# ---------------- ESTILOS (ELEGANTE / AGENCIA) ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.block-container {
    padding-top: 1.5rem;
}
h1, h2, h3 {
    color: #f5c542;
}
.stat-box {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 12px;
}
.good { color: #00ff9d; }
.bad { color: #ff6b6b; }
.neutral { color: #f5c542; }
.small {
    font-size: 0.85rem;
    color: #cfcfcf;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO / TITULO ----------------
st.markdown("<h1 style='text-align:center'>🎲 Pronósticos Lucky</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center' class='small'>Análisis estadístico del TRIS (solo informativo)</p>", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS (FUNCIÓN CLAVE CORREGIDA) ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Normalizar dígitos correctamente (ESTO ARREGLA TODO)
    for col in ["R1", "R2", "R3", "R4", "R5"]:
        df[col] = df[col].fillna(0).astype(int).astype(str)

    df["NUMERO"] = df["R1"] + df["R2"] + df["R3"] + df["R4"] + df["R5"]
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    return df

df = cargar_datos()

st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- FUNCIONES DE APOYO ----------------
def obtener_parte(numero, modalidad):
    if modalidad == "Directa 5":
        return numero
    if modalidad == "Directa 4 final":
        return numero[-4:]
    if modalidad == "Directa 3 final":
        return numero[-3:]
    if modalidad == "Par final":
        return numero[-2:]
    if modalidad == "Par inicial":
        return numero[:2]
    if modalidad == "Número final":
        return numero[-1]
    if modalidad == "Número inicial":
        return numero[0]

def calcular_estado(conteo, promedio):
    if conteo >= promedio * 1.2:
        return "🔥 Número caliente", "good"
    elif conteo <= promedio * 0.8:
        return "❄️ Número frío", "bad"
    else:
        return "➖ Número promedio", "neutral"

# ---------------- INPUT USUARIO ----------------
st.markdown("## 🔍 Analizar número")

numero_usuario = st.text_input("Ingresa el número", max_chars=5)

modalidad = st.selectbox(
    "Selecciona la modalidad",
    [
        "Par final",
        "Par inicial",
        "Número final",
        "Número inicial",
        "Directa 3 final",
        "Directa 4 final",
        "Directa 5"
    ],
    index=0
)

# ---------------- ANALISIS ----------------
if numero_usuario.isdigit() and len(numero_usuario) <= 5:
    numero_usuario = numero_usuario.zfill(5)
    parte = obtener_parte(numero_usuario, modalidad)

    df["PARTE"] = df["NUMERO"].apply(lambda x: obtener_parte(x, modalidad))

    apariciones = df[df["PARTE"] == parte]
    conteo = len(apariciones)

    promedio = df["PARTE"].value_counts().mean()

    estado, color = calcular_estado(conteo, promedio)

    ultima_fecha = (
        apariciones["FECHA"].max().strftime("%d/%m/%Y")
        if conteo > 0 else "Nunca ha salido"
    )

    st.markdown("## 📊 Análisis estadístico")

    st.markdown(f"""
    <div class="stat-box">
        🎯 <b>Modalidad:</b> {modalidad}<br>
        🔎 <b>Número analizado:</b> {parte}<br><br>
        📈 <b>Apariciones históricas:</b> {conteo}<br>
        🗓 <b>Última aparición:</b> {ultima_fecha}<br><br>
        <span class="{color}"><b>{estado}</b></span><br>
        <span class="small">
        Caliente = ≥20% más apariciones que el promedio |
        Frío = ≥20% menos apariciones
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- NUMEROS SIMILARES ----------------
    st.markdown("### 🔄 Números similares")

    similares = []
    try:
        base = int(parte)
        for i in range(-2, 3):
            if i != 0:
                similares.append(str(base + i).zfill(len(parte)))
    except:
        pass

    for s in similares:
        c = len(df[df["PARTE"] == s])
        st.write(f"{s}: {c} apariciones")

# ---------------- AVISO LEGAL ----------------
st.markdown("""
---
⚠️ **Este análisis es únicamente estadístico e informativo.  
No garantiza premios ni resultados.**  
Las decisiones de juego son responsabilidad del usuario.
""")

st.markdown("<p style='text-align:center'>🍀 Pronósticos Lucky — suerte informada</p>", unsafe_allow_html=True)
