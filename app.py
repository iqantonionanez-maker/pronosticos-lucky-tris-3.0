import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

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

    # Construir número ganador con R1 a R5
    df["numero"] = (
        df["R1"].astype(int).astype(str) +
        df["R2"].astype(int).astype(str) +
        df["R3"].astype(int).astype(str) +
        df["R4"].astype(int).astype(str) +
        df["R5"].astype(int).astype(str)
    )

    df["numero"] = df["numero"].str.zfill(5)
    return df

df = cargar_datos()

st.success(f"Sorteos cargados: {len(df)}")

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

    # -------- SELECCIÓN PARA 1 O 2 DÍGITOS --------
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

    if multiplicador == "Sí":
        mult = st.selectbox(
            "Selecciona multiplicador",
            [2, 3, 5, 10]
        )
    else:
        mult = 1

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
    else:
        coincidencias = pd.Series([False]*len(numeros))
        premio_base = 0

    total_apariciones = coincidencias.sum()

    # ---------------- RESULTADOS ----------------
    st.markdown("## 📊 Análisis básico")

    st.write(f"**Apariciones históricas:** {total_apariciones}")

    if total_apariciones > 0:
        ultima_aparicion = df[coincidencias].iloc[-1]
        st.write("**Última aparición:** registrada en histórico")
    else:
        st.write("**Última aparición:** Nunca ha salido")

    # ---------------- INDICADOR ----------------
    st.markdown("## 🚦 Indicador histórico")

    promedio = len(df) / max(1, premio_base)

    if total_apariciones == 0:
        st.error("🔴 Frecuencia nula — No hay registros históricos.")
    elif total_apariciones < promedio * 0.5:
        st.warning("🟠 Frecuencia baja — Aparición inferior al promedio.")
    else:
        st.success("🟢 Frecuencia media/alta — Comportamiento activo.")

    st.caption("""
🔴 Baja: Ha salido pocas veces históricamente  
🟠 Media: Comportamiento dentro de lo esperado  
🟢 Alta: Ha aparecido con frecuencia reciente  
""")

    # ---------------- GANANCIA ----------------
    st.markdown("## 💵 Ganancia máxima posible")

    ganancia = monto * premio_base * mult

    st.write(
        f"Ganancia máxima posible según reglas oficiales: **${ganancia:,.2f}**"
    )

    st.caption(
        "Este cálculo se basa en pagos oficiales del TRIS y multiplicadores vigentes."
    )

else:
    st.info("Ingresa solo números para comenzar el análisis.")

# ---------------- CIERRE DE MARCA ----------------
st.markdown("---")
st.markdown(
    "<center><b>Pronósticos Lucky te desea buena suerte 🍀</b></center>",
    unsafe_allow_html=True
)
