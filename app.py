import streamlit as st
import pandas as pd
from datetime import timedelta

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config("Pronósticos Lucky TRIS", layout="wide")

st.markdown("""
<style>
body { background-color:#0b0f1a; }
h1,h2,h3 { color:#f5c77a; }
.card {
    background:#141a2e;
    padding:15px;
    border-radius:12px;
    margin-bottom:12px;
}
.ok { color:#2ecc71; font-weight:bold; }
.warn { color:#f1c40f; font-weight:bold; }
.danger { color:#e74c3c; font-weight:bold; }
.info { color:#5dade2; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS
# =====================================================
@st.cache_data
def cargar():
    df = pd.read_csv("Tris.csv")
    df.columns = df.columns.str.upper().str.strip()

    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["FECHA"])
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
# PREMIOS OFICIALES POR MODALIDAD
# =====================================================
PREMIOS_BASE = {
    "NUM": 5,      # Número final/inicial
    "PAR": 50,     # Par final/inicial
    "D3": 500,     # Directa 3
    "D4": 5000,    # Directa 4
    "D5": 50000    # Directa 5
}

MULTIPLICADOR_MAX = 4  # máximo multiplicador oficial

# =====================================================
# FUNCIONES ESTADÍSTICAS
# =====================================================
def stats(col, val):
    d = df[df[col] == val]
    if d.empty:
        return None

    ultimo = d.iloc[-1]["SORTEO"]
    sin = df["SORTEO"].max() - ultimo
    prom = d["SORTEO"].diff().mean()

    ult_ano = df[df["FECHA"] >= df["FECHA"].max() - timedelta(days=365)]
    d_ano = ult_ano[ult_ano[col] == val]
    prom_ano = d_ano["SORTEO"].diff().mean()

    ult_100 = df.tail(100)
    veces_100 = (ult_100[col] == val).sum()

    return sin, prom, prom_ano, veces_100

def top_modalidad(col):
    conteo = df[col].value_counts()
    promedio = conteo.mean()
    return (
        conteo[conteo > promedio].head(5),
        conteo[conteo < promedio].tail(5)
    )

# =====================================================
# INTERFAZ
# =====================================================
st.title("🎲 Pronósticos Lucky")

col1, col2 = st.columns(2)

with col1:
    tipo = st.selectbox(
        "🎯 Tipo de jugada",
        [
            "Número final",
            "Número inicial",
            "Par final",
            "Par inicial",
            "Directa 3",
            "Directa 4",
            "Directa 5"
        ]
    )

with col2:
    num = st.text_input("🔍 Ingresa tu número")

apuesta = st.number_input("💰 Monto a apostar ($)", min_value=1, value=1)
use_mult = st.checkbox("Activar Tris Multiplicador")

# =====================================================
# MAPEO DE COLUMNAS
# =====================================================
mapa = {
    "Número final": ("NUM_FINAL", "NUM"),
    "Número inicial": ("NUM_INICIAL", "NUM"),
    "Par final": ("PAR_FINAL", "PAR"),
    "Par inicial": ("PAR_INICIAL", "PAR"),
    "Directa 3": ("D3", "D3"),
    "Directa 4": ("D4", "D4"),
    "Directa 5": ("D5", "D5")
}

if num.isdigit() and tipo in mapa:
    col_db, key_premio = mapa[tipo]
    req_len = int(col_db.replace("D","")) if col_db.startswith("D") else (1 if "NUM" in col_db else 2)

    if len(num) != req_len:
        st.error(f"❌ {tipo} requiere exactamente {req_len} dígito(s).")
        st.stop()

    st.header(f"📊 Análisis – {tipo} {num}")

    r = stats(col_db, num)
    if not r:
        st.warning("Sin historial para esta jugada.")
    else:
        sin, prom, prom_ano, v100 = r
        st.markdown(f"""
<div class="card">
🔎 Veces en últimos 100 sorteos: {v100}<br>
⏱ Promedio histórico: {int(prom) if prom==prom else '-'} sorteos<br>
📅 Promedio último año: {int(prom_ano) if prom_ano==prom_ano else '-'} sorteos<br>
⚠️ Sorteos sin salir: {sin}
</div>
""", unsafe_allow_html=True)

    # =====================================================
    # CÁLCULO DE PREMIO
    # =====================================================
    st.header("💰 Premio estimado")

    base = PREMIOS_BASE[key_premio] * apuesta
    con_mult = base * MULTIPLICADOR_MAX if use_mult else None

    st.markdown(f"""
<div class="card">
🏆 **Premio base (sin multiplicador):** ${base:,}<br>
{"🔁 **Premio con multiplicador máximo:** $" + str(con_mult) + "<br>" if use_mult else ""}
Notas: Premios según reglas oficiales del TRIS.
</div>
""", unsafe_allow_html=True)

    # =====================================================
    # RECOMENDACIÓN LUCKY
    # =====================================================
    st.header("🍀 Recomendación Lucky")

    st.markdown(f"""
<div class="card">
🟢 <b>Conservadora</b><br>
{tipo} {num}<br>
Premio base: ${base:,}<br>
Motivo: combinación de historial y frecuencia estable.
</div>

<div class="card">
🟡 <b>Intermedia</b><br>
Directa 3 {num[-3:].zfill(3)}<br>
Premio base: ${PREMIOS_BASE['D3']*apuesta:,}<br>
Motivo: opción equilibrada entre riesgo y premio.
</div>

<div class="card">
🔴 <b>Agresiva</b><br>
Directa 5 {num.zfill(5)}<br>
Premio base: ${PREMIOS_BASE['D5']*apuesta:,}<br>
Motivo: mayor premio posible, pero más riesgo.
</div>
""", unsafe_allow_html=True)

    st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantiza premio.")

else:
    st.info("Ingresa un número y tipo de jugada válido para comenzar.")
