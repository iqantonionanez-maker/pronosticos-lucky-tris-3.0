import streamlit as st
import pandas as pd
import os

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(page_title="🎲 Pronósticos Lucky", layout="centered")

# ---------------- LOGO ----------------
if os.path.exists("logolucky.jpg"):
    st.image("logolucky.jpg", width=200)

st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    # Detectar columna correcta
    posibles = ["R5", "numero", "Número", "RESULTADO"]
    col = None
    for c in posibles:
        if c in df.columns:
            col = c
            break

    if col is None:
        st.error("No se encontró la columna de resultados en el CSV")
        st.stop()

    df["numero"] = df[col].astype(str).str.replace(".0", "", regex=False).str.zfill(5)
    return df

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- INPUT USUARIO ----------------
st.markdown("### 🔍 Analizar número")
numero_usuario = st.text_input("Ingresa el número que deseas analizar", "")

if not numero_usuario.isdigit():
    st.stop()

# ---------------- MODALIDADES ----------------
modalidades = {
    "Par final": 2,
    "Número final": 1,
    "Directa 3": 3,
    "Directa 4": 4,
    "Directa 5": 5
}

st.markdown("### Selecciona la modalidad")
modalidad = st.radio(
    "",
    list(modalidades.keys()),
    index=0
)

digitos_req = modalidades[modalidad]

if len(numero_usuario) != digitos_req:
    st.warning(f"Esta modalidad requiere exactamente {digitos_req} dígitos.")
    st.stop()

# ---------------- APUESTA ----------------
st.markdown("### 💰 Datos de la jugada")
apuesta = st.number_input("Cantidad a jugar (pesos)", min_value=1, max_value=100, value=1)

multiplicador = st.radio("¿Jugar con multiplicador?", ["No", "Sí"])

multi = 1
if multiplicador == "Sí":
    multi = st.number_input(
        "Selecciona multiplicador",
        min_value=1,
        max_value=apuesta,
        value=1
    )

if apuesta * multi > 100:
    st.error("La apuesta total no puede exceder $100")
    st.stop()

# ---------------- FILTRO ----------------
def filtrar(df, num, modalidad):
    if modalidad == "Par final":
        return df[df["numero"].str[-2:] == num]
    if modalidad == "Número final":
        return df[df["numero"].str[-1:] == num]
    if modalidad == "Directa 3":
        return df[df["numero"].str[-3:] == num]
    if modalidad == "Directa 4":
        return df[df["numero"].str[-4:] == num]
    return df[df["numero"] == num]

df_match = filtrar(df, numero_usuario, modalidad)

# ---------------- RESULTADOS ----------------
st.markdown("### 📊 Análisis básico")
apariciones = len(df_match)

st.write(f"**Apariciones históricas:** {apariciones}")

if apariciones > 0:
    ultima = df_match.index.max()
    st.write(f"**Última aparición:** Sorteo #{ultima}")
else:
    st.write("**Última aparición:** Nunca ha salido")

# ---------------- CALIENTE / FRÍO ----------------
conteo = df["numero"].value_counts()
promedio = conteo.mean()

st.markdown("### 🔥❄️ Indicador histórico")

if apariciones > promedio:
    st.success("🔥 Número caliente")
elif apariciones < promedio:
    st.error("❄️ Número frío")
else:
    st.info("⚪ Comportamiento promedio")

# ---------------- PERIODOS ----------------
st.markdown("### ⏳ Análisis por periodos")

for p in [50, 100, 500]:
    sub = df.tail(p)
    ap = len(filtrar(sub, numero_usuario, modalidad))
    st.write(f"Últimos {p}: {ap} apariciones")

# ---------------- ESCALERA ----------------
st.markdown("### 🔢 Escalera")

def es_escalera(num):
    return all(int(num[i])+1 == int(num[i+1]) for i in range(len(num)-1))

if len(numero_usuario) >= 3:
    if es_escalera(numero_usuario):
        st.success("✔ Es una escalera")
    else:
        st.info("No es escalera")

# ---------------- PIRÁMIDE ----------------
st.markdown("### 🔺 Pirámide")

def es_piramide(num):
    return len(set(num)) == 1

if es_piramide(numero_usuario):
    st.success("✔ Es pirámide")
else:
    st.info("No es pirámide")

# ---------------- COMPARACIONES ----------------
st.markdown("### 🔄 Comparaciones avanzadas")

num_int = int(numero_usuario)
comparaciones = []

for i in range(1, 3):
    comparaciones.append(str(num_int - i).zfill(digitos_req))
    comparaciones.append(str(num_int + i).zfill(digitos_req))

st.write("Similares:", ", ".join(comparaciones))

# ---------------- GANANCIA ----------------
st.markdown("### 💵 Ganancia máxima posible")

tabla_pagos = {
    "Número final": 7,
    "Par final": 50,
    "Directa 3": 500,
    "Directa 4": 5000,
    "Directa 5": 50000
}

ganancia = apuesta * multi * tabla_pagos[modalidad]
st.success(f"Ganancia máxima posible: ${ganancia:,.2f}")

# ---------------- FOOTER ----------------
st.caption("Este análisis se basa en comportamiento estadístico histórico.")
st.caption("Pronósticos Lucky te desea buena suerte 🍀")
