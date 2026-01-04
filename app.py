import streamlit as st
import pandas as pd
from datetime import timedelta

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Pronósticos Lucky",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===============================
# ESTILOS (VERDE CASINO)
# ===============================
st.markdown("""
<style>
.stApp {
    background-color: #0E3B2E;
}
.card {
    background-color: #145A45;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
h1, h2, h3, h4 {
    color: #FFFFFF;
}
p, li, span, div {
    color: #E0E0E0;
}
.gold {
    color: #F5C542;
    font-weight: bold;
}
.hot { color: #F5C542; }
.cold { color: #6EC1E4; }
.avg { color: #B0B0B0; }
.small {
    font-size: 0.9em;
    color: #CFCFCF;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True)
    df["R5"] = df["R5"].astype(str).str.zfill(5)
    df = df.sort_values("FECHA", ascending=False).reset_index(drop=True)
    return df

df = cargar_datos()

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS basado en historial real")
st.success(f"Sorteos cargados correctamente: {len(df)}")

st.markdown("""
<div class="small">
🔥 Caliente: aparece más que el promedio &nbsp;&nbsp;
❄️ Frío: aparece menos que el promedio &nbsp;&nbsp;
⚪ Promedio: comportamiento normal
</div>
""", unsafe_allow_html=True)

# ===============================
# ENTRADA USUARIO
# ===============================
numero = st.text_input(
    "🔍 Ingresa tu número (1 a 5 dígitos)",
    max_chars=5
).strip()

if not numero.isdigit() or len(numero) == 0:
    st.stop()

# ===============================
# FUNCIONES AUXILIARES
# ===============================
def analizar_apariciones(filtro_series):
    apariciones = df[filtro_series]
    total = len(apariciones)

    if total == 0:
        return {
            "total": 0,
            "ultima": None,
            "sorteos_sin_salir": len(df)
        }

    ultima = apariciones.iloc[0]
    idx_ultima = apariciones.index[0]
    sorteos_sin = idx_ultima

    return {
        "total": total,
        "ultima": ultima,
        "sorteos_sin_salir": sorteos_sin
    }

def promedio_entre_apariciones(series_index):
    if len(series_index) < 2:
        return None
    difs = series_index.to_series().diff().dropna()
    return int(difs.mean())

# ===============================
# ANÁLISIS DE TU NÚMERO
# ===============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Análisis de tu número")

filtro = df["R5"].str.endswith(numero)
res = analizar_apariciones(filtro)

if res["total"] == 0:
    st.write(f"El número **{numero}** no tiene apariciones históricas registradas.")
else:
    ultima = res["ultima"]
    st.write(
        f"**La última vez que tu número salió ganador fue en el sorteo "
        f"#{ultima['CONCURSO']} el día {ultima['FECHA'].strftime('%d/%m/%Y')}.**"
    )

    # Último año
    hace_un_ano = df["FECHA"].max() - timedelta(days=365)
    ult_ano = df[(df["FECHA"] >= hace_un_ano) & (df["R5"].str.endswith(numero))]
    prom_ano = promedio_entre_apariciones(ult_ano.index)

    st.write(
        f"En el **último año**, tu número ha salido ganador **{len(ult_ano)} veces**, "
        f"con un promedio de **{prom_ano if prom_ano else '—'} sorteos** entre apariciones."
    )

    # Histórico
    prom_hist = promedio_entre_apariciones(df[filtro].index)
    st.write(
        f"En el **histórico completo**, tu número ha salido ganador "
        f"**{res['total']} veces**, con un periodo promedio de "
        f"**{prom_hist if prom_hist else '—'} sorteos** entre apariciones."
    )

    st.write(
        f"Actualmente acumula **{res['sorteos_sin_salir']} sorteos consecutivos "
        f"sin ser número ganador.**"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# RECOMENDACIONES RELACIONADAS
# ===============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔍 Recomendaciones relacionadas")

def recomendar(label, valor):
    filtro = df["R5"].str.endswith(valor)
    r = analizar_apariciones(filtro)

    if r["total"] == 0:
        st.write(f"• **{label} {valor}** → Sin historial")
    else:
        st.write(
            f"• **{label} {valor}** → "
            f"{r['sorteos_sin_salir']} sorteos sin salir | "
            f"Última: {r['ultima']['FECHA'].strftime('%d/%m/%Y')}"
        )

if len(numero) >= 2:
    recomendar("Par final", numero[-2:])
    recomendar("Par inicial", numero[:2])

if len(numero) >= 3:
    recomendar("Directa 3", numero[-3:])

if len(numero) >= 4:
    recomendar("Directa 4", numero[-4:])

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# TOP PAR FINAL POR PERIODO
# ===============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔥❄️ Top Par Final por periodo")

def top_par_final(dias, titulo):
    st.write(f"**{titulo}**")
    desde = df["FECHA"].max() - timedelta(days=dias)
    sub = df[df["FECHA"] >= desde]
    pares = sub["R5"].str[-2:].value_counts()

    promedio = pares.mean()

    calientes = pares[pares >= promedio * 1.2].head(5)
    frios = pares[pares <= promedio * 0.8].head(5)

    if not calientes.empty:
        st.write("🔥 Calientes:")
        for n, c in calientes.items():
            st.write(f"• {n} → {c} apariciones (promedio esperado {promedio:.1f})")

    if not frios.empty:
        st.write("❄️ Fríos:")
        for n, c in frios.items():
            st.write(f"• {n} → {c} apariciones (promedio esperado {promedio:.1f})")

top_par_final(30, "Último mes")
top_par_final(180, "Últimos 6 meses")
top_par_final(365, "Último año")

st.markdown('</div>', unsafe_allow_html=True)

st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantía de premio.")
