import streamlit as st
import pandas as pd

# =============================
# CONFIGURACIÓN GENERAL
# =============================
st.set_page_config(
    page_title="🎲 Pronósticos Lucky – TRIS",
    layout="centered"
)

st.title("🎲 Pronósticos Lucky – TRIS")
st.caption("Análisis estadístico basado únicamente en histórico oficial")

st.markdown(
    """
    **Disclaimer:**  
    Este análisis es únicamente estadístico e informativo.  
    No garantiza premios ni resultados.
    """
)

# =============================
# CARGA Y LIMPIEZA DE DATOS
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("Tris.csv")

    # Convertir fecha
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")

    # Eliminar sorteos incompletos
    df = df.dropna(subset=["FECHA", "R1", "R2", "R3", "R4", "R5"])

    # Asegurar que los resultados sean texto (NO int)
    for col in ["R1", "R2", "R3", "R4", "R5"]:
        df[col] = df[col].astype(str).str.strip()

    return df

df = load_data()

total_sorteos = df["CONCURSO"].nunique()
fecha_inicio = df["FECHA"].min().date()
fecha_fin = df["FECHA"].max().date()

st.markdown(
    f"""
    **Histórico analizado:**  
    {total_sorteos} sorteos  
    Desde **{fecha_inicio}** hasta **{fecha_fin}**
    """
)

# =============================
# MODALIDADES OFICIALES
# =============================
modalidades = {
    "Directa 5": ["R1", "R2", "R3", "R4", "R5"],
    "Directa 4": ["R2", "R3", "R4", "R5"],
    "Directa 3": ["R3", "R4", "R5"],
    "Par inicial": ["R1", "R2"],
    "Par final": ["R4", "R5"],
    "Número inicial": ["R1"],
    "Número final": ["R5"]
}

premios_tris = {
    "Directa 5": 50000,
    "Directa 4": 5000,
    "Directa 3": 500,
    "Par inicial": 50,
    "Par final": 50,
    "Número inicial": 5,
    "Número final": 5
}

multiplicadores = {
    "Directa 5": 200000,
    "Directa 4": 20000,
    "Directa 3": 2000,
    "Par inicial": 200,
    "Par final": 200,
    "Número inicial": 20,
    "Número final": 20
}

# =============================
# INPUTS DEL USUARIO
# =============================
st.subheader("🎯 Selección de jugada")

modalidad = st.selectbox("Modalidad", list(modalidades.keys()))
numero = st.text_input("Número a analizar (sin espacios)", "").strip()

col1, col2 = st.columns(2)
with col1:
    apuesta_tris = st.number_input("Apuesta TRIS ($)", min_value=1, step=1)
with col2:
    apuesta_multiplicador = st.number_input("Apuesta multiplicador ($)", min_value=0, step=1)

# =============================
# VALIDACIONES
# =============================
partes = modalidades[modalidad]

if len(numero) != len(partes) or not numero.isdigit():
    st.warning(f"El número debe tener exactamente {len(partes)} dígitos.")
    st.stop()

# =============================
# CONSTRUCCIÓN DE LA JUGADA
# =============================
df["JUGADA"] = df[partes].agg("".join, axis=1)

apariciones = df[df["JUGADA"] == numero]
conteo = len(apariciones)

ultima_fecha = apariciones["FECHA"].max().date() if conteo > 0 else "Nunca"
ultimo_concurso = apariciones["CONCURSO"].max() if conteo > 0 else None
