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
    df["R5"] = df["R5"].astype(str).str.zfill(5)
    return df

df = cargar_datos()

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS")
st.success(f"Sorteos cargados: {len(df)}")

# =========================
# ENTRADA
# =========================
numero_usuario = st.text_input(
    "🔍 Ingresa tu número (1 a 5 dígitos)",
    max_chars=5
).zfill(len(st.text_input("", "", key="hidden")))

if not numero_usuario.strip():
    st.stop()

# =========================
# FUNCIONES
# =========================
def estado_numero(conteo, promedio):
    ratio = conteo / promedio if promedio > 0 else 0
    if ratio >= 1.2:
        return "🔥 Caliente (sale más que el promedio)"
    elif ratio <= 0.8:
        return "❄️ Frío (sale menos que el promedio)"
    else:
        return "⚪ Promedio (comportamiento normal)"

def ultima_aparicion(valor, columna):
    apar = df[df[columna] == valor]
    if len(apar) == 0:
        return "Sin historial"
    ult = apar.iloc[0]
    return f"{ult['FECHA'].strftime('%d/%m/%Y')} – Sorteo {ult['CONCURSO']}"

# =========================
# ANALISIS PRINCIPAL
# =========================
st.subheader("📊 Análisis de tu número")

col = f"R{len(numero_usuario)}"
apariciones = df[df[col] == numero_usuario]
promedio = len(df) / (10 ** len(numero_usuario))

st.write(f"Apariciones: **{len(apariciones)}**")
st.write(f"Estado: **{estado_numero(len(apariciones), promedio)}**")
st.write(f"Última aparición: **{ultima_aparicion(numero_usuario, col)}**")

# =========================
# DESCOMPOSICION AUTOMATICA
# =========================
st.subheader("🔍 Descomposición y análisis automático")

def analizar(valor, etiqueta):
    col = f"R{len(valor)}"
    apar = df[df[col] == valor]
    estado = estado_numero(len(apar), len(df) / (10 ** len(valor)))
    ultima = ultima_aparicion(valor, col)
    st.write(f"**{etiqueta} {valor}** → {estado} | {ultima}")

n = numero_usuario

if len(n) >= 5:
    analizar(n[:4], "Directa 4")
    analizar(n[1:], "Directa 4")
if len(n) >= 4:
    analizar(n[:3], "Directa 3")
    analizar(n[-3:], "Directa 3")
if len(n) >= 2:
    analizar(n[:2], "Par inicial")
    analizar(n[-2:], "Par final")
analizar(n[0], "Número inicial")
analizar(n[-1], "Número final")

# =========================
# CALIENTES / FRIOS POR PERIODO
# =========================
st.subheader("🔥❄️ Top números por periodo")

def top_periodo(dias, titulo):
    fecha_limite = df["FECHA"].max() - timedelta(days=dias)
    sub = df[df["FECHA"] >= fecha_limite]
    conteo = sub["R2"].value_counts()
    st.write(f"**{titulo}**")
    st.write("🔥 Calientes:", ", ".join(conteo.head(5).index))
    st.write("❄️ Fríos:", ", ".join(conteo.tail(5).index))

top_periodo(30, "Último mes")
top_periodo(180, "Últimos 6 meses")
top_periodo(365, "Último año")

# =========================
# ESCALERAS Y PIRÁMIDES
# =========================
st.subheader("🧠 Patrones recomendados")

def es_escalera(n):
    return abs(int(n[0]) - int(n[1])) == 1

def es_piramide(n):
    return n[0] == n[1]

esc = df[df["R2"].apply(es_escalera)]
pir = df[df["R2"].apply(es_piramide)]

st.write(f"🔢 Escaleras: {len(esc)} | Última: {esc.iloc[0]['FECHA'].strftime('%d/%m/%Y')}")
st.write(f"🔺 Pirámides: {len(pir)} | Última: {pir.iloc[0]['FECHA'].strftime('%d/%m/%Y')}")

st.caption("Pronósticos Lucky 🍀")
st.caption("Análisis basado únicamente en resultados históricos")
