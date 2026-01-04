import streamlit as st
import pandas as pd
from datetime import timedelta

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config("Pronósticos Lucky TRIS", layout="wide")

st.markdown("""
<style>
body { background-color:#1f7a4d; }
.block-container { padding:2rem; }
h1,h2,h3,h4 { color:#000000; }
p,span,li,label { color:#000000; font-size:16px; }
.card {
    background:#e8f4ec;
    padding:16px;
    border-radius:14px;
    margin-bottom:14px;
    border:1px solid #b6d7c9;
}
.kpi { font-weight:700; }
.sep { height:8px; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS (ADAPTADA A TU CSV)
# =====================================================
@st.cache_data
def cargar():
    df = pd.read_csv("Tris.csv")
    df.columns = df.columns.str.upper().str.strip()

    # Fecha
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["FECHA"])

    # Sorteo
    if "CONCURSO" in df.columns:
        df = df.rename(columns={"CONCURSO": "SORTEO"})
    if "SORTEO" not in df.columns:
        df["SORTEO"] = range(1, len(df)+1)

    # Dígitos
    for c in ["R1","R2","R3","R4","R5"]:
        if c not in df.columns:
            df[c] = "0"
        df[c] = df[c].fillna("0").astype(str).str.replace(".0","", regex=False)

    df["NUMERO"] = df["R1"]+df["R2"]+df["R3"]+df["R4"]+df["R5"]

    # Modalidades
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
# PREMIOS OFICIALES TRIS
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
# FUNCIONES
# =====================================================
def analizar(col, val):
    d = df[df[col] == val]
    if d.empty:
        return None
    ultimo = d.iloc[-1]["SORTEO"]
    sin = int(df["SORTEO"].max() - ultimo)
    prom = d["SORTEO"].diff().mean()
    ult100 = df.tail(100)
    v100 = int((ult100[col] == val).sum())
    return sin, prom, v100

def explicar(sin, prom, v100):
    if v100 >= 3:
        return ("🔥 Caliente",
                f"ha salido {v100} veces en los últimos 100 sorteos, indicando actividad reciente.")
    if prom == prom and sin >= prom:
        return ("❄️ Atrasado",
                f"sale en promedio cada {int(prom)} sorteos y lleva {sin} sorteos sin salir.")
    return ("⚪ Normal",
            "su frecuencia es similar al promedio histórico.")

# =====================================================
# INTERFAZ
# =====================================================
st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS basado en historial real")
st.success(f"Sorteos cargados correctamente: {len(df)}")

st.markdown("""
**Leyenda:**  
🔥 Caliente = aparece más que el promedio | ❄️ Frío/Atrasado = aparece menos que el promedio | ⚪ Normal = comportamiento promedio
""")

# Selecciones
tipo = st.selectbox(
    "🎯 Tipo de jugada",
    ["Par final","Par inicial","Número final","Número inicial","Directa 3","Directa 4","Directa 5"],
    index=0
)

num = st.text_input("🔍 Ingresa tu número")
apuesta = st.number_input("💰 Apuesta base ($)", min_value=1, value=1)

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

# =====================================================
# ANÁLISIS PRINCIPAL
# =====================================================
if num.isdigit() and tipo in mapa:
    col_db, key, largo = mapa[tipo]
    if len(num) != largo:
        st.error(f"{tipo} requiere exactamente {largo} dígito(s).")
        st.stop()

    st.header("📊 Análisis de tu número")
    r = analizar(col_db, num)
    if not r:
        st.warning("Este número no tiene apariciones históricas.")
    else:
        sin, prom, v100 = r
        estado, motivo = explicar(sin, prom, v100)
        st.markdown(f"""
<div class="card">
<b>{estado}</b><br>
{motivo}<br>
<b>Sorteos sin salir:</b> {sin}
</div>
""", unsafe_allow_html=True)

    # =================================================
    # PREMIO MÁXIMO (DESGLOSE CORRECTO)
    # =================================================
    st.header("💰 Premio máximo por jugada")
    premio_base = PREMIOS[key] * apuesta
    premio_mult = PREMII = 0
    if use_mult and monto_mult > 0:
        premio_mult = monto_mult * PREMIOS[key] * MULTIPLICADOR_MAX
    total = premio_base + premio_mult

    st.markdown(f"""
<div class="card">
<b>Premio base:</b> ${premio_base:,}<br>
<b>Premio con multiplicador:</b> ${premio_mult:,}<br>
<hr>
<b>Total máximo posible:</b> ${total:,}
</div>
""", unsafe_allow_html=True)

    # =================================================
    # RECOMENDACIÓN LUCKY (5 OPCIONES, ANALIZADAS)
    # =================================================
    st.header("🍀 Recomendación Lucky (ordenadas por oportunidad)")

    candidatos = []
    for t,(c,k,l) in mapa.items():
        if len(num) >= l:
            val = num[-l:]
            rr = analizar(c, val)
            if rr:
                sin,p,v100 = rr
                score = (v100*3) + max(0, (sin - (p if p==p else 0)))
                candidatos.append((score, t, val, sin, p, v100, k))

    candidatos = sorted(candidatos, reverse=True)[:5]

    for i,(s,t,v,sin,p,v100,k) in enumerate(candidatos, start=1):
        estado, motivo = explicar(sin, p, v100)
        st.markdown(f"""
<div class="card">
<b>{i}. {t} {v}</b><br>
{estado}<br>
<b>Motivo:</b> {motivo}<br>
<b>Promedio histórico:</b> {int(p) if p==p else '-'} sorteos | <b>Sin salir:</b> {sin}<br>
<b>Premio por $1:</b> ${PREMIOS[k]:,}
</div>
""", unsafe_allow_html=True)

    st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantiza premio.")
else:
    st.info("Ingresa un número válido para comenzar.")
