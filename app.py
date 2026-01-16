import streamlit as st
import pandas as pd
from itertools import permutations

st.set_page_config(page_title="Pronósticos Lucky – TRIS", layout="centered")
st.title("🎲 Pronósticos Lucky – TRIS")

# ==================================================
# CARGA DE DATOS (ESTO YA FUNCIONABA)
# ==================================================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    return df

df = cargar_datos()
total_sorteos = len(df)

# ==================================================
# MODALIDADES (MISMA LÓGICA QUE ANTES)
# ==================================================
modalidades = {
    "Número inicial": ["R1"],
    "Par inicial": ["R1", "R2"],
    "Directa 3": ["R3", "R4", "R5"],
    "Directa 4": ["R2", "R3", "R4", "R5"],
    "Directa 5": ["R1", "R2", "R3", "R4", "R5"],
    "Número final": ["R5"],
    "Par final": ["R4", "R5"]
}

# ==================================================
# TABLA OFICIAL DE PREMIOS (NUEVO, NO TOCA ANÁLISIS)
# ==================================================
premios_oficiales = {
    "Número inicial": {"tris": 10, "multi": 20},
    "Número final": {"tris": 10, "multi": 20},
    "Par inicial": {"tris": 50, "multi": 200},
    "Par final": {"tris": 50, "multi": 200},
    "Directa 3": {"tris": 500, "multi": 500},
    "Directa 4": {"tris": 5000, "multi": 1000},
    "Directa 5": {"tris": 50000, "multi": 10000}
}

# ==================================================
# ENTRADAS
# ==================================================
modalidad = st.selectbox("Selecciona la modalidad", modalidades.keys())
numero = st.text_input("Ingresa el número a jugar")
apuesta_tris = st.number_input("Apuesta TRIS ($)", min_value=1, value=1)
apuesta_multi = st.number_input("Apuesta Multiplicador ($)", min_value=0, value=0)

partes = modalidades[modalidad]

# ==================================================
# VALIDACIÓN (MISMA IDEA, NO SE ENDURECE)
# ==================================================
if numero:
    if not numero.isdigit():
        st.warning("El número solo debe contener dígitos.")
        st.stop()

    if len(numero) != len(partes):
        st.warning(
            f"Para {modalidad} debes ingresar {len(partes)} dígito(s)."
        )
        st.stop()

# ==================================================
# ANÁLISIS (ESTE BLOQUE YA FUNCIONABA)
# ==================================================
if st.button("🔍 Analizar"):
    df_temp = df.copy()

    # Construcción de jugada (MISMO MÉTODO)
    df_temp["JUGADA"] = df_temp[partes].astype(str).agg("".join, axis=1)

    apariciones = (df_temp["JUGADA"] == numero).sum()

    st.subheader("📊 Análisis estadístico")
    st.write(
        f"El número **{numero}** apareció **{apariciones} veces** "
        f"en los últimos **{total_sorteos} sorteos analizados**."
    )

    # ==================================================
    # NÚMEROS SIMILARES (SE MANTIENE)
    # ==================================================
    st.subheader("🔄 Números similares")

    similares = set()

    if len(numero) > 1:
        for p in set(permutations(numero)):
            similares.add("".join(p))

    while len(similares) < 5:
        similares.add(numero[:-1] + "0")

    similares = list(similares)[:5]
    st.write(", ".join(similares))

    # ==================================================
    # 👉 NUEVO: CÁLCULO OFICIAL (NO TOCA ANÁLISIS)
    # ==================================================
    st.subheader("💰 Estimación de premio (oficial)")

    premio_tris = apuesta_tris * premios_oficiales[modalidad]["tris"]
    premio_multi = apuesta_multi * premios_oficiales[modalidad]["multi"]
    total_ganar = premio_tris + premio_multi

    st.markdown(
        f"""
        **Detalle de jugada**

        - Modalidad: **{modalidad}**
        - Número: **{numero}**
        - Apuesta TRIS: ${apuesta_tris}
        - Apuesta Multiplicador: ${apuesta_multi}

        **Desglose**
        - Premio TRIS: ${premio_tris}
        - Premio Multiplicador: ${premio_multi}

        ### 🟢 Cantidad máxima a ganar: **${total_ganar}**
        """
    )

    # ==================================================
    # DISCLAIMER
    # ==================================================
    st.markdown(
        """
        ---
        **Este análisis es únicamente estadístico e informativo.  
        No garantiza premios ni resultados.**
        """
    )
