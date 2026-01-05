import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(page_title="Pronósticos Lucky", layout="centered")

# ---------------- LOGO ----------------
st.image("logolucky.jpg", width=200)
st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    df.columns = [c.strip().upper() for c in df.columns]

    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    # Construimos número ganador de 5 dígitos
    df["NUMERO"] = (
        df["R1"].astype(str)
        + df["R2"].astype(str)
        + df["R3"].astype(str)
        + df["R4"].astype(str)
        + df["R5"].astype(str)
    )

    return df.dropna(subset=["NUMERO"])

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- FUNCIONES AUXILIARES ----------------
def ultima_aparicion(df, columna, valor):
    apariciones = df[df[columna] == valor]
    if apariciones.empty:
        return "Nunca ha salido"
    fila = apariciones.iloc[-1]
    return f"Sorteo #{fila['SORTEO']} – {fila['FECHA'].strftime('%d/%m/%Y')}"

def frecuencia(df, columna, valor):
    return df[df[columna] == valor].shape[0]

def estado_caliente(freq, promedio):
    if freq > promedio * 1.2:
        return "🔥 Número caliente — Sale más que el promedio histórico."
    elif freq < promedio * 0.8:
        return "❄️ Número frío — Sale menos que el promedio histórico."
    else:
        return "⚪ Comportamiento promedio — Frecuencia similar al resto."

def top_numeros(df, columna, top=5, asc=False):
    return (
        df[columna]
        .value_counts()
        .sort_values(ascending=asc)
        .head(top)
        .index.tolist()
    )

def escalera(num):
    return "".join(sorted(num)) in ["012","123","234","345","456","567","678","789"]

def piramide(num):
    return len(set(num)) == 1

# ---------------- INPUT USUARIO ----------------
numero_usuario = st.text_input("Ingresa el número", max_chars=5).strip()

modalidad = st.selectbox(
    "Selecciona la modalidad",
    [
        "Par final",
        "Número final",
        "Par inicial",
        "Número inicial",
        "Directa 3",
        "Directa 4",
        "Directa 5",
    ],
)

# ---------------- MAPEO DE MODALIDADES ----------------
df["PAR_FINAL"] = df["NUMERO"].str[-2:]
df["PAR_INICIAL"] = df["NUMERO"].str[:2]
df["NUM_FINAL"] = df["NUMERO"].str[-1]
df["NUM_INICIAL"] = df["NUMERO"].str[:1]
df["D3F"] = df["NUMERO"].str[-3:]
df["D3I"] = df["NUMERO"].str[:3]
df["D4F"] = df["NUMERO"].str[-4:]
df["D4I"] = df["NUMERO"].str[:4]

mapa = {
    "Par final": "PAR_FINAL",
    "Número final": "NUM_FINAL",
    "Par inicial": "PAR_INICIAL",
    "Número inicial": "NUM_INICIAL",
    "Directa 3": ["D3F", "D3I"],
    "Directa 4": ["D4F", "D4I"],
    "Directa 5": "NUMERO",
}

# ---------------- ANÁLISIS ----------------
if numero_usuario:
    st.divider()
    st.subheader("📊 Análisis estadístico")

    if modalidad in ["Directa 3", "Directa 4"]:
        resultados = []
        for col in mapa[modalidad]:
            freq = frecuencia(df, col, numero_usuario)
            promedio = df[col].value_counts().mean()
            resultados.append((col, freq, promedio))

        total_freq = sum(r[1] for r in resultados)
        promedio = sum(r[2] for r in resultados) / len(resultados)

        st.write(f"Apariciones históricas: {total_freq}")
        st.write(estado_caliente(total_freq, promedio))

    else:
        col = mapa[modalidad]
        freq = frecuencia(df, col, numero_usuario)
        promedio = df[col].value_counts().mean()

        st.write(f"Apariciones históricas: {freq}")
        st.write(f"Última aparición: {ultima_aparicion(df, col, numero_usuario)}")
        st.write(estado_caliente(freq, promedio))

    # ---------------- ESCALERA Y PIRÁMIDE (RECOMENDACIÓN) ----------------
    st.divider()
    st.subheader("🔮 Recomendaciones históricas")

    ult_mes = df.tail(300)

    esc = [n for n in ult_mes["NUMERO"] if escalera(n)]
    pir = [n for n in ult_mes["NUMERO"] if piramide(n)]

    st.write("🔢 Escaleras recientes:")
    if esc:
        for n in esc[:5]:
            st.write(f"- {n} ({ultima_aparicion(df, 'NUMERO', n)})")
    else:
        st.write("No se detectaron escaleras recientes.")

    st.write("🔺 Pirámides recientes:")
    if pir:
        for n in pir[:5]:
            st.write(f"- {n} ({ultima_aparicion(df, 'NUMERO', n)})")
    else:
        st.write("No se detectaron pirámides recientes.")

    # ---------------- TOP 5 POR MODALIDAD ----------------
    st.divider()
    st.subheader("🔥❄️ Top 5 números por modalidad")

    for nombre, columna in {
        "Directa 5": "NUMERO",
        "Directa 4 final": "D4F",
        "Directa 3 final": "D3F",
        "Par final": "PAR_FINAL",
        "Par inicial": "PAR_INICIAL",
        "Número final": "NUM_FINAL",
        "Número inicial": "NUM_INICIAL",
    }.items():

        calientes = top_numeros(df, columna, 5)
        frios = top_numeros(df, columna, 5, asc=True)

        st.write(f"**{nombre}**")
        st.write("🔥 Calientes:", ", ".join(calientes))
        st.write("❄️ Fríos:", ", ".join(frios))
        st.write("")

    st.divider()
    st.caption("Análisis basado en comportamiento histórico del TRIS.")
    st.success("Pronósticos Lucky 🍀")
