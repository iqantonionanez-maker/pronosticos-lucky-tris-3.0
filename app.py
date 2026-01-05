import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    layout="centered"
)

# ---------------- ESTILOS ----------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: #e5e7eb;
}
.block-container {
    background-color: #020617;
    padding: 2rem;
    border-radius: 12px;
}
.metric-box {
    background-color: #020617;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
st.image("logolucky.jpg", use_container_width=True)

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS (solo informativo)")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Normalizar nombres
    df.columns = [c.upper() for c in df.columns]

    # Detectar columnas R1-R5
    r_cols = [c for c in df.columns if c.startswith("R")]

    # Crear número completo SIN ceros artificiales
    df["NUMERO"] = df[r_cols].astype(str).agg("".join, axis=1)

    # Fecha
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    return df

df = cargar_datos()
total_sorteos = len(df)

st.success(f"Sorteos cargados correctamente: {total_sorteos}")

# ---------------- FUNCIONES ----------------
def obtener_parte(numero, modalidad):
    if modalidad == "Par final":
        return numero[-2:]
    if modalidad == "Par inicial":
        return numero[:2]
    if modalidad == "Número final":
        return numero[-1]
    if modalidad == "Número inicial":
        return numero[:1]
    if modalidad == "Directa 3":
        return numero[-3:]
    if modalidad == "Directa 4":
        return numero[-4:]
    return numero

def conteo_modalidad(modalidad):
    return df["NUMERO"].apply(lambda x: obtener_parte(x, modalidad))

def estadisticas(valor, modalidad):
    serie = conteo_modalidad(modalidad)
    apariciones = (serie == valor).sum()

    if apariciones == 0:
        return 0, None, None, None

    ultimo = df[serie == valor].iloc[-1]
    fecha = ultimo["FECHA"].strftime("%d %B %Y")
    sorteo = ultimo.get("SORTEO", "N/D")

    ultimos_100 = serie.tail(100)
    ultimos_30 = serie.tail(30)

    return (
        apariciones,
        f"Sorteo #{sorteo} – {fecha}",
        (ultimos_30 == valor).sum(),
        (ultimos_100 == valor).sum()
    )

def estado_caliente(apariciones, total, total_valores):
    promedio = total / total_valores
    if apariciones >= promedio * 1.2:
        return "🔥 Número caliente — aparece ≥20% más que el promedio."
    if apariciones <= promedio * 0.8:
        return "❄️ Número frío — aparece ≥20% menos que el promedio."
    return "⚪ Comportamiento promedio."

# ---------------- INPUT USUARIO ----------------
st.subheader("🔍 Analizar número")

numero_usuario = st.text_input("Ingresa el número").strip()

modalidad = st.selectbox(
    "Selecciona la modalidad",
    [
        "Par final",
        "Número final",
        "Par inicial",
        "Número inicial",
        "Directa 3",
        "Directa 4",
        "Directa 5"
    ],
    index=0
)

if numero_usuario.isdigit():
    valor = obtener_parte(numero_usuario, modalidad)

    st.markdown(f"🎯 **Modalidad:** {modalidad}")
    st.markdown(f"🔎 **Número analizado:** {valor}")

    apar, ultima, ult30, ult100 = estadisticas(valor, modalidad)

    st.subheader("📊 Análisis estadístico")

    st.markdown(f"""
    <div class="metric-box">
    <b>Apariciones históricas:</b> {apar}<br>
    <b>Última aparición:</b> {ultima if ultima else "Nunca ha salido"}
    </div>
    """, unsafe_allow_html=True)

    estado = estado_caliente(
        apar,
        total_sorteos,
        conteo_modalidad(modalidad).nunique()
    )
    st.info(estado)

    st.caption(
        "🔥 Caliente = ≥20% más apariciones | ❄️ Frío = ≥20% menos apariciones"
    )

    # --------- NÚMEROS SIMILARES ---------
    st.subheader("🔄 Números similares")

    try:
        base = int(valor)
        similares = [str(base-2), str(base-1), str(base+1), str(base+2)]
    except:
        similares = []

    for s in similares:
        a, u, _, _ = estadisticas(s, modalidad)
        st.write(f"**{s}** → {a} apariciones | Última vez: {u or 'Nunca'}")

    # --------- RECOMENDACIONES LUCKY ---------
    st.subheader("🍀 Recomendaciones Lucky")

    serie = conteo_modalidad(modalidad)
    conteo = serie.value_counts()

    promedio = total_sorteos / conteo.size

    candidatos = []
    for num, cnt in conteo.items():
        if cnt < promedio:
            ultimo = df[serie == num].iloc[-1]
            dias = (df.iloc[-1]["FECHA"] - ultimo["FECHA"]).days
            candidatos.append((num, cnt, dias))

    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)[:3]

    if candidatos:
        for n, c, d in candidatos:
            st.markdown(f"""
            **{n}**  
            📅 Última vez que salió: {df[serie == n].iloc[-1]["FECHA"].strftime("%d %B %Y")}  
            📊 Apariciones históricas: {c}  
            ⏳ Lleva {d} días sin salir  
            📈 Históricamente aparece cada ~{int(total_sorteos/c)} sorteos
            """)
    else:
        st.write("No se detectaron recomendaciones estadísticas claras.")

    st.warning(
        "⚠️ Este análisis es únicamente estadístico e informativo. "
        "No garantiza premios ni resultados."
    )

    st.markdown("🍀 **Pronósticos Lucky — suerte informada**")

else:
    st.info("Ingresa solo números para iniciar el análisis.")
