import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🎲",
    layout="centered"
)

# ---------------- ESTILOS (BLANCO Y LIMPIO) ----------------
st.markdown("""
<style>
body {
    background-color: white;
    color: black;
}
div[data-testid="stMetric"] {
    background-color: #f7f7f7;
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
try:
    st.image("logo.png", width=160)
except:
    pass

st.markdown("<h2 style='text-align:center;'>🎲 Pronósticos Lucky</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Análisis estadístico del TRIS (solo informativo)</p>", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Normalizar columnas
    df.columns = [c.upper() for c in df.columns]

    if "NUMERO" not in df.columns:
        raise ValueError("El archivo debe contener la columna NUMERO")

    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    df["NUMERO"] = df["NUMERO"].astype(str).str.zfill(5)

    return df

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- FUNCIONES ----------------
def obtener_parte(numero, modalidad):
    if modalidad == "Par final":
        return numero.zfill(2)[-2:]
    if modalidad == "Par inicial":
        return numero.zfill(2)[:2]
    if modalidad == "Número final":
        return numero[-1]
    if modalidad == "Número inicial":
        return numero[0]
    if modalidad == "Directa 3":
        return numero.zfill(3)[-3:]
    if modalidad == "Directa 4":
        return numero.zfill(4)[-4:]
    if modalidad == "Directa 5":
        return numero.zfill(5)[-5:]
    return numero

def analizar_numero(df, numero_usuario, modalidad):
    serie = df["NUMERO"].apply(lambda x: obtener_parte(x, modalidad))
    conteo = serie.value_counts()

    apariciones = conteo.get(numero_usuario, 0)

    fechas = None
    if "FECHA" in df.columns:
        fechas = df.loc[serie == numero_usuario, "FECHA"].dropna()

    ultima_fecha = fechas.iloc[-1] if fechas is not None and len(fechas) > 0 else None

    promedio = conteo.mean()

    if apariciones >= promedio * 1.2:
        estado = "🔥 Número caliente"
    elif apariciones <= promedio * 0.8:
        estado = "❄️ Número frío"
    else:
        estado = "⚖️ Número neutro"

    return apariciones, ultima_fecha, estado, conteo

# ---------------- INTERFAZ ----------------
st.markdown("### 🔍 Analizar número")

numero_input = st.text_input("Ingresa el número", value="")
modalidad = st.selectbox(
    "Selecciona la modalidad",
    ["Par final", "Par inicial", "Número final", "Número inicial", "Directa 3", "Directa 4", "Directa 5"]
)

if numero_input:
    numero_input = numero_input.strip()

    apariciones, ultima_fecha, estado, conteo = analizar_numero(
        df, numero_input, modalidad
    )

    st.markdown("### 📊 Análisis estadístico")

    st.write(f"**Número analizado:** {numero_input}")
    st.write(f"**Apariciones históricas:** {apariciones}")

    if ultima_fecha is not None:
        st.write(f"**Última vez que salió:** {ultima_fecha.strftime('%d %B %Y')}")
    else:
        st.write("**Última vez que salió:** Nunca ha salido")

    st.write(estado)
    st.caption("Caliente = ≥20% más apariciones | Frío = ≥20% menos apariciones")

    # ---------------- SIMILARES ----------------
    st.markdown("### 🔄 Números similares")

    try:
        base = int(numero_input)
        similares = [str(base - 2), str(base - 1), str(base + 1), str(base + 2)]
    except:
        similares = []

    for s in similares:
        apar = conteo.get(s, 0)
        fechas_s = df.loc[
            df["NUMERO"].apply(lambda x: obtener_parte(x, modalidad)) == s,
            "FECHA"
        ] if "FECHA" in df.columns else None

        if fechas_s is not None and not fechas_s.dropna().empty:
            ult = fechas_s.dropna().iloc[-1].strftime('%d %B %Y')
        else:
            ult = "Nunca ha salido"

        st.write(f"• {s} → {apar} apariciones | Última vez: {ult}")

    # ---------------- RECOMENDACIONES LUCKY ----------------
    st.markdown("### 🍀 Recomendaciones Lucky")

    promedio = conteo.mean()
    candidatos = conteo[
        (conteo > 0) &
        (conteo < promedio * 0.9)
    ].sort_values().head(3)

    if len(candidatos) == 0:
        st.write("No se detectaron recomendaciones claras.")
    else:
        for n, v in candidatos.items():
            st.write(f"• {n} → {v} apariciones (por debajo del promedio)")

# ---------------- DISCLAIMER ----------------
st.markdown("---")
st.caption("⚠️ Este análisis es únicamente estadístico e informativo. No garantiza premios ni resultados.")
st.markdown("🍀 **Pronósticos Lucky — suerte informada**")
