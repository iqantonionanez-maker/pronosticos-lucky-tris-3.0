import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN VISUAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🍀",
    layout="centered"
)

st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.big-title {
    font-size:32px;
    font-weight:bold;
    color:#2ecc71;
}
.card {
    background-color:#161b22;
    padding:15px;
    border-radius:10px;
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
st.image("logolucky.jpg", width=200)

st.markdown('<div class="big-title">🎲 Pronósticos Lucky</div>', unsafe_allow_html=True)
st.caption("Análisis estadístico del TRIS (solo informativo)")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Crear número completo
    df["NUMERO"] = (
        df["R1"].astype(str)
        + df["R2"].astype(str)
        + df["R3"].astype(str)
        + df["R4"].astype(str)
        + df["R5"].astype(str)
    )

    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
    return df

df = cargar_datos()

st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- INPUT USUARIO ----------------
st.markdown("## 🔍 Analizar número")

numero_usuario = st.text_input("Ingresa el número", "").strip()

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

def extraer_numero(numero, modalidad):
    if modalidad == "Par final":
        return numero[-2:]
    if modalidad == "Número final":
        return numero[-1]
    if modalidad == "Par inicial":
        return numero[:2]
    if modalidad == "Número inicial":
        return numero[:1]
    if modalidad == "Directa 3":
        return numero[-3:]
    if modalidad == "Directa 4":
        return numero[-4:]
    if modalidad == "Directa 5":
        return numero.zfill(5)
    return None

# ---------------- ANÁLISIS ----------------
if numero_usuario.isdigit() and len(numero_usuario) <= 5:

    objetivo = extraer_numero(numero_usuario.zfill(5), modalidad)

    if objetivo:
        if modalidad in ["Par final", "Número final", "Directa 3", "Directa 4"]:
            serie = df["NUMERO"].str[-len(objetivo):]
        elif modalidad in ["Par inicial", "Número inicial"]:
            serie = df["NUMERO"].str[:len(objetivo)]
        else:
            serie = df["NUMERO"]

        apariciones = df[serie == objetivo]

        total = len(apariciones)

        st.markdown("## 📊 Análisis estadístico")

        st.markdown(f"**Apariciones históricas:** {total}")

        if total > 0:
            ultima = apariciones.iloc[-1]
            st.markdown(
                f"**Última aparición:** Sorteo #{ultima['CONCURSO']} "
                f"({ultima['FECHA'].date()})"
            )
        else:
            st.markdown("**Última aparición:** Nunca ha salido")

        # --------- CALIENTE / FRÍO ----------
        promedio = len(df) / len(serie.unique())
        ratio = total / promedio if promedio > 0 else 0

        if ratio >= 1.2:
            st.success("🔥 Número caliente — aparece más que el promedio histórico.")
        elif ratio <= 0.8:
            st.info("❄️ Número frío — aparece menos que el promedio histórico.")
        else:
            st.warning("⚪ Comportamiento promedio — similar al resto.")

        st.caption(
            "Caliente = ≥20% más apariciones que el promedio | "
            "Frío = ≥20% menos apariciones"
        )

        # --------- COMPARACIONES ----------
        st.markdown("## 🔄 Números similares")
        similares = []
        try:
            n = int(objetivo)
            for i in range(-2, 3):
                if i != 0:
                    similares.append(str(n + i).zfill(len(objetivo)))
        except:
            pass

        for s in similares:
            cnt = (serie == s).sum()
            st.markdown(f"- {s}: {cnt} apariciones")

        # --------- AVISO LEGAL ----------
        st.divider()
        st.caption(
            "⚠️ Este análisis es únicamente estadístico e informativo. "
            "No garantiza premios ni resultados."
        )

else:
    st.info("Ingresa un número válido (1 a 5 dígitos).")

st.markdown("🍀 **Pronósticos Lucky** — suerte informada")
