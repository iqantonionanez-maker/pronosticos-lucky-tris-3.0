import streamlit as st
import pandas as pd
from itertools import permutations

st.set_page_config(page_title="Pronósticos Lucky – TRIS", layout="centered")

st.title("🎲 Pronósticos Lucky – TRIS")

# ===============================
# CARGA DE DATOS (CSV REAL)
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    return df

df = cargar_datos()
total_sorteos = len(df)

# ===============================
# MODALIDADES (COLUMNAS REALES R1–R5)
# ===============================
modalidades = {
    "Número inicial": {
        "partes": ["R1"],
        "premio": 10,
        "multiplicador": 20
    },
    "Par inicial": {
        "partes": ["R1", "R2"],
        "premio": 50,
        "multiplicador": 200
    },
    "Número final": {
        "partes": ["R5"],
        "premio": 10,
        "multiplicador": 20
    },
    "Par final": {
        "partes": ["R4", "R5"],
        "premio": 50,
        "multiplicador": 200
    },
    "Directa 3": {
        "partes": ["R3", "R4", "R5"],
        "premio": 500,
        "multiplicador": 500
    },
    "Directa 4": {
        "partes": ["R2", "R3", "R4", "R5"],
        "premio": 5000,
        "multiplicador": 1000
    },
    "Directa 5": {
        "partes": ["R1", "R2", "R3", "R4", "R5"],
        "premio": 50000,
        "multiplicador": 10000
    }
}

# ===============================
# ENTRADAS USUARIO
# ===============================
modalidad = st.selectbox("Selecciona la modalidad", modalidades.keys())
numero = st.text_input("Ingresa el número a jugar")
apuesta_tris = st.number_input("Apuesta TRIS ($)", min_value=1, value=1)
apuesta_multi = st.number_input("Apuesta Multiplicador ($)", min_value=0, value=0)

info = modalidades[modalidad]
partes = info["partes"]

# ===============================
# VALIDACIONES CORRECTAS
# ===============================
if numero:
    if not numero.isdigit():
        st.warning("El número solo debe contener dígitos.")
        st.stop()

    if len(numero) != len(partes):
        st.warning(
            f"Para **{modalidad}** debes ingresar "
            f"exactamente **{len(partes)} dígito(s)**."
        )
        st.stop()

# ===============================
# ANÁLISIS
# ===============================
if st.button("🔍 Analizar"):
    df_temp = df.copy()

    # Construcción segura de la jugada
    df_temp["JUGADA"] = df_temp[partes].astype(str).agg("".join, axis=1)

    apariciones = (df_temp["JUGADA"] == numero).sum()

    st.subheader("📊 Análisis estadístico")
    st.write(
        f"El número **{numero}** apareció **{apariciones} veces** "
        f"en los últimos **{total_sorteos} sorteos analizados**."
    )

    # ===============================
    # NÚMEROS SIMILARES (5)
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
    # CÁLCULO OFICIAL DE PREMIOS
    # ===============================
    st.subheader("💰 Cálculo de premio estimado")

    premio_tris = apuesta_tris * info["premio"]
    premio_multi = apuesta_multi * info["multiplicador"]
    total_ganar = premio_tris + premio_multi

    st.markdown(
        f"""
        **Detalle de jugada**

        - Modalidad: **{modalidad}**
        - Número: **{numero}**
        - Apuesta TRIS: **${apuesta_tris}**
        - Apuesta Multiplicador: **${apuesta_multi}**

        **Desglose**
        - Premio TRIS: ${premio_tris}
        - Premio Multiplicador: ${premio_multi}

        ### 🟢 Cantidad máxima a ganar: **${total_ganar}**
        """
    )

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
