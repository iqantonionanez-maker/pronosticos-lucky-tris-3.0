import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Pronósticos Lucky - TRIS",
    layout="wide"
)

st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS")

st.markdown("---")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Convertir fecha
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True)

    # Crear número completo como texto
    df["NUMERO"] = (
        df["R1"].astype(str) +
        df["R2"].astype(str) +
        df["R3"].astype(str) +
        df["R4"].astype(str) +
        df["R5"].astype(str)
    )

    return df

df = cargar_datos()

st.success(f"Sorteos cargados: {len(df)}")

st.markdown("---")

st.header("🔍 Analizar número")

numero_input = st.text_input(
    "Ingresa el número que deseas analizar",
    placeholder="Ejemplo: 569, 4583, 59862"
)

if numero_input:
    longitud = len(numero_input)

    if longitud == 5:
        forma = "Directa 5"
        coincidencia = numero_input
    elif longitud == 4:
        forma = "Directa 4 (últimos 4 del número ganador)"
        coincidencia = numero_input
    elif longitud == 3:
        forma = "Directa 3 (últimos 3 del número ganador)"
        coincidencia = numero_input
    else:
        forma = "Forma manual"
        coincidencia = numero_input

    st.info(f"Forma de juego detectada: **{forma}**")

    if longitud <= 2:
        forma_manual = st.selectbox(
            "¿Cómo deseas analizar este número?",
            ["Par inicial", "Par final", "Número inicial", "Número final"]
        )
        st.info(f"Forma seleccionada: **{forma_manual}**")

    st.markdown("---")

    st.header("💰 Datos de la jugada")

    cantidad = st.number_input(
        "Cantidad a jugar (pesos)",
        min_value=1,
        value=1
    )

    multiplicador = st.selectbox(
        "¿Jugar con multiplicador?",
        ["No", "Sí"]
    )

    if multiplicador == "Sí":
        multi_valor = st.selectbox(
            "Selecciona multiplicador",
            [2, 3, 5, 10]
        )
    else:
        multi_valor = 1

    st.markdown("---")

    # Conteo de apariciones
    total_apariciones = df["NUMERO"].str.endswith(coincidencia).sum()
    ultima_fecha = df[df["NUMERO"].str.endswith(coincidencia)]["FECHA"].max()

    st.header("📊 Análisis básico")

    st.write(f"**Apariciones históricas:** {total_apariciones}")

    if pd.isna(ultima_fecha):
        st.write("**Última aparición:** Nunca ha salido")
    else:
        st.write(f"**Última aparición:** {ultima_fecha.strftime('%d/%m/%Y')}")

    st.markdown("---")

    st.header("🚦 Indicador histórico")

    if total_apariciones > 100:
        st.success("🟢 Frecuencia alta — Aparece más veces que el promedio histórico.")
    elif total_apariciones >= 30:
        st.warning("🟡 Frecuencia media — Comportamiento dentro de lo normal.")
    else:
        st.error("🔴 Frecuencia baja — Ha aparecido menos veces que el promedio.")

    st.markdown("---")

    st.header("💵 Ganancia máxima posible")

    premios = {
        "Directa 5": 50000,
        "Directa 4 (últimos 4 del número ganador)": 5000,
        "Directa 3 (últimos 3 del número ganador)": 500,
    }

    premio_base = premios.get(forma, 0)
    ganancia_max = premio_base * cantidad * multi_valor

    st.info(f"Ganancia máxima posible según reglas oficiales: **${ganancia_max:,.2f}**")

    st.markdown("---")

    st.markdown(
        """
        *Este análisis se basa en comportamiento estadístico histórico.*  
        **Pronósticos Lucky te desea buena suerte 🍀**
        """
    )
