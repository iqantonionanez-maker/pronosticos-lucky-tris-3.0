import streamlit as st
import pandas as pd
from datetime import timedelta

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config("Pronósticos Lucky TRIS", layout="wide")

st.markdown("""
<style>
body { background-color:#1e7f43; }
.block-container { padding:2rem; }
h1,h2,h3,h4 { color:#000000; }
p,span,li { color:#000000; font-size:16px; }
.card {
    background:#e9f5ec;
    padding:15px;
    border-radius:12px;
    margin-bottom:12px;
}
.good { color:#0a5; font-weight:bold; }
.mid { color:#b58900; font-weight:bold; }
.bad { color:#b00; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS (ADAPTADA A TU CSV)
# =====================================================
@st.cache_data
def cargar():
    df = pd.read_csv("Tris.csv")
    df.columns = df.columns.str.upper().str.strip()

    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["FECHA"])

    if "CONCURSO" in df.columns:
        df = df.rename(columns={"CONCURSO": "SORTEO"})

    for c in ["R1","R2","R3","R4","R5"]:
        df[c] = df[c].fillna("0").astype(str).str.replace(".0","", regex=False)

    df["NUMERO"] = df["R1"]+df["R2"]+df["R3"]+df["R4"]+df["R5"]

    df["NUM_FINAL"] = df["NUMERO"].str[-1]
    df["NUM_INICIAL"] = df["NUMERO"].str[0]
    df["PAR_FINAL"] = df["NUMERO"].str[-2:]
    df["PAR_INICIAL"] = df["NUMERO"].str[:2]
    df["D3"] = df["NUMERO"].str[-3:]
    df["D4"] = df["NUMERO"].str[-4:]
    df["D5"] = df["NUMERO"]

    return df.sort_values("SORTEO")

df = cargar()

# =====================================================
# PREMIOS OFICIALES
# =====================================================
PREMIOS = {
    "NUM": 5,
    "PAR": 50,
    "D3": 500,
    "D4": 5000,
    "D5": 50000
}
MULTIPLICADOR_MAX = 4

# =====================================================
# FUNCIONES DE ANÁLISIS
# =====================================================
def analizar(col, val):
    d = df[df[col] == val]
    if d.empty:
        return None

    ultimo_sorteo = d.iloc[-1]["SORTEO"]
    sin_salir = df["SORTEO"].max() - ultimo_sorteo
    promedio = d["SORTEO"].diff().mean()

    ult_30 = df.tail(30)
    veces_30 = (ult_30[col] == val).sum()

    return sin_salir, promedio, veces_30

def explicar(sin, prom, v30):
    if v30 >= 4:
        estado = "🔥 Número caliente"
        motivo = f"ha salido {v30} veces en los últimos 30 sorteos."
    elif sin > prom:
        estado = "❄️ Número atrasado"
        motivo = f"sale en promedio cada {int(prom)} sorteos y lleva {sin} sin salir."
    else:
        estado = "⚪ Comportamiento normal"
        motivo = "su frecuencia es similar al promedio histórico."
    return estado, motivo

# =====================================================
# INTERFAZ
# =====================================================
st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS basado en historial real")

st.markdown("""
🔥 Caliente: aparece más que el promedio  
❄️ Frío: aparece menos que el promedio  
⚪ Promedio: comportamiento normal
""")

tipo = st.selectbox(
    "🎯 Tipo de jugada",
    ["Par final","Par inicial","Número final","Número inicial","Directa 3","Directa 4","Directa 5"],
    index=0
)

num = st.text_input("🔍 Ingresa tu número")
apuesta = st.number_input("💰 Monto base a apostar ($)", min_value=1, value=1)

use_mult = st.checkbox("Activar Tris Multiplicador")
monto_mult = st.number_input(
    "💰 Monto para multiplicador ($)",
    min_value=0,
    value=0,
    disabled=not use_mult
)

mapa = {
    "Número final": ("NUM_FINAL","NUM",1),
    "Número inicial": ("NUM_INICIAL","NUM",1),
    "Par final": ("PAR_FINAL","PAR",2),
    "Par inicial": ("PAR_INICIAL","PAR",2),
    "Directa 3": ("D3","D3",3),
    "Directa 4": ("D4","D4",4),
    "Directa 5": ("D5","D5",5)
}

if num.isdigit() and tipo in mapa:
    col_db, key, largo = mapa[tipo]

    if len(num) != largo:
        st.error(f"{tipo} requiere {largo} dígitos.")
        st.stop()

    res = analizar(col_db, num)

    st.header("📊 Análisis de tu número")

    if not res:
        st.warning("No tiene historial registrado.")
    else:
        sin, prom, v30 = res
        estado, motivo = explicar(sin, prom, v30)

        st.markdown(f"""
<div class="card">
<b>{estado}</b><br>
Este número {motivo}<br>
Sorteos sin salir: <b>{sin}</b>
</div>
""", unsafe_allow_html=True)

    # ===============================
    # PREMIO
    # ===============================
    st.header("💰 Premio máximo")

    base = PREMIOS[key] * apuesta
    premio_mult = monto_mult * PREMIOS[key] * MULTIPLICADOR_MAX if use_mult else 0

    st.markdown(f"""
<div class="card">
Premio base: <b>${base:,}</b><br>
Premio máximo con multiplicador: <b>${premio_mult:,}</b>
</div>
""", unsafe_allow_html=True)

    # ===============================
    # RECOMENDACIÓN LUCKY REAL
    # ===============================
    st.header("🍀 Recomendación Lucky")

    opciones = []
    for t,(c,k,l) in mapa.items():
        if len(num) >= l:
            val = num[-l:]
            r = analizar(c,val)
            if r:
                sin,p,v30 = r
                score = v30*2 + max(0,(sin-p))
                opciones.append((score,t,val,sin,p,v30))

    opciones = sorted(opciones, reverse=True)[:3]

    for i,(s,t,v,sin,p,v30) in enumerate(opciones):
        estado,motivo = explicar(sin,p,v30)
        st.markdown(f"""
<div class="card">
<b>{t} {v}</b><br>
{estado}<br>
Recomendado porque {motivo}
</div>
""", unsafe_allow_html=True)

    st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantiza premio.")
