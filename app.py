import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="Pronósticos Lucky", layout="centered")

# =========================
# CARGA DE DATOS (ROBUSTA)
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True)

    # Forzar R1–R5 como dígitos reales
    for c in ["R1", "R2", "R3", "R4", "R5"]:
        df[c] = df[c].fillna(0).astype(int).astype(str)

    # Construcciones TRIS reales
    df["D5"] = df["R1"] + df["R2"] + df["R3"] + df["R4"] + df["R5"]
    df["D4"] = df["R2"] + df["R3"] + df["R4"] + df["R5"]
    df["D3"] = df["R3"] + df["R4"] + df["R5"]

    df["PAR_INICIAL"] = df["R1"] + df["R2"]
    df["PAR_FINAL"]   = df["R4"] + df["R5"]

    df["NUM_INICIAL"] = df["R1"]
    df["NUM_FINAL"]   = df["R5"]

    return df.sort_values("FECHA", ascending=False)

df = cargar_datos()

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS")
st.success(f"Sorteos cargados: {len(df)}")

# =========================
# LEYENDA CLARA
# =========================
st.info(
    "🔥 **Caliente**: aparece más que el promedio | "
    "❄️ **Frío**: aparece menos que el promedio | "
    "⚪ **Promedio**: comportamiento normal"
)

# =========================
# INPUT
# =========================
numero = st.text_input("🔍 Ingresa tu número (1 a 5 dígitos)", max_chars=5)

if not numero.isdigit():
    st.stop()

# =========================
# FUNCIONES
# =========================
def estado(conteo, total):
    promedio = len(df) / total
    ratio = conteo / promedio if promedio > 0 else 0
    if ratio >= 1.2:
        return "🔥 Caliente"
    elif ratio <= 0.8:
        return "❄️ Frío"
    else:
        return "⚪ Promedio"

def ultima(df_filtrado):
    if df_filtrado.empty:
        return "Sin historial"
    f = df_filtrado.iloc[0]
    return f"{f['FECHA'].strftime('%d/%m/%Y')} – Sorteo {f['CONCURSO']}"

def analizar(col, valor, total, etiqueta):
    sub = df[df[col] == valor]
    st.write(
        f"**{etiqueta} {valor}** → "
        f"{estado(len(sub), total)} | "
        f"{ultima(sub)}"
    )

# =========================
# ANALISIS PRINCIPAL
# =========================
st.subheader("📊 Análisis de tu número")

l = len(numero)

if l == 5:
    analizar("D5", numero, 100000, "Directa 5")

if l >= 4:
    analizar("D4", numero[-4:], 10000, "Directa 4")

if l >= 3:
    analizar("D3", numero[-3:], 1000, "Directa 3")

if l >= 2:
    analizar("PAR_FINAL", numero[-2:], 100, "Par final")
    analizar("PAR_INICIAL", numero[:2], 100, "Par inicial")

analizar("NUM_INICIAL", numero[0], 10, "Número inicial")
analizar("NUM_FINAL", numero[-1], 10, "Número final")

# =========================
# OPCIONES RELACIONADAS
# =========================
st.subheader("🔍 Recomendaciones relacionadas")

if l >= 2:
    analizar("PAR_INICIAL", numero[:2], 100, "Par inicial recomendado")
    analizar("PAR_FINAL", numero[-2:], 100, "Par final recomendado")

if l >= 3:
    analizar("D3", numero[-3:], 1000, "Directa 3 recomendad
