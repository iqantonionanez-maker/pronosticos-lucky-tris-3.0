import streamlit as st
import pandas as pd
from datetime import datetime

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Pronósticos Lucky TRIS",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0f0f1a;
}
.block-container {
    padding: 2rem;
}
h1, h2, h3, h4 {
    color: #f5c77a;
}
p, span, li {
    color: #e6e6e6;
}
.stTextInput input {
    background-color: #1b1b2f;
    color: white;
}
.stNumberInput input {
    background-color: #1b1b2f;
    color: white;
}
.stButton button {
    background-color: #f5c77a;
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    df["NUMERO"] = df["NUMERO"].astype(str).str.zfill(5)

    df["PAR_FINAL"] = df["NUMERO"].str[-2:]
    df["PAR_INICIAL"] = df["NUMERO"].str[:2]
    df["D3"] = df["NUMERO"].str[-3:]
    df["D4"] = df["NUMERO"].str[-4:]
    df["D5"] = df["NUMERO"]

    return df.sort_values("SORTEO")

df = cargar_datos()

# =========================
# PREMIOS OFICIALES
# =========================
PREMIOS = {
    "D5": 50000,
    "D4": 5000,
    "D3": 500,
    "PAR": 50,
    "NUM": 5
}

MULTIPLICADOR = 4

# =========================
# FUNCIONES CLAVE
# =========================
def estadistica(col, valor):
    data = df[df[col] == valor]
    if data.empty:
        return None

    ultimo = data.iloc[-1]
    sorteos_entre = data["SORTEO"].diff().mean()
    sin_salir = df["SORTEO"].max() - ultimo["SORTEO"]

    return {
        "ultimo_sorteo": int(ultimo["SORTEO"]),
        "fecha": ultimo["FECHA"].date(),
        "apariciones": len(data),
        "promedio": int(sorteos_entre) if not pd.isna(sorteos_entre) else None,
        "sin_salir": int(sin_salir)
    }

def top_modalidad(col, n=5):
    conteo = df[col].value_counts()
    promedio = conteo.mean()
    calientes = conteo[conteo > promedio].head(n)
    frios = conteo[conteo < promedio].tail(n)
    return calientes, frios

# =========================
# INTERFAZ
# =========================
st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS basado en historial real")

st.info(f"Sorteos cargados correctamente: {len(df)}")

numero = st.text_input("🔍 Ingresa tu número (1 a 5 dígitos)").strip()

apuesta = st.number_input("💰 Monto a apostar ($)", min_value=1, max_value=100, value=10)
usar_multiplicador = st.checkbox("Activar Tris Multiplicador")

# =========================
# ANÁLISIS PRINCIPAL
# =========================
if numero.isdigit() and 1 <= len(numero) <= 5:
    numero = numero.zfill(5)

    st.header("📊 Análisis de tu número")

    est = estadistica("D5", numero)

    if not est:
        st.warning(f"El número {numero} no tiene apariciones históricas registradas.")
    else:
        st.success(
            f"La última vez que salió fue en el sorteo {est['ultimo_sorteo']} "
            f"el día {est['fecha']}"
        )

        st.write(f"• Apariciones totales: {est['apariciones']}")
        st.write(f"• Promedio entre apariciones: {est['promedio']} sorteos")
        st.write(f"• Sorteos sin salir actualmente: {est['sin_salir']}")

    # =========================
    # RECOMENDACIONES RELACIONADAS
    # =========================
    st.header("🔍 Recomendaciones relacionadas")

    for label, col, val in [
        ("Par Final", "PAR_FINAL", numero[-2:]),
        ("Par Inicial", "PAR_INICIAL", numero[:2]),
        ("Directa 3", "D3", numero[-3:]),
        ("Directa 4", "D4", numero[-4:])
    ]:
        e = estadistica(col, val)
        if e:
            st.write(
                f"• {label} {val} → "
                f"{e['sin_salir']} sorteos sin salir | "
                f"Última vez: {e['fecha']}"
            )
        else:
            st.write(f"• {label} {val} → Sin historial")

    # =========================
    # TOPS
    # =========================
    st.header("🔥❄️ Tops por modalidad")

    for titulo, col in [
        ("Par Final", "PAR_FINAL"),
        ("Directa 3", "D3"),
        ("Directa 4", "D4"),
        ("Directa 5", "D5")
    ]:
        hot, cold = top_modalidad(col)
        st.subheader(titulo)
        st.write("🔥 Calientes:", ", ".join(hot.index))
        st.write("❄️ Fríos:", ", ".join(cold.index))

    # =========================
    # RECOMENDACIÓN LUCKY
    # =========================
    st.header("🍀 Recomendación Lucky")

    base = PREMIOS["PAR"] * apuesta
    multi = base * MULTIPLICADOR if usar_multiplicador else base

    st.markdown(f"""
**🟢 Conservadora**
- Par Final {numero[-2:]}
- Premio estimado: ${base:,}
- Con multiplicador: ${multi:,}

**🟡 Intermedia**
- Directa 3 {numero[-3:]}
- Premio estimado: ${PREMIOS['D3'] * apuesta:,}
- Con multiplicador: ${PREMIOS['D3'] * apuesta * MULTIPLICADOR:,}

**🔴 Agresiva**
- Directa 5 {numero}
- Premio estimado: ${PREMIOS['D5'] * apuesta:,}
- Con multiplicador: ${PREMIOS['D5'] * apuesta * MULTIPLICADOR:,}
""")

    st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantía de premio.")

else:
    st.info("Ingresa un número válido para comenzar el análisis.")
