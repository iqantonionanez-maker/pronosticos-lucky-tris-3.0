import streamlit as st
import pandas as pd

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Pronósticos Lucky TRIS",
    layout="centered"
)

# =========================
# ESTILOS (BLANCO)
# =========================
st.markdown("""
<style>
body { background-color: white; color: black; }
div[data-testid="metric-container"] {
    background-color: #f6f6f6;
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def procesar_csv(df):
    df.columns = df.columns.str.upper().str.strip()

    # CASO NUMERO
    if "NUMERO" in df.columns:
        df["NUMERO"] = (
            df["NUMERO"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.zfill(3)
        )
    else:
        posibles = [
            ("N1", "N2", "N3"),
            ("D1", "D2", "D3"),
            ("DIGITO1", "DIGITO2", "DIGITO3"),
        ]

        columnas = None
        for c in posibles:
            if all(col in df.columns for col in c):
                columnas = c
                break

        if columnas is None:
            st.error("❌ No se encontró columna NUMERO ni dígitos separados")
            st.stop()

        for c in columnas:
            df[c] = (
                pd.to_numeric(df[c], errors="coerce")
                .fillna(0)
                .astype(int)
                .astype(str)
            )

        df["NUMERO"] = df[columnas[0]] + df[columnas[1]] + df[columnas[2]]

    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    return df


# =========================
# UI CARGA ARCHIVO
# =========================
st.image("logo.png", width=150)
st.title("🍀 Pronósticos Lucky TRIS")

archivo = st.file_uploader(
    "📂 Sube el archivo CSV del TRIS",
    type=["csv"]
)

df = None

if archivo is not None:
    df_raw = pd.read_csv(archivo)
    df = procesar_csv(df_raw)
    st.success(f"✔ Sorteos cargados correctamente: {len(df)}")
else:
    st.info("⬆️ Sube el archivo CSV para iniciar el análisis")
    st.stop()

# =========================
# INPUT USUARIO
# =========================
numero = st.text_input("🔍 Analizar número", max_chars=3)
modalidad = st.selectbox(
    "Selecciona la modalidad",
    ["Número exacto", "Par final", "Impar final"]
)

# =========================
# ANÁLISIS
# =========================
if numero and numero.isdigit():

    numero = numero.zfill(3)

    if modalidad == "Par final":
        df_filtrado = df[df["NUMERO"].astype(int) % 2 == 0]
    elif modalidad == "Impar final":
        df_filtrado = df[df["NUMERO"].astype(int) % 2 != 0]
    else:
        df_filtrado = df

    apariciones = (df_filtrado["NUMERO"] == numero).sum()

    st.subheader("📊 Análisis estadístico")
    st.write(f"**Número analizado:** {numero}")
    st.write(f"**Apariciones históricas:** {apariciones}")

    fechas = df_filtrado.loc[df_filtrado["NUMERO"] == numero, "FECHA"]

    if not fechas.empty and fechas.notna().any():
        ultima = fechas.dropna().iloc[-1]
        st.write(f"**Última vez que salió:** {ultima.strftime('%d %B %Y')}")
    else:
        st.write("**Última vez que salió:** Nunca ha salido")

    promedio = df_filtrado["NUMERO"].value_counts().mean()

    if apariciones >= promedio * 1.2:
        st.success("🔥 Número caliente")
    elif apariciones <= promedio * 0.8:
        st.info("❄️ Número frío")
    else:
        st.warning("⚖️ Número neutro")

    # =========================
    # SIMILARES
    # =========================
    st.subheader("🔄 Números similares")
    base = int(numero)

    for n in range(base - 2, base + 3):
        if 0 <= n <= 999:
            n_str = str(n).zfill(3)
            cnt = (df_filtrado["NUMERO"] == n_str).sum()

            fechas_n = df_filtrado.loc[df_filtrado["NUMERO"] == n_str, "FECHA"]
            if not fechas_n.empty and fechas_n.notna().any():
                ultima_n = fechas_n.dropna().iloc[-1].strftime("%d %B %Y")
            else:
                ultima_n = "Nunca ha salido"

            st.write(f"• {n_str} → {cnt} apariciones | Última vez: {ultima_n}")

    # =========================
    # RECOMENDACIÓN
    # =========================
    st.subheader("🍀 Recomendaciones Lucky")
    if apariciones == 0:
        st.info("Número exploratorio.")
    elif apariciones > promedio:
        st.success("Buen historial.")
    else:
        st.warning("Frecuencia baja.")

    st.caption("⚠️ Análisis estadístico, no garantiza premios.")

