import streamlit as st
import pandas as pd

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    layout="centered"
)

# ---------------- ESTILO CLARO ----------------
st.markdown("""
<style>
body {
    background-color: #ffffff;
    color: #000000;
}
.block-container {
    background-color: #ffffff;
    padding: 2rem;
}
.metric-box {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logolucky.jpg", width=180)

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS (solo informativo)")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df.columns = [c.upper() for c in df.columns]

    r_cols = [c for c in df.columns if c.startswith("R")]
    df["NUMERO"] = df[r_cols].astype(str).agg("".join, axis=1)

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

def serie_modalidad(modalidad):
    return df["NUMERO"].apply(lambda x: obtener_parte(x, modalidad))

def ultima_info(valor, modalidad):
    serie = serie_modalidad(modalidad)
    coincidencias = df[serie == valor]

    if coincidencias.empty:
        return "Nunca ha salido"

    fila = coincidencias.iloc[-1]
    if pd.isna(fila["FECHA"]):
        return "Fecha no disponible"

    return fila["FECHA"].strftime("%d %B %Y")

def estado_caliente(apariciones, total, universo):
    promedio = total / universo
    if apariciones >= promedio * 1.2:
        return "🔥 Número caliente — aparece ≥20% más que el promedio."
    if apariciones <= promedio * 0.8:
        return "❄️ Número frío — aparece ≥20% menos que el promedio."
    return "⚪ Comportamiento promedio."

# ---------------- INPUT ----------------
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
    serie = serie_modalidad(modalidad)

    apariciones = (serie == valor).sum()
    ultima = ultima_info(valor, modalidad)

    st.subheader("📊 Análisis estadístico")
    st.markdown(f"""
    <div class="metric-box">
    <b>Número analizado:</b> {valor}<br>
    <b>Apariciones históricas:</b> {apariciones}<br>
    <b>Última vez que salió:</b> {ultima}
    </div>
    """, unsafe_allow_html=True)

    estado = estado_caliente(
        apariciones,
        total_sorteos,
        serie.nunique()
    )
    st.info(estado)

    st.caption(
        "Caliente = ≥20% más apariciones | Frío = ≥20% menos apariciones"
    )

    # ---------------- NÚMEROS SIMILARES ----------------
    st.subheader("🔄 Números similares")

    try:
        base = int(valor)
        similares = [str(base-2), str(base-1), str(base+1), str(base+2)]
    except:
        similares = []

    for s in similares:
        apar_s = (serie == s).sum()
        ult_s = ultima_info(s, modalidad)
        st.write(f"• **{s}** → {apar_s} apariciones | Última vez: {ult_s}")

    # ---------------- RECOMENDACIONES ----------------
    st.subheader("🍀 Recomendaciones Lucky")

    conteo = serie.value_counts()
    promedio = total_sorteos / conteo.size

    candidatos = []
    for num, cnt in conteo.items():
        if cnt < promedio:
            coincidencias = df[serie == num]
            if coincidencias.empty:
                continue
            fecha = coincidencias.iloc[-1]["FECHA"]
            if pd.isna(fecha):
                continue
            dias = (df.iloc[-1]["FECHA"] - fecha).days
            candidatos.append((num, cnt, dias))

    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)[:3]

    if candidatos:
        for n, c, d in candidatos:
            st.markdown(f"""
            **{n}**  
            📅 Última vez: {ultima_info(n, modalidad)}  
            📊 Apariciones: {c}  
            ⏳ Lleva {d} días sin salir  
            📈 Promedio histórico: cada ~{int(total_sorteos/c)} sorteos
            """)
    else:
        st.write("No se detectaron recomendaciones claras.")

    st.warning(
        "⚠️ Este análisis es únicamente estadístico e informativo. "
        "No garantiza premios ni resultados."
    )

    st.markdown("🍀 **Pronósticos Lucky — suerte informada**")

else:
    st.info("Ingresa solo números para iniciar el análisis.")
