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
.stButton button {
    background-color: #f5c77a;
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS (ROBUSTA)
# =====================================================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Normalizar nombres
    df.columns = df.columns.str.upper()

    # Fecha segura (formato mexicano + tolerante)
    df["FECHA"] = pd.to_datetime(
        df["FECHA"],
        dayfirst=True,
        errors="coerce"
    )

    # Eliminar registros inválidos
    df = df.dropna(subset=["FECHA"])

    # Asegurar tipos
    df["SORTEO"] = df["SORTEO"].astype(int)
    df["NUMERO"] = df["NUMERO"].astype(str).str.zfill(5)

    # Derivados de juego
    df["PAR_FINAL"] = df["NUMERO"].str[-2:]
    df["PAR_INICIAL"] = df["NUMERO"].str[:2]
    df["D3"] = df["NUMERO"].str[-3:]
    df["D4"] = df["NUMERO"].str[-4:]
    df["D5"] = df["NUMERO"]

    return df.sort_values("SORTEO")

df = cargar_datos()

# =====================================================
# CONSTANTES OFICIALES TRIS
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
        "ultimo_sorteo": int(ultimo["SORTEO"]),
        "fecha": ultimo["FECHA"].strftime("%d/%m/%Y"),
        "promedio": int(promedio) if not pd.isna(promedio) else None,
        "sin_salir": int(sin_salir)
    }

def top_modalidad(col, nombre):
    conteo = df[col].value_counts()
    promedio = conteo.mean()

    calientes = conteo[conteo > promedio].head(5)
    frios = conteo[conteo < promedio].tail(5)

    st.subheader(nombre)
    st.write("🔥 Calientes:", ", ".join(calientes.index) if not calientes.empty else "Sin datos")
    st.write("❄️ Fríos:", ", ".join(frios.index) if not frios.empty else "Sin datos")

# =====================================================
# INTERFAZ
# =====================================================
st.title("🎲 Pronósticos Lucky")
st.caption("Análisis estadístico del TRIS basado en historial real")

st.success(f"Sorteos cargados correctamente: {len(df)}")

st.markdown(
    "🔥 **Caliente**: aparece más que el promedio &nbsp;&nbsp;"
    "❄️ **Frío**: aparece menos que el promedio &nbsp;&nbsp;"
    "⚪ **Promedio**: comportamiento normal"
)

numero = st.text_input("🔍 Ingresa tu número (1 a 5 dígitos)").strip()
apuesta = st.number_input("💰 Monto a apostar ($)", min_value=1, max_value=500, value=10)
usar_multiplicador = st.checkbox("Usar Tris Multiplicador")

# =====================================================
# ANÁLISIS PRINCIPAL
# =====================================================
if numero.isdigit() and 1 <= len(numero) <= 5:
    numero = numero.zfill(5)

    st.header("📊 Análisis de tu número")

    est = estadistica("D5", numero)

    if not est:
        st.warning(f"El número {numero} no tiene apariciones históricas registradas.")
    else:
        st.success(
            f"La última vez que tu número salió ganador fue en el "
            f"sorteo {est['ultimo_sorteo']} el día {est['fecha']}"
        )
        st.write(f"• Apariciones totales: **{est['apariciones']}**")
        st.write(f"• Promedio entre apariciones: **{est['promedio']} sorteos**")
        st.write(f"• Sorteos sin salir actualmente: **{est['sin_salir']}**")

    # =================================================
    # RECOMENDACIONES RELACIONADAS
    # =================================================
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
                f"• {nombre} **{val}** → "
                f"{e['sin_salir']} sorteos sin salir | "
                f"Última vez: {e['fecha']}"
            )
        else:
            st.write(f"• {nombre} **{val}** → Sin historial")

    # =================================================
    # TOPS
    # =================================================
    st.header("🔥❄️ Tops por modalidad")
    top_modalidad("PAR_FINAL", "Par Final")
    top_modalidad("D3", "Directa 3")
    top_modalidad("D4", "Directa 4")
    top_modalidad("D5", "Directa 5")

    # =================================================
    # RECOMENDACIÓN LUCKY
    # =================================================
    st.header("🍀 Recomendación Lucky")

    mult = MULTIPLICADOR if usar_multiplicador else 1

    st.markdown(f"""
### 🟢 Opción Conservadora
- **Par Final {numero[-2:]}**
- Ganancia máxima: **${PREMIOS['PAR'] * apuesta * mult:,}**

### 🟡 Opción Intermedia
- **Directa 3 {numero[-3:]}**
- Ganancia máxima: **${PREMIOS['D3'] * apuesta * mult:,}**

### 🔴 Opción Agresiva
- **Directa 5 {numero}**
- Ganancia máxima: **${PREMIOS['D5'] * apuesta * mult:,}**
""")

    st.caption("Pronósticos Lucky 🍀 — análisis estadístico, no garantía de premio.")

else:
    st.info("Ingresa un número válido para comenzar el análisis.")
