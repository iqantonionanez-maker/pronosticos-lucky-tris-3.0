import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="Pronósticos Lucky", layout="centered")

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True)

    # reconstruimos el número completo
    df["NUMERO"] = (
        df["R1"].astype(str)
        + df["R2"].astype(str)
        + df["R3"].astype(str)
        + df["R4"].astype(str)
        + df["R5"].astype(int).astype(str)
    )

    return df.sort_values("FECHA", ascending=False)

df = cargar_datos()

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS")
st.success(f"Sorteos cargados: {len(df)}")

# =========================
# LEYENDA
# =========================
st.info(
    "🔥 **Caliente**: aparece más que el promedio | "
    "❄️ **Frío**: aparece menos que el promedio | "
    "⚪ **Promedio**: comportamiento normal"
)

# =========================
# ENTRADA USUARIO
# =========================
numero_usuario = st.text_input(
    "🔍 Ingresa tu número (1 a 5 dígitos)",
    max_chars=5
)

if not numero_usuario.isdigit():
    st.stop()

# =========================
# FUNCIONES
# =========================
def estado_numero(conteo, total_posibles):
    promedio = len(df) / total_posibles
    ratio = conteo / promedio if promedio > 0 else 0

    if ratio >= 1.2:
        return "🔥 Caliente"
    elif ratio <= 0.8:
        return "❄️ Frío"
    else:
        return "⚪ Promedio"

def ultima_aparicion(filtro):
    if len(filtro) == 0:
        return "Sin historial"
    fila = filtro.iloc[0]
    return f"{fila['FECHA'].strftime('%d/%m/%Y')} – Sorteo {fila['CONCURSO']}"

def analizar(valor, tipo):
    largo = len(valor)

    if largo == 5:
        apar = df[df["NUMERO"] == valor]
        total = 100000
    elif largo == 4:
        apar = df[df["NUMERO"].str.endswith(valor) | df["NUMERO"].str.startswith(valor)]
        total = 10000
    elif largo == 3:
        apar = df[df["NUMERO"].str.contains(valor)]
        total = 1000
    elif largo == 2:
        apar = df[df["NUMERO"].str.endswith(valor)]
        total = 100
    else:
        apar = df[df["NUMERO"].str.endswith(valor)]
        total = 10

    estado = estado_numero(len(apar), total)
    ultima = ultima_aparicion(apar)

    st.write(f"**{tipo} {valor}** → {estado} | {ultima}")

# =========================
# ANALISIS PRINCIPAL
# =========================
st.subheader("📊 Análisis de tu número")

analizar(numero_usuario, "Número ingresado")

# =========================
# DESCOMPOSICION AUTOMATICA
# =========================
st.subheader("🔍 Opciones de juego con este número")

n = numero_usuario

if len(n) == 5:
    analizar(n[:4], "Directa 4")
    analizar(n[1:], "Directa 4")
    analizar(n[:3], "Directa 3")
    analizar(n[-3:], "Directa 3")
    analizar(n[:2], "Par inicial")
    analizar(n[-2:], "Par final")
    analizar(n[0], "Número inicial")
    analizar(n[-1], "Número final")

elif len(n) == 4:
    analizar(n[:3], "Directa 3")
    analizar(n[-3:], "Directa 3")
    analizar(n[:2], "Par inicial")
    analizar(n[-2:], "Par final")
    analizar(n[0], "Número inicial")
    analizar(n[-1], "Número final"
