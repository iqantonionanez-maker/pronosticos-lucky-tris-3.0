import streamlit as st
import pandas as pd
from itertools import permutations
from datetime import date

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky – TRIS",
    layout="wide"
)

# ----------- ESTILOS VISUALES (PSICOLOGÍA DE COLORES) -----------
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #e5e7eb;
    }
    h1, h2, h3, h4 {
        color: #f8fafc;
    }
    .stMarkdown, .stText, .stWrite {
        color: #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎲 Pronósticos Lucky – TRIS")
st.write("Análisis estadístico basado únicamente en el histórico oficial del TRIS.")

st.markdown("""
**Disclaimer:**  
_Este análisis es únicamente estadístico e informativo.  
No garantiza premios ni resultados._
""")

CSV_LOCAL = "Tris.csv"

# ---------------- FUNCIONES AUXILIARES ----------------
def cargar_local():
    df = pd.read_csv(CSV_LOCAL)
    df["CONCURSO"] = df["CONCURSO"].astype(int)
    return df

def guardar(df):
    df = df.sort_values("CONCURSO", ascending=False)
    df.to_csv(CSV_LOCAL, index=False)

def normalizar_csv_externo(df):
    df.columns = [c.strip() for c in df.columns]

    df = df.rename(columns={
        "Sorteo": "CONCURSO",
        "Fecha": "FECHA"
    })

    if "Combinación Ganadora" in df.columns:
        df["Combinación Ganadora"] = df["Combinación Ganadora"].astype(str).str.zfill(5)
        df["R1"] = df["Combinación Ganadora"].str[0].astype(int)
        df["R2"] = df["Combinación Ganadora"].str[1].astype(int)
        df["R3"] = df["Combinación Ganadora"].str[2].astype(int)
        df["R4"] = df["Combinación Ganadora"].str[3].astype(int)
        df["R5"] = df["Combinación Ganadora"].str[4].astype(int)

    df["NPRODUCTO"] = 60
    df["Multiplicador"] = df.get("Multiplicador", "NO")

    return df[[
        "NPRODUCTO", "CONCURSO",
        "R1", "R2", "R3", "R4", "R5",
        "FECHA", "Multiplicador"
    ]]

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_LOCAL)
    df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y", errors="coerce")
    return df.sort_values("CONCURSO")

df = load_data()
total_sorteos = df["CONCURSO"].nunique()

# ---------------- SELECCIÓN DE MODALIDAD ----------------
st.subheader("🎯 Modalidad a analizar")

modalidad = st.selectbox(
    "Selecciona la modalidad:",
    [
        "Directa 5",
        "Directa 4",
        "Directa 3",
        "Par inicial",
        "Par final",
        "Número inicial",
        "Número final"
    ]
)

def extraer_valor(row):
    if modalidad == "Directa 5":
        return f"{row.R1}{row.R2}{row.R3}{row.R4}{row.R5}"
    if modalidad == "Directa 4":
        return f"{row.R2}{row.R3}{row.R4}{row.R5}"
    if modalidad == "Directa 3":
        return f"{row.R3}{row.R4}{row.R5}"
    if modalidad == "Par inicial":
        return f"{row.R1}{row.R2}"
    if modalidad == "Par final":
        return f"{row.R4}{row.R5}"
    if modalidad == "Número inicial":
        return f"{row.R1}"
    if modalidad == "Número final":
        return f"{row.R5}"

df["JUGADA"] = df.apply(extraer_valor, axis=1)
df_modalidad = df.dropna(subset=["JUGADA"])

# ---------------- ANÁLISIS PRINCIPAL ----------------
st.subheader("📊 Análisis estadístico")

seleccion = st.text_input("Ingresa el número a analizar:")

if seleccion and seleccion.isdigit():
    data = df_modalidad[df_modalidad["JUGADA"] == seleccion]
    apariciones = len(data)

    if apariciones > 0:
        max_concurso = df_modalidad["CONCURSO"].max()

        def conteo_rango(n):
            return len(data[data["CONCURSO"] > max_concurso - n])

        ultimas_fechas = (
            data.sort_values("FECHA", ascending=False)
            .head(5)["FECHA"]
            .dt.strftime("%d/%m/%Y")
            .tolist()
        )

        st.markdown(f"""
### 🔢 Frecuencia del número **{seleccion}**
- Ha aparecido **{apariciones} veces** en todo el histórico  
- **{conteo_rango(10000)} veces** en los últimos **10,000 sorteos**  
- **{conteo_rango(1000)} veces** en los últimos **1,000 sorteos**  
- **{conteo_rango(500)} veces** en los últimos **500 sorteos**  
- **{conteo_rango(100)} veces** en los últimos **100 sorteos**
""")

        st.markdown("### 📅 Últimas 5 apariciones")
        for f in ultimas_fechas:
            st.write(f"• {f}")

    else:
        st.warning("Este número no ha salido en esta modalidad.")
