import streamlit as st
import pandas as pd
from itertools import permutations
from datetime import date

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky – TRIS",
    layout="wide"
)

# ---------------- ESTILOS (PSICOLOGÍA DE COLOR) ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0e1a24;
    color: #f5f7fa;
}
h1, h2, h3 {
    color: #e8f1f8;
}
p, label, span {
    color: #d6dde5;
}
input, textarea {
    background-color: #1b2a38 !important;
    color: #ffffff !important;
}
[data-testid="stDataFrame"] {
    background-color: #1b2a38;
}
.stAlert-success {
    background-color: #1f3d2b;
    color: #c8facc;
}
.stAlert-info {
    background-color: #1c3347;
    color: #d6ecff;
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
    df = df.rename(columns={"Sorteo": "CONCURSO", "Fecha": "FECHA"})

    if "Combinación Ganadora" in df.columns:
        df["Combinación Ganadora"] = df["Combinación Ganadora"].astype(str).str.zfill(5)
        for i in range(5):
            df[f"R{i+1}"] = df["Combinación Ganadora"].str[i].astype(int)

    df["NPRODUCTO"] = 60
    df["Multiplicador"] = df.get("Multiplicador", "NO").astype(str).str.upper().replace({"SÍ": "SI"})

    return df[["NPRODUCTO", "CONCURSO", "R1", "R2", "R3", "R4", "R5", "FECHA", "Multiplicador"]]

# ---------------- ACTUALIZACIÓN HISTÓRICO ----------------
with st.expander("🔄 Actualización del histórico"):
    df_local = cargar_local()
    ultimo_concurso = df_local["CONCURSO"].max()
    st.info(f"📄 Último concurso registrado: {ultimo_concurso}")

    archivo = st.file_uploader("Sube el CSV oficial del TRIS", type=["csv"])
    if archivo:
        df_nuevo = normalizar_csv_externo(pd.read_csv(archivo))
        nuevos = df_nuevo[df_nuevo["CONCURSO"] > ultimo_concurso]
        if nuevos.empty:
            st.warning("No hay sorteos nuevos.")
        else:
            guardar(pd.concat([df_local, nuevos]))
            st.success(f"✅ Se agregaron {len(nuevos)} sorteos.")
            st.experimental_rerun()

    with st.form("captura_manual"):
        numero = st.text_input("Número ganador (5 dígitos)")
        multiplicador = st.selectbox("¿Salió multiplicador?", ["NO", "SI"])
        fecha = st.date_input("Fecha", value=date.today())
        enviar = st.form_submit_button("Guardar sorteo")

        if enviar and numero.isdigit() and len(numero) == 5:
            nuevo = {
                "NPRODUCTO": 60,
                "CONCURSO": ultimo_concurso + 1,
                "R1": int(numero[0]),
                "R2": int(numero[1]),
                "R3": int(numero[2]),
                "R4": int(numero[3]),
                "R5": int(numero[4]),
                "FECHA": fecha.strftime("%d/%m/%Y"),
                "Multiplicador": multiplicador
            }
            guardar(pd.concat([df_local, pd.DataFrame([nuevo])]))
            st.success("✅ Sorteo agregado.")
            st.experimental_rerun()

# ---------------- CARGA DATOS ----------------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_LOCAL)
    df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y", errors="coerce")
    return df.sort_values("CONCURSO")

df = load_data()
total_sorteos = df["CONCURSO"].nunique()

# ---------------- MODALIDAD ----------------
modalidad = st.selectbox("🎯 Modalidad", [
    "Directa 5","Directa 4","Directa 3",
    "Par inicial","Par final","Número inicial","Número final"
])

def extraer_valor(row):
    if modalidad == "Directa 5": return f"{row.R1}{row.R2}{row.R3}{row.R4}{row.R5}"
    if modalidad == "Directa 4": return f"{row.R2}{row.R3}{row.R4}{row.R5}"
    if modalidad == "Directa 3": return f"{row.R3}{row.R4}{row.R5}"
    if modalidad == "Par inicial": return f"{row.R1}{row.R2}"
    if modalidad == "Par final": return f"{row.R4}{row.R5}"
    if modalidad == "Número inicial": return f"{row.R1}"
    if modalidad == "Número final": return f"{row.R5}"

df["JUGADA"] = df.apply(extraer_valor, axis=1)
df_modalidad = df.dropna()

# ---------------- ANÁLISIS ESTADÍSTICO ----------------
st.subheader("📊 Análisis estadístico")

seleccion = st.text_input("Ingresa el número a analizar:")

if seleccion and seleccion.isdigit():
    max_conc = df_modalidad["CONCURSO"].max()
    data = df_modalidad[df_modalidad["JUGADA"] == seleccion]

    def rango(n):
        return len(data[data["CONCURSO"] > max_conc - n])

    ult_fechas = (
        data.sort_values("FECHA", ascending=False)
        .head(5)["FECHA"].dt.strftime("%d/%m/%Y").tolist()
    )

    st.markdown(f"""
### 🔢 Frecuencia del número {seleccion}
- **{len(data)} veces** en todo el histórico  
- **{rango(10000)} veces** en los últimos **10,000 sorteos**  
- **{rango(1000)} veces** en los últimos **1,000 sorteos**  
- **{rango(500)} veces** en los últimos **500 sorteos**  
- **{rango(100)} veces** en los últimos **100 sorteos**
""")

    st.markdown("### 📅 Últimas 5 apariciones")
    for f in ult_fechas or ["Nunca"]:
        st.write(f"• {f}")
