import streamlit as st
import pandas as pd
from itertools import permutations
from datetime import date

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky – TRIS",
    layout="wide"
)

# ---------------- ESTILOS VISUALES (SIN TOCAR LÓGICA) ----------------
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
    if "Multiplicador" in df.columns:
        df["Multiplicador"] = df["Multiplicador"].str.upper().replace({"SÍ": "SI"})
    else:
        df["Multiplicador"] = "NO"

    return df[[
        "NPRODUCTO",
        "CONCURSO",
        "R1", "R2", "R3", "R4", "R5",
        "FECHA",
        "Multiplicador"
    ]]

# ---------------- ACTUALIZACIÓN DEL HISTÓRICO ----------------
with st.expander("🔄 Actualización del histórico", expanded=False):

    df_local = cargar_local()
    ultimo_concurso = df_local["CONCURSO"].max()
    st.info(f"📄 Último concurso registrado: {ultimo_concurso}")

    st.markdown("### 📤 Actualizar desde archivo oficial")
    archivo = st.file_uploader("Sube el CSV oficial del TRIS", type=["csv"])

    if archivo is not None:
        try:
            df_nuevo = pd.read_csv(archivo)
            df_nuevo = normalizar_csv_externo(df_nuevo)
            nuevos = df_nuevo[df_nuevo["CONCURSO"] > ultimo_concurso]

            if nuevos.empty:
                st.warning("No hay sorteos nuevos en el archivo.")
            else:
                df_final = pd.concat([df_local, nuevos], ignore_index=True)
                guardar(df_final)
                st.success(f"✅ Se agregaron {len(nuevos)} sorteos nuevos.")
                st.experimental_rerun()

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

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
                st.success(f"✅ Sorteo {concurso_manual} agregado.")
                st.experimental_rerun()

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

# ---------------- EXTRACCIÓN DE JUGADA ----------------
def extraer_valor(row):
    try:
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
    except:
        return None

df["JUGADA"] = df.apply(extraer_valor, axis=1)
df_modalidad = df.dropna(subset=["JUGADA"])

# ---------------- ANÁLISIS ESTADÍSTICO (MEJORADO, FUNCIONAL) ----------------
st.subheader("📊 Análisis estadístico")

seleccion = st.text_input("Ingresa el número a analizar:")

if seleccion and seleccion.isdigit():

    data = df_modalidad[df_modalidad["JUGADA"] == seleccion]
    max_concurso = df_modalidad["CONCURSO"].max()

    def conteo_rango(n):
        return len(
            df_modalidad[
                (df_modalidad["CONCURSO"] > max_concurso - n) &
                (df_modalidad["JUGADA"] == seleccion)
            ]
        )

    apariciones = len(data)

    ult_fechas = (
        data.sort_values("FECHA", ascending=False)
        .head(5)["FECHA"]
        .dt.strftime("%d/%m/%Y")
        .tolist()
    )

    if apariciones > 0:
        ultimo_concurso = data["CONCURSO"].max()
        sorteos_sin_salir = max_concurso - ultimo_concurso
        promedio = total_sorteos / apariciones

        if sorteos_sin_salir >= promedio * 1.2:
            estado = "🔥 Caliente"
        elif sorteos_sin_salir <= promedio * 0.8:
            estado = "❄️ Frío"
        else:
            estado = "⚪ Promedio"
    else:
        sorteos_sin_salir = "N/A"
        promedio = "N/A"
        estado = "Sin datos"

    st.markdown(f"""
### 🔢 Frecuencia del número **{seleccion}**
- Ha aparecido **{apariciones} veces en todo el histórico**
- **{conteo_rango(10000)} veces** en los últimos **10,000 sorteos**
- **{conteo_rango(1000)} veces** en los últimos **1,000 sorteos**
- **{conteo_rango(500)} veces** en los últimos **500 sorteos**
- **{conteo_rango(100)} veces** en los últimos **100 sorteos**
""")

    st.markdown("### 📅 Últimas 5 apariciones")
    if ult_fechas:
        for f in ult_fechas:
            st.write(f"• {f}")
    else:
        st.write("Nunca ha salido.")

    st.markdown("### 📌 Estado estadístico")
    st.write(f"**Sorteos sin salir:** {sorteos_sin_salir}")
    st.write(f"**Promedio histórico:** {round(promedio,2) if promedio!='N/A' else 'N/A'}")
    st.write(f"**Clasificación:** {estado}")
