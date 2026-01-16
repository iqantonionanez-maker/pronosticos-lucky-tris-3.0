import streamlit as st
import pandas as pd
from itertools import permutations

st.set_page_config(page_title="Pronósticos Lucky TRIS", layout="centered")

st.title("🎲 Pronósticos Lucky – TRIS")

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df.columns = [c.upper() for c in df.columns]
    return df

df = cargar_datos()
total_sorteos = len(df)

# ===============================
# MODALIDADES
# ===============================
modalidades = {
    "Número final": {
        "partes": ["N5"],
        "premio": 10,
        "multiplicador": 20
    },
    "Par final": {
        "partes": ["N4", "N5"],
        "premio": 50,
        "multiplicador": 200
    },
    "Número inicial": {
        "partes": ["N1"],
        "premio": 10,
        "multiplicador": 20
    },
    "Par inicial": {
        "partes": ["N1", "N2"],
        "premio": 50,
        "multiplicador": 200
    },
    "Directa 3": {
        "partes": ["N3", "N4", "N5"],
        "premio": 500,
        "multiplicador": 500
    },
    "Directa 4": {
        "partes": ["N2", "N3", "N4", "N5"],
        "premio": 5000,
        "multiplicador": 1000
    },
    "Directa 5": {
        "partes": ["N1", "N2", "N3", "N4", "N5"],
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
# VALIDACIONES
# ===============================
if numero:
    if not numero.isdigit():
        st.warning("El número solo debe contener dígitos.")
        st.stop()

    if len(numero) != len(partes):
        st.warning(
            f"Para la modalidad **{modalidad}** debes ingresar "
            f"**{len(partes)} dígito(s)**."
        )
        st.stop()

# ===============================
# ANÁLISIS
# ===============================
if st.button("🔍 Analizar"):
    df_temp = df.copy()

    # Construir jugada según modalidad
    df_temp["JUGADA"] = df_temp[partes].astype(str).agg("".join, axis=1)

    apariciones = (df_temp["JUGADA"] == numero).sum()

    st.subheader("📊 Análisis estadístico")
    st.write(
        f"El número **{numero}** apareció **{apariciones} veces** "
        f"en los últimos **{total_sorteos} sorteos analizados**."
    )

    # ===============================
    # NÚMEROS SIMILARES
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
    # CÁLCULO DE PREMIOS
    # ===============================
    st.subheader("💰 Cálculo de premio estimado")

    premio_tris = apuesta_tris * info["premio"]
    premio_multi = apuesta_multi * info["multiplicador"]
    total_ganar = premio_tris + premio_multi

    st.markdown(
        f"""
        **Ejemplo de jugada**

        - Modalidad: **{modalidad}**
        - Número jugado: **{numero}**
        - Apuesta TRIS: **${apuesta_tris}**
        - Apuesta Multiplicador: **${apuesta_multi}**

        **Desglose**
        - Premio TRIS: ${premio_tris}
        - Premio Multiplicador: ${premio_multi}

        ### 🟢 Cantidad máxima a ganar: **${total_ganar}**
        """
    )

    # ===============================
    # TABLA OFICIAL
    # ===============================
    st.subheader("📋 Tabla oficial aplicada")
    st.write(
        f"""
        - Premio por $1 TRIS: **${info['premio']}**
        - Multiplicador oficial: **{info['multiplicador']}×**
        """
    )
