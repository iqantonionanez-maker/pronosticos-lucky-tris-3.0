import streamlit as st
import pandas as pd
from itertools import permutations
from datetime import date

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky – TRIS",
    layout="wide"
)

st.title("🎲 Pronósticos Lucky – TRIS")
st.write("Análisis estadístico basado únicamente en el histórico oficial del TRIS.")

st.markdown("""
**Disclaimer:**  
_Este análisis es únicamente estadístico e informativo.  
No garantiza premios ni resultados._
""")

CSV_LOCAL = "Tris.csv"

# ---------------- FUNCIONES NUEVAS (NO TOCAN ANÁLISIS) ----------------
def cargar_local():
    df = pd.read_csv(CSV_LOCAL)
    df["CONCURSO"] = df["CONCURSO"].astype(int)
    return df

def guardar(df):
    df = df.sort_values("CONCURSO", ascending=False)
    df.to_csv(CSV_LOCAL, index=False)

def normalizar_csv_externo(df):
    df.columns = [c.strip() for c in df.columns]

    if "Combinación Ganadora" in df.columns:
        df["Combinación Ganadora"] = df["Combinación Ganadora"].astype(str).str.zfill(5)
        df["R1"] = df["Combinación Ganadora"].str[0].astype(int)
        df["R2"] = df["Combinación Ganadora"].str[1].astype(int)
        df["R3"] = df["Combinación Ganadora"].str[2].astype(int)
        df["R4"] = df["Combinación Ganadora"].str[3].astype(int)
        df["R5"] = df["Combinación Ganadora"].str[4].astype(int)

    df = df.rename(columns={
        "Sorteo": "CONCURSO",
        "Fecha": "FECHA"
    })

    df["NPRODUCTO"] = 60
    df["Multiplicador"] = df["Multiplicador"].str.upper().replace({"SÍ": "SI"})

    return df[[
        "NPRODUCTO", "CONCURSO",
        "R1", "R2", "R3", "R4", "R5",
        "FECHA", "Multiplicador"
    ]]

# ---------------- BLOQUE NUEVO: ACTUALIZACIÓN ----------------
st.subheader("🔄 Actualización del histórico")

df_local = cargar_local()
ultimo_concurso = df_local["CONCURSO"].max()

st.info(f"📄 Último concurso registrado: {ultimo_concurso}")

# ---- SUBIR CSV ----
st.markdown("### 📤 Actualizar desde archivo oficial")

archivo = st.file_uploader("Sube el CSV oficial del TRIS", type=["csv"])

if archivo:
    try:
        df_nuevo = pd.read_csv(archivo)
        df_nuevo = normalizar_csv_externo(df_nuevo)
        nuevos = df_nuevo[df_nuevo["CONCURSO"] > ultimo_concurso]

        if nuevos.empty:
            st.warning("No hay sorteos nuevos en el archivo.")
        else:
            df_final = pd.concat([df_local, nuevos], ignore_index=True)
            guardar(df_final)
            st.success(f"✅ Se agregaron {len(nuevos)} sorteos nuevos. Recarga la app.")
            st.stop()

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

# ---- CAPTURA MANUAL ----
st.markdown("### ✍️ Captura manual de sorteo")

with st.form("captura_manual"):
    concurso_manual = ultimo_concurso + 1
    numero = st.text_input("Número ganador (5 dígitos)")
    multiplicador = st.selectbox("¿Salió multiplicador?", ["NO", "SI"])
    fecha = st.date_input("Fecha del sorteo", value=date.today())
    enviar = st.form_submit_button("Guardar sorteo")

    if enviar:
        if not numero.isdigit() or len(numero) != 5:
            st.error("El número debe tener exactamente 5 dígitos.")
        else:
            nuevo = {
                "NPRODUCTO": 60,
                "CONCURSO": concurso_manual,
                "R1": int(numero[0]),
                "R2": int(numero[1]),
                "R3": int(numero[2]),
                "R4": int(numero[3]),
                "R5": int(numero[4]),
                "FECHA": fecha.strftime("%d/%m/%Y"),
                "Multiplicador": multiplicador
            }

            df_final = pd.concat([df_local, pd.DataFrame([nuevo])], ignore_index=True)
            guardar(df_final)
            st.success(f"✅ Sorteo {concurso_manual} agregado. Recarga la app.")
            st.stop()

# ---------------- CARGA DE DATOS (ORIGINAL) ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("Tris.csv")
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

# ---------------- EXTRACCIÓN DE JUGADA ----------------
def extraer_valor(row):
    try:
        if modalidad == "Directa 5":
            return f"{int(row.R1)}{int(row.R2)}{int(row.R3)}{int(row.R4)}{int(row.R5)}"
        if modalidad == "Directa 4":
            return f"{int(row.R2)}{int(row.R3)}{int(row.R4)}{int(row.R5)}"
        if modalidad == "Directa 3":
            return f"{int(row.R3)}{int(row.R4)}{int(row.R5)}"
        if modalidad == "Par inicial":
            return f"{int(row.R1)}{int(row.R2)}"
        if modalidad == "Par final":
            return f"{int(row.R4)}{int(row.R5)}"
        if modalidad == "Número inicial":
            return f"{int(row.R1)}"
        if modalidad == "Número final":
            return f"{int(row.R5)}"
    except:
        return None

df["JUGADA"] = df.apply(extraer_valor, axis=1)
df_modalidad = df.dropna(subset=["JUGADA"])

# ---------------- TODO LO DEMÁS QUEDA IGUAL ----------------
# (análisis, premios, similares, recomendaciones)
