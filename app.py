import streamlit as st
import pandas as pd
from datetime import datetime

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
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["FECHA"])
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
numero = st.text_input("Número a analizar (sin espacios)", "")

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
df["JUGADA"] = df[partes].astype(int).astype(str).agg("".join, axis=1)

apariciones = df[df["JUGADA"] == numero]
conteo = len(apariciones)

ultima_fecha = apariciones["FECHA"].max().date() if conteo > 0 else "Nunca"
ultimo_concurso = apariciones["CONCURSO"].max() if conteo > 0 else None

if conteo > 0:
    sorteos_sin_salir = df["CONCURSO"].max() - ultimo_concurso
else:
    sorteos_sin_salir = total_sorteos

# =============================
# ANÁLISIS ESTADÍSTICO
# =============================
st.subheader("📊 Análisis estadístico")

st.markdown(
    f"""
    **Número analizado:** {numero}  
    **Apariciones:** {conteo} veces en {total_sorteos} sorteos  
    **Última aparición:** {ultima_fecha}  
    **Sorteos sin salir:** {sorteos_sin_salir}
    """
)

# =============================
# NÚMEROS SIMILARES
# =============================
st.subheader("🔄 Números similares")

def generar_similares(num, total=5):
    similares = set()
    digits = list(num)

    for i in range(len(digits)):
        for delta in [-1, 1]:
            new = digits.copy()
            d = int(new[i]) + delta
            if 0 <= d <= 9:
                new[i] = str(d)
                similares.add("".join(new))

    # Permutaciones
    if len(num) > 1:
        for i in range(len(num)):
            for j in range(i + 1, len(num)):
                perm = digits.copy()
                perm[i], perm[j] = perm[j], perm[i]
                similares.add("".join(perm))

    similares.discard(num)

    while len(similares) < total:
        similares.add(num[:-1] + str((int(num[-1]) + len(similares)) % 10))

    return list(similares)[:total]

similares = generar_similares(numero)

for s in similares:
    apar = df[df["JUGADA"] == s]
    st.markdown(
        f"""
        **{s}**  
        Apariciones: {len(apar)}  
        Última vez: {apar["FECHA"].max().date() if len(apar) > 0 else "Nunca"}
        """
    )

# =============================
# CÁLCULO DE PREMIOS (OFICIAL)
# =============================
st.subheader("💰 Estimación de premio (oficial)")

premio_base = apuesta_tris * premios_tris[modalidad]
premio_multiplicador = apuesta_multiplicador * multiplicadores[modalidad]
total_maximo = premio_base + premio_multiplicador

st.markdown(
    f"""
    **Desglose de la jugada:**  

    - Premio TRIS: ${premio_base:,}  
    - Premio multiplicador: ${premio_multiplicador:,}  
    - **Cantidad máxima a ganar:** ${total_maximo:,}
    """
)

# =============================
# TABLA INFORMATIVA
# =============================
st.subheader("ℹ️ Tabla informativa de premios")

tabla = pd.DataFrame({
    "Modalidad": premios_tris.keys(),
    "Premio por $1": premios_tris.values(),
    "Multiplicador máximo": multiplicadores.values()
})

st.dataframe(tabla, use_container_width=True)
