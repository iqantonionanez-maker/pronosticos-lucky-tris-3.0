import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN VISUAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky",
    page_icon="🎲",
    layout="centered"
)

st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.block-container {
    background-color: #020617;
    padding: 2rem;
    border-radius: 12px;
}
h1, h2, h3, label {
    color: #e5e7eb;
}
.stTextInput input {
    background-color: #020617;
    color: white;
}
.info-box {
    background-color: #020617;
    border-left: 5px solid #3b82f6;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
}
.good {color:#22c55e;}
.bad {color:#ef4444;}
.neutral {color:#e5e7eb;}
</style>
""", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
    df["NUMERO"] = df["NUMERO"].astype(str).str.zfill(5)
    return df

df = cargar_datos()

# ---------------- FUNCIONES ----------------
def extraer_modalidad(numero, modalidad):
    if modalidad == "Número final":
        return numero[-1]
    if modalidad == "Número inicial":
        return numero[0]
    if modalidad == "Par final":
        return numero[-2:]
    if modalidad == "Par inicial":
        return numero[:2]
    if modalidad == "Directa 3":
        return numero[-3:]
    if modalidad == "Directa 4":
        return numero[-4:]
    if modalidad == "Directa 5":
        return numero
    return None

def clasificar_caliente(conteo, promedio):
    if conteo > promedio * 1.2:
        return "🔥 Caliente", "good", "Sale más que el promedio histórico."
    elif conteo < promedio * 0.8:
        return "❄️ Frío", "bad", "Sale menos que el promedio histórico."
    else:
        return "⚪ Promedio", "neutral", "Tiene un comportamiento similar al resto."

# ---------------- INTERFAZ ----------------
st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS")

st.success(f"Sorteos cargados correctamente: {len(df)}")

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

# ---------------- ANÁLISIS ----------------
if numero_usuario:
    numero_usuario = numero_usuario.zfill(5)
    valor = extraer_modalidad(numero_usuario, modalidad)

    if valor:
        if modalidad == "Directa 5":
            serie = df["NUMERO"]
        elif modalidad in ["Directa 4", "Directa 3"]:
            n = int(modalidad[-1])
            serie = df["NUMERO"].str[-n:]
        elif modalidad == "Par final":
            serie = df["NUMERO"].str[-2:]
        elif modalidad == "Par inicial":
            serie = df["NUMERO"].str[:2]
        elif modalidad == "Número final":
            serie = df["NUMERO"].str[-1]
        elif modalidad == "Número inicial":
            serie = df["NUMERO"].str[0]

        total_apariciones = (serie == valor).sum()
        promedio = serie.value_counts().mean()

        st.subheader("📊 Análisis estadístico")
        st.write(f"**Apariciones históricas:** {total_apariciones}")

        if total_apariciones > 0:
            ultima = df[serie == valor].iloc[-1]
            fecha = ultima["FECHA"].strftime("%d/%m/%Y")
            sorteo = ultima["SORTEO"]
            st.write(f"**Última aparición:** {fecha} (Sorteo #{sorteo})")
        else:
            st.write("**Última aparición:** Nunca ha salido")

        estado, clase, texto = clasificar_caliente(total_apariciones, promedio)
        st.markdown(
            f"<div class='info-box {clase}'>{estado} — {texto}</div>",
            unsafe_allow_html=True
        )

        st.caption("Análisis basado en comportamiento histórico del TRIS. No garantiza resultados.")

