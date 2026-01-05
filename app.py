import streamlit as st
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🎲",
    layout="centered"
)

# ---------------- ESTILO LIMPIO ----------------
st.markdown("""
<style>
body { background-color: white; color: black; }
div[data-testid="stMetric"] {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
try:
    st.image("logo.png", width=140)
except:
    pass

st.markdown("<h2 style='text-align:center;'>🎲 Pronósticos Lucky</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Análisis estadístico del TRIS (solo informativo)</p>", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df.columns = [c.upper() for c in df.columns]

    # Detectar columna del número automáticamente
    posibles = ["NUMERO", "RESULTADO", "NUM", "GANADOR", "COMBINACION"]
    col_numero = None

    for c in posibles:
        if c in df.columns:
            col_numero = c
            break

    if col_numero is None:
        st.error("❌ No se encontró columna de números en el CSV")
        st.stop()

    df["NUMERO_BASE"] = df[col_numero].astype(str).str.zfill(5)

    # Fecha si existe
    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
    else:
        df["FECHA"] = pd.NaT

    return df

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- FUNCIONES ----------------
def extraer_parte(numero, modalidad):
    if modalidad == "Par final":
        return numero[-2:]
    if modalidad == "Par inicial":
        return numero[:2]
    if modalidad == "Número final":
        return numero[-1]
    if modalidad == "Número inicial":
        return numero[0]
    if modalidad == "Directa 3":
        return numero[-3:]
    if modalidad == "Directa 4":
        return numero[-4:]
    if modalidad == "Directa 5":
        return numero
    return numero

def analizar(df, valor, modalidad):
    serie = df["NUMERO_BASE"].apply(lambda x: extraer_parte(x, modalidad))
    conteo = serie.value_counts()

    apariciones = conteo.get(valor, 0)
    promedio = conteo.mean()

    fechas = df.loc[serie == valor, "FECHA"].dropna()
    ultima = fechas.iloc[-1] if len(fechas) > 0 else None

    if apariciones >= promedio * 1.2:
        estado = "🔥 Número caliente"
    elif apariciones <= promedio * 0.8:
        estado = "❄️ Número frío"
    else:
        estado = "⚖️ Número neutro"

    return apariciones, promedio, ultima, estado, conteo

# ---------------- INTERFAZ ----------------
st.markdown("### 🔍 Analizar número")

numero = st.text_input("Ingresa el número")
modalidad = st.selectbox(
    "Selecciona la modalidad",
    ["Par final", "Par inicial", "Número final", "Número inicial", "Directa 3", "Directa 4", "Directa 5"]
)

if numero:
    numero = numero.strip()

    apar, prom, ultima, estado, conteo = analizar(df, numero, modalidad)

    st.markdown("### 📊 Análisis estadístico")
    st.write(f"**Número analizado:** {numero}")
    st.write(f"**Apariciones históricas:** {apar}")

    if ultima is not None:
        st.write(f"**Última vez que salió:** {ultima.strftime('%d %B %Y')}")
    else:
        st.write("**Última vez que salió:** Nunca ha salido")

    st.write(estado)
    st.caption("Caliente = ≥20% más apariciones | Frío = ≥20% menos apariciones")

    # ---------------- SIMILARES ----------------
    st.markdown("### 🔄 Números similares")

    try:
        base = int(numero)
        similares = [base - 2, base - 1, base + 1, base + 2]
    except:
        similares = []

    for s in similares:
        s = str(s).zfill(len(numero))
        apar_s = conteo.get(s, 0)

        fechas_s = df.loc[
            df["NUMERO_BASE"].apply(lambda x: extraer_parte(x, modalidad)) == s,
            "FECHA"
        ].dropna()

        ult_s = fechas_s.iloc[-1].strftime('%d %B %Y') if len(fechas_s) > 0 else "Nunca ha salido"

        st.write(f"• {s} → {apar_s} apariciones | Última vez: {ult_s}")

    # ---------------- RECOMENDACIONES ----------------
    st.markdown("### 🍀 Recomendaciones Lucky")

    candidatos = conteo[(conteo > 0) & (conteo < prom)].sort_values().head(3)

    if len(candidatos) == 0:
        st.write("No se detectaron recomendaciones claras.")
    else:
        for n, v in candidatos.items():
            st.write(f"• {n} → {v} apariciones (debajo del promedio)")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("⚠️ Este análisis es únicamente estadístico e informativo. No garantiza premios ni resultados.")
st.markdown("🍀 **Pronósticos Lucky — suerte informada**")
