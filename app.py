import streamlit as st
import pandas as pd
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🎲 Pronósticos Lucky", layout="centered")

# ---------------- LOGO ----------------
if os.path.exists("logolucky.jpg"):
    st.image("logolucky.jpg", width=200)

st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS")

# ---------------- DATA ----------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    posibles = ["R5", "numero", "Número", "RESULTADO"]
    col = None
    for c in posibles:
        if c in df.columns:
            col = c
            break

    if col is None:
        st.error("No se encontró la columna de resultados")
        st.stop()

    df["numero"] = df[col].astype(str).str.replace(".0", "", regex=False).str.zfill(5)
    return df

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------------- INPUT ----------------
st.markdown("### 🔍 Analizar número")
numero_usuario = st.text_input("Ingresa el número", "").strip()

if not numero_usuario.isdigit():
    st.stop()

# ---------------- MODALIDADES ----------------
modalidades = {
    "Número inicial": ("inicio", 1),
    "Par inicial": ("inicio", 2),
    "Número final": ("final", 1),
    "Par final": ("final", 2),
    "Directa 3": ("final", 3),
    "Directa 4": ("final", 4),
    "Directa 5": ("final", 5),
}

st.markdown("### Selecciona la modalidad")
modalidad = st.radio("", list(modalidades.keys()), index=3)

tipo, digitos_req = modalidades[modalidad]

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

# ---------------- FILTRO CENTRAL ----------------
def filtrar(df, num, tipo, dig):
    if tipo == "inicio":
        return df[df["numero"].str[:dig] == num]
    else:
        return df[df["numero"].str[-dig:] == num]

df_match = filtrar(df, numero_usuario, tipo, digitos_req)

# ---------------- ANALISIS ----------------
st.markdown("### 📊 Análisis estadístico")

apariciones = len(df_match)
st.write(f"**Apariciones históricas:** {apariciones}")

if apariciones > 0:
    ultima_pos = df_match.index.max()
    st.write(f"**Última aparición:** Sorteo #{ultima_pos}")
else:
    st.write("**Última aparición:** Nunca ha salido")

# ---------------- CALIENTE / FRIO ----------------
st.markdown("### 🔥❄️ Número caliente / frío")

conteo = (
    df["numero"]
    .apply(lambda x: x[:digitos_req] if tipo == "inicio" else x[-digitos_req:])
    .value_counts()
)

promedio = conteo.mean()

if numero_usuario in conteo:
    if conteo[numero_usuario] > promedio:
        st.success("🔥 Número caliente")
    elif conteo[numero_usuario] < promedio:
        st.error("❄️ Número frío")
    else:
        st.info("⚪ Comportamiento promedio")
else:
    st.warning("Número sin historial")

# ---------------- PERIODOS ----------------
st.markdown("### ⏳ Análisis por periodos")

for p in [50, 100, 500]:
    sub = df.tail(p)
    ap = len(filtrar(sub, numero_usuario, tipo, digitos_req))
    st.write(f"Últimos {p}: {ap} apariciones")

# ---------------- ESCALERA ----------------
st.markdown("### 🔢 Escalera")

def es_escalera(num):
    return len(num) >= 3 and all(int(num[i]) + 1 == int(num[i+1]) for i in range(len(num)-1))

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
similares = []

for i in range(1, 3):
    similares.append(str(num_int - i).zfill(digitos_req))
    similares.append(str(num_int + i).zfill(digitos_req))

st.write("Números cercanos:", ", ".join(similares))

# ---------------- GANANCIA ----------------
st.markdown("### 💵 Ganancia máxima posible")

tabla_pagos = {
    "Número inicial": 7,
    "Número final": 7,
    "Par inicial": 50,
    "Par final": 50,
    "Directa 3": 500,
    "Directa 4": 5000,
    "Directa 5": 50000
}

ganancia = apuesta * multi * tabla_pagos[modalidad]
st.success(f"Ganancia máxima posible: ${ganancia:,.2f}")

# ---------------- FOOTER ----------------
st.caption("Análisis basado en comportamiento histórico del TRIS.")
st.caption("Pronósticos Lucky 🍀")
