import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN VISUAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    layout="centered"
)

st.markdown("""
<style>
body {
    background-color: white;
}
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Construir número TRIS real
    df["NUMERO"] = (
        df["R1"].astype(str) +
        df["R2"].astype(str) +
        df["R3"].astype(str) +
        df["R4"].astype(str) +
        df["R5"].astype(str)
    )

    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df = df.sort_values("CONCURSO")

    return df

df = cargar_datos()

# ---------------- TÍTULO ----------------
st.markdown("<h1 style='text-align:center'>🎲 Pronósticos Lucky</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Análisis estadístico del TRIS (solo informativo)</p>", unsafe_allow_html=True)

st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- INPUTS ----------------
st.subheader("🔍 Analizar número")

numero_usuario = st.text_input("Ingresa el número", max_chars=5)

modalidad = st.selectbox(
    "Selecciona la modalidad",
    [
        "Par final",
        "Par inicial",
        "Número final",
        "Número inicial",
        "Directa 3",
        "Directa 4",
        "Directa 5"
    ],
    index=0
)

# ---------------- FUNCIONES ----------------
def extraer_parte(numero, modo):
    if modo == "Par final":
        return numero[-2:]
    if modo == "Par inicial":
        return numero[:2]
    if modo == "Número final":
        return numero[-1]
    if modo == "Número inicial":
        return numero[:1]
    if modo == "Directa 3":
        return numero[-3:]
    if modo == "Directa 4":
        return numero[-4:]
    return numero

def contar_apariciones(parte, modo):
    if modo == "Directa 5":
        return df[df["NUMERO"] == parte]

    return df[df["NUMERO"].str.endswith(parte)]

# ---------------- ANÁLISIS ----------------
if numero_usuario.isdigit() and len(numero_usuario) >= 1:

    parte = extraer_parte(numero_usuario, modalidad)
    resultados = contar_apariciones(parte, modalidad)

    st.subheader("📊 Análisis estadístico")

    st.write(f"**Número analizado:** {parte}")
    st.write(f"**Apariciones históricas:** {len(resultados)}")

    if len(resultados) > 0:
        ultima_fecha = resultados.iloc[-1]["FECHA"]
        st.write(f"**Última vez que salió:** {ultima_fecha.strftime('%d/%m/%Y')}")
    else:
        st.write("**Última vez que salió:** Nunca ha salido")

    # ---------------- CALIENTE / FRÍO ----------------
    promedio = len(df) / (100 if modalidad != "Directa 5" else len(df))
    estado = "⚪ Promedio"

    if len(resultados) >= promedio * 1.2:
        estado = "🔥 Número caliente — aparece ≥20% más que el promedio."
    elif len(resultados) <= promedio * 0.8:
        estado = "❄️ Número frío — aparece ≥20% menos que el promedio."

    st.markdown(f"**{estado}**")
    st.caption("Caliente = ≥20% más apariciones | Frío = ≥20% menos apariciones")

    # ---------------- NÚMEROS SIMILARES ----------------
    st.subheader("🔄 Números similares")

    similares = []
    base = int(parte)

    for i in range(-2, 3):
        n = base + i
        if n >= 0:
            similares.append(str(n).zfill(len(parte)))

    for n in similares:
        apar = df[df["NUMERO"].str.endswith(n)]
        if len(apar) > 0:
            fecha = apar.iloc[-1]["FECHA"].strftime("%d/%m/%Y")
        else:
            fecha = "Nunca ha salido"

        st.write(f"• {n} → {len(apar)} apariciones | Última vez: {fecha}")

    # ---------------- RECOMENDACIÓN LUCKY ----------------
    st.subheader("🍀 Recomendaciones Lucky")

    if len(resultados) == 0:
        st.info("Este número no ha salido antes. Puede considerarse exploratorio.")
    else:
        st.info("Número con historial estable. Jugar con moderación.")

# ---------------- DISCLAIMER ----------------
st.markdown("---")
st.caption(
    "⚠️ Este análisis es únicamente estadístico e informativo. "
    "No garantiza premios ni resultados."
)
st.markdown("🍀 **Pronósticos Lucky — suerte informada**")
