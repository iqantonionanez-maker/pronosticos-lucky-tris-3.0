import streamlit as st
import pandas as pd

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Pronósticos Lucky TRIS",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0f0f1a;
}
.block-container {
    padding: 2rem;
}
h1, h2, h3, h4 {
    color: #f5c77a;
}
p, span, li {
    color: #e6e6e6;
}
.stTextInput input, .stNumberInput input {
    background-color: #1b1b2f;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS (100% COMPATIBLE CON CSV TRIS REAL)
# =====================================================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")
    df.columns = df.columns.str.upper().str.strip()

    # Fecha segura
    df["FECHA"] = pd.to_datetime(
        df["FECHA"],
        dayfirst=True,
        errors="coerce"
    )
    df = df.dropna(subset=["FECHA"])

    # Renombrar sorteo
    if "CONCURSO" in df.columns:
        df = df.rename(columns={"CONCURSO": "SORTEO"})
    else:
        st.error("❌ El archivo no tiene la columna CONCURSO")
        st.stop()

    # Limpiar dígitos R1–R5 (pueden venir con NaN)
    for col in ["R1", "R2", "R3", "R4", "R5"]:
        if col not in df.columns:
            st.error(f"❌ Falta la columna {col} en el CSV")
            st.stop()

        df[col] = (
            df[col]
            .fillna(0)
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.zfill(1)
        )

    # Construir número TRIS real
    df["NUMERO"] = df["R1"] + df["R2"] + df["R3"] + df["R4"] + df["R5"]

    # Derivados de juego
    df["PAR_FINAL"] = df["NUMERO"].str[-2:]
    df["PAR_INICIAL"] = df["NUMERO"].str[:2]
    df["D3"] = df["NUMERO"].str[-3:]
    df["D4"] = df["NUMERO"].str[-4:]
    df["D5"] = df["NUMERO"]

    return df.sort_values("SORTEO")

df = cargar_datos()

# =====================================================
# PREMIOS OFICIALES TRIS
# =====================================================
PREMIOS = {
    "PAR": 50,
    "D3": 500,
    "D4": 5000,
    "D5": 50000
}
MULTIPLICADOR = 4

# =====================================================
# FUNCIONES
# =====================================================
def estadistica(col, valor):
    data = df[df[col] == valor]
    if data.empty:
        return None

    ultimo = data.iloc[-1]
    promedio = data["SORTEO"].diff().mean()
    sin_salir = df["SORTEO"].max() - ultimo["SORTEO"]

    return {
        "apariciones": len(data),
        "fecha": ultimo["FECHA"].strftime("%d/%m/%Y"),
        "ultimo_sorteo": int(ultimo["SORTEO"]),
        "promedio": int(promedio) if not pd.isna(promedio) else None,
        "sin_salir": int(sin_salir)
    }

def top_modalidad(col):
    conteo = df[col].value_counts()
    promedio = conteo.mean()
    return (
        conteo[conteo > promedio].head(5),
        conteo[conteo < promedio].tail(5)
    )

# =====================================================
# INTERFAZ
# =====================================================
st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS basado en historial real")
st.success(f"Sorteos cargados correctamente: {len(df)}")

numero = st.text_input("🔍 Ingresa tu número (1 a 5 dígitos)").strip()
apuesta = st.number_input("💰 Monto a apostar ($)", min_value=1, max_value=500, value=10)
usar_multiplicador = st.checkbox("Usar Tris Multiplicador")

# =====================================================
# ANÁLISIS
# =====================================================
if numero.isdigit() and 1 <= len(numero) <= 5:
    numero = numero.zfill(5)

    st.header("📊 Análisis de tu número")

    est = estadistica("D5", numero)
    if not est:
        st.warning(f"El número {numero} no tiene apariciones históricas.")
    else:
        st.success(
            f"La última vez que salió fue en el sorteo {est['ultimo_sorteo']} "
            f"el día {est['fecha']}"
        )
        st.write(f"Apariciones totales: {est['apariciones']}")
        st.write(f"Promedio entre apariciones: {est['promedio']} sorteos")
        st.write(f"Sorteos sin salir: {est['sin_salir']}")

    st.header("🔍 Recomendaciones relacionadas")

    for nombre, col, val in [
        ("Par Final", "PAR_FINAL", numero[-2:]),
        ("Par Inicial", "PAR_INICIAL", numero[:2]),
        ("Directa 3", "D3", numero[-3:]),
        ("Directa 4", "D4", numero[-4:])
    ]:
        e = estadistica(col, val)
        if e:
            st.write(
                f"{nombre} {val} → {e['sin_salir']} sorteos sin salir | "
                f"Última vez: {e['fecha']}"
            )
        else:
            st.write(f"{nombre} {val} → Sin historial")

    st.header("🔥❄️ Tops")
    for titulo, col in [
        ("Par Final", "PAR_FINAL"),
        ("Directa 3", "D3"),
        ("Directa 4", "D4"),
        ("Directa 5", "D5")
    ]:
        calientes, frios = top_modalidad(col)
        st.subheader(titulo)
        st.write("🔥 Calientes:", ", ".join(calientes.index))
        st.write("❄️ Fríos:", ", ".join(frios.index))

    st.header("🍀 Recomendación Lucky")

    mult = MULTIPLICADOR if usar_multiplicador else 1
    st.write(f"🟢 Conservadora: Par Final {numero[-2:]} → ${PREMIOS['PAR'] * apuesta * mult:,}")
    st.write(f"🟡 Intermedia: Directa 3 {numero[-3:]} → ${PREMIOS['D3'] * apuesta * mult:,}")
    st.write(f"🔴 Agresiva: Directa 5 {numero} → ${PREMIOS['D5'] * apuesta * mult:,}")

    st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantía de premio.")

else:
    st.info("Ingresa un número válido para comenzar.")
