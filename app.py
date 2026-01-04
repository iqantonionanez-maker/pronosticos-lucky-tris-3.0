import streamlit as st
import pandas as pd
import os

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🎲",
    layout="centered"
)

# -------------------------------------------------
# LOGO
# -------------------------------------------------
if os.path.exists("logolucky.jpg"):
    st.image("logolucky.jpg", width=220)

st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS (Lotería Nacional)")

# -------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    columnas = ["R1", "R2", "R3", "R4", "R5"]
    for c in columnas:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=columnas)

    df["numero"] = (
        df["R1"].astype(int).astype(str) +
        df["R2"].astype(int).astype(str) +
        df["R3"].astype(int).astype(str) +
        df["R4"].astype(int).astype(str) +
        df["R5"].astype(int).astype(str)
    ).str.zfill(5)

    df["num_inicial"] = df["numero"].str[:1]
    df["num_final"] = df["numero"].str[-1]
    df["par_inicial"] = df["numero"].str[:2]
    df["par_final"] = df["numero"].str[-2:]
    df["directa_3"] = df["numero"].str[-3:]
    df["directa_4"] = df["numero"].str[-4:]
    df["directa_5"] = df["numero"]

    return df

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# -------------------------------------------------
# MODALIDADES
# -------------------------------------------------
MODALIDADES = {
    "Número inicial":  {"col": "num_inicial", "digitos": 1, "premio": 5},
    "Número final":    {"col": "num_final", "digitos": 1, "premio": 5},
    "Par inicial":     {"col": "par_inicial", "digitos": 2, "premio": 50},
    "Par final":       {"col": "par_final", "digitos": 2, "premio": 50},
    "Directa 3":       {"col": "directa_3", "digitos": 3, "premio": 500},
    "Directa 4":       {"col": "directa_4", "digitos": 4, "premio": 5000},
    "Directa 5":       {"col": "directa_5", "digitos": 5, "premio": 50000},
}

# -------------------------------------------------
# ANÁLISIS
# -------------------------------------------------
st.markdown("## 🔍 Analizar número")

numero = st.text_input(
    "Ingresa el número que deseas analizar",
    max_chars=5,
    placeholder="Ej: 21, 345, 7890, 12345"
)

modalidad = st.selectbox(
    "Selecciona la modalidad",
    list(MODALIDADES.keys()),
    index=3  # Par final por default
)

config = MODALIDADES[modalidad]
col = config["col"]
digitos = config["digitos"]

# -------------------------------------------------
# RANKING
# -------------------------------------------------
st.markdown("## 🏆 Ranking histórico")

conteo = df[col].value_counts()

top_calientes = conteo.head(10).reset_index()
top_calientes.columns = ["Número", "Apariciones"]

top_frios = conteo.tail(10).reset_index()
top_frios.columns = ["Número", "Apariciones"]

col1, col2 = st.columns(2)

with col1:
    st.markdown("🔥 Más frecuentes")
    st.dataframe(top_calientes, hide_index=True)

with col2:
    st.markdown("❄️ Menos frecuentes")
    st.dataframe(top_frios, hide_index=True)

# -------------------------------------------------
# VALIDACIÓN NÚMERO
# -------------------------------------------------
if numero:
    numero = numero.strip()

    if not numero.isdigit():
        st.error("Solo se permiten números.")
        st.stop()

    if len(numero) != digitos:
        st.error(f"Esta modalidad requiere exactamente {digitos} dígitos.")
        st.stop()

    numero = numero.zfill(digitos)

    # -------------------------------------------------
    # APUESTA
    # -------------------------------------------------
    st.markdown("## 💰 Datos de la jugada")

    apuesta = st.number_input(
        "Cantidad a jugar (pesos)",
        min_value=1,
        max_value=100,
        value=1
    )

    usar_mult = st.radio(
        "¿Jugar con multiplicador?",
        ["No", "Sí"],
        horizontal=True
    )

    mult = 1
    if usar_mult == "Sí":
        mult = st.number_input(
            "Selecciona multiplicador",
            min_value=1,
            max_value=apuesta,
            value=1
        )

        if apuesta + mult > 100:
            st.error("La suma de TRIS + multiplicador no puede exceder $100.")
            st.stop()

    # -------------------------------------------------
    # BOTÓN
    # -------------------------------------------------
    if st.button("🎯 Analizar jugada"):
        apariciones = (df[col] == numero).sum()
        ultimo = df[df[col] == numero].tail(1)

        st.markdown("## 📊 Análisis básico")

        st.write(f"🔢 Número analizado: **{numero}**")
        st.write(f"🎰 Modalidad: **{modalidad}**")
        st.write(f"📈 Apariciones históricas: **{apariciones}**")

        if ultimo.empty:
            st.write("📅 Última aparición: **Nunca ha salido**")
        else:
            st.write("📅 Última aparición: **Registrada en el histórico**")

        st.markdown("## 💵 Ganancia máxima posible")

        premio = apuesta * config["premio"]
        premio_total = premio * mult

        st.write(f"💰 Premio base: **${premio:,.0f}**")
        st.write(f"🚀 Premio máximo posible: **${premio_total:,.0f}**")

        st.caption(
            "Este análisis se basa en comportamiento estadístico histórico. "
            "Pronósticos Lucky te desea buena suerte 🍀"
        )
