import streamlit as st
import pandas as pd
import numpy as np

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🍀",
    layout="centered"
)

# ---------------- LOGO Y TÍTULO ----------------
st.image("logolucky.jpg", width=180)
st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Asegurar que las columnas existan
    columnas = ["R1", "R2", "R3", "R4", "R5"]
    df = df[columnas]

    # Eliminar filas con datos faltantes
    df = df.dropna()

    # Convertir a entero de forma segura
    for col in columnas:
        df[col] = df[col].astype(int)

    # Construir número ganador
    df["numero"] = (
        df["R1"].astype(str) +
        df["R2"].astype(str) +
        df["R3"].astype(str) +
        df["R4"].astype(str) +
        df["R5"].astype(str)
    )

    df["numero"] = df["numero"].str.zfill(5)

    return df.reset_index(drop=True)

df = cargar_datos()

st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- INPUT DEL USUARIO ----------------
st.markdown("## 🔍 Analizar número")

numero_input = st.text_input(
    "Ingresa el número que deseas analizar",
    max_chars=5
).strip()

if numero_input.isdigit():

    longitud = len(numero_input)

    # -------- DETECCIÓN DE FORMA --------
    if longitud == 5:
        forma_detectada = "Directa 5"
    elif longitud == 4:
        forma_detectada = "Directa 4 (últimos 4 números)"
    elif longitud == 3:
        forma_detectada = "Directa 3 (últimos 3 números)"
    else:
        forma_detectada = "Forma manual"

    st.info(f"Forma de juego detectada: **{forma_detectada}**")

    if longitud <= 2:
        forma = st.selectbox(
            "¿Cómo deseas analizar este número?",
            ["Par final", "Par inicial", "Número final", "Número inicial"],
            index=0,
            key="forma_juego_final"
        )
    else:
        forma = forma_detectada

    st.write(f"Forma seleccionada: **{forma}**")

    # ---------------- DATOS DE JUGADA ----------------
    st.markdown("## 💰 Datos de la jugada")

    monto = st.number_input(
        "Cantidad a jugar (pesos)",
        min_value=1,
        value=1
    )

    multiplicador = st.radio(
        "¿Jugar con multiplicador?",
        ["No", "Sí"],
        horizontal=True
    )

    mult = st.selectbox("Selecciona multiplicador", [2, 3, 5, 10]) if multiplicador == "Sí" else 1

    # ---------------- FILTRADO ----------------
    numeros = df["numero"]

    if forma == "Directa 5":
        coincidencias = numeros == numero_input.zfill(5)
        premio_base = 50000
    elif forma == "Directa 4 (últimos 4 números)":
        coincidencias = numeros.str[-4:] == numero_input.zfill(4)
        premio_base = 5000
    elif forma == "Directa 3 (últimos 3 números)":
        coincidencias = numeros.str[-3:] == numero_input.zfill(3)
        premio_base = 500
    elif forma == "Par final":
        coincidencias = numeros.str[-2:] == numero_input.zfill(2)
        premio_base = 50
    elif forma == "Par inicial":
        coincidencias = numeros.str[:2] == numero_input.zfill(2)
        premio_base = 50
    elif forma == "Número final":
        coincidencias = numeros.str[-1:] == numero_input.zfill(1)
        premio_base = 10
    elif forma == "Número inicial":
        coincidencias = numeros.str[:1] == numero_input.zfill(1)
        premio_base = 10
