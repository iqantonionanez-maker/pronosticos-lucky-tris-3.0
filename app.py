import streamlit as st
import pandas as pd
from itertools import permutations

st.set_page_config(page_title="Pronósticos Lucky – TRIS", layout="centered")
st.title("🎲 Pronósticos Lucky – TRIS")

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    return df

df = cargar_datos()
total_sorteos = len(df)

# ===============================
# MODALIDADES (BASE FUNCIONAL)
# ===============================
modalidades = {
    "Número inicial": ["R1"],
    "Par inicial": ["R1", "R2"],
    "Directa 3": ["R3", "R4", "R5"],
    "Directa 4": ["R2", "R3", "R4", "R5"],
    "Directa 5": ["R1", "R2", "R3", "R4", "R5"],
    "Número final": ["R5"],
    "Par final": ["R4", "R5"]
}

# ===============================
# ENTRADAS
# ===============================
modalidad = st.selectbox("Selecciona la modalidad", modalidades.keys())
numero = st.text_input("Ingresa el número a analizar")

partes = modalidades[modalidad]

# ===============================
# VALIDACIÓN SIMPLE (LA QUE SÍ FUNCIONABA)
# ===============================
if numero:
    if not numero.isdigit():
        st.warning("El número solo debe contener dígitos.")
        st.stop()

    if len(numero) != len(partes):
        st.warning(
            f"Para {modalidad} debes ingresar {len(partes)} dígito(s)."
        )
        st.stop()

# ===============================
# ANÁLISIS (ESTE ES EL BLOQUE CLAVE)
# ===============================
if st.button("🔍 Analizar"):
    df_temp = df.copy()

    # Construcción correcta de la jugada
    df_temp["JUGADA"] = df_temp[partes].astype(str).agg("".join, axis=1)

    apariciones = (df_temp["JUGADA"] == numero).sum()

    st.subheader("📊 Análisis estadístico")
    st.write(
        f"El número **{numero}** apareció **{apariciones} veces** "
        f"en los últimos **{total_sorteos} sorteos analizados**."
    )

    # ===============================
    # NÚMEROS SIMILARES (BASE)
    # ===============================
    st.subheader("🔄 Números similares")

    similares = set()

    if len(numero) > 1:
        for p in set(permutations(numero)):
            similares.add("".join(p))

    while len(similares) < 5:
        similares.add(numero[:-1] + "0")

    similares = list(similares)[:5]
    st.write(", ".join(similares))

    # ===============================
    # DISCLAIMER
    # ===============================
    st.markdown(
        """
        ---
        **Este análisis es únicamente estadístico e informativo.  
        No garantiza premios ni resultados.**
        """
    )
