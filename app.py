import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🎲 Pronósticos Lucky", layout="centered")

# ---------- LOGO ----------
if os.path.exists("logolucky.jpg"):
    st.image("logolucky.jpg", width=200)

st.title("🎲 Pronósticos Lucky")
st.subheader("Análisis estadístico del TRIS")

# ---------- CARGA DE DATOS ----------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    columnas = ["R1", "R2", "R3", "R4", "R5"]
    for col in columnas:
        if col not in df.columns:
            st.error("El CSV no contiene las columnas R1 a R5")
            st.stop()

    # LIMPIEZA CLAVE (FIX DEFINITIVO)
    for col in columnas:
        df[col] = (
            df[col]
            .fillna(0)
            .astype(int)
            .astype(str)
        )

    df["numero"] = df["R1"] + df["R2"] + df["R3"] + df["R4"] + df["R5"]

    return df

df = cargar_datos()
st.success(f"Sorteos cargados correctamente: {len(df)}")

# ---------- INPUT ----------
st.markdown("### 🔍 Analizar número")
numero_usuario = st.text_input("Ingresa el número", "").strip()

if not numero_usuario.isdigit():
    st.stop()

# ---------- MODALIDADES ----------
modalidades = {
    "Par final": ("final", 2),
    "Número final": ("final", 1),
    "Par inicial": ("inicio", 2),
    "Número inicial": ("inicio", 1),
    "Directa 3": ("final", 3),
    "Directa 4": ("final", 4),
    "Directa 5": ("final", 5),
}

st.markdown("### Selecciona la modalidad")

modalidad = st.radio(
    "",
    list(modalidades.keys()),
    index=0  # Par final por default
)

tipo, digitos = modalidades[modalidad]

if len(numero_usuario) != digitos:
    st.warning(f"Esta modalidad requiere exactamente {digitos} dígitos.")
    st.stop()

# ---------- APUESTA ----------
st.markdown("### 💰 Datos de la jugada")
apuesta = st.number_input("Cantidad a jugar (pesos)", min_value=1, max_value=100, value=1)

usa_multi = st.radio("¿Jugar con multiplicador?", ["No", "Sí"])
multi = 1

if usa_multi == "Sí":
    multi = st.number_input(
        "Selecciona multiplicador",
        min_value=1,
        max_value=apuesta,
        value=1
    )

if apuesta * multi > 100:
    st.error("La apuesta total no puede exceder $100")
    st.stop()

# ---------- COLUMNA DE ANÁLISIS ----------
if tipo == "inicio":
    df["analisis"] = df["numero"].str[:digitos]
else:
    df["analisis"] = df["numero"].str[-digitos:]

# ---------- ANÁLISIS ----------
st.markdown("### 📊 Análisis estadístico")

conteo = df["analisis"].value_counts()
apariciones = int(conteo.get(numero_usuario, 0))

st.write(f"**Apariciones históricas:** {apariciones}")

if apariciones > 0:
    ultima = df[df["analisis"] == numero_usuario].index.max()
    st.write(f"**Última aparición:** Sorteo #{ultima}")
else:
    st.write("**Última aparición:** Nunca ha salido")

# ---------- CALIENTE / FRÍO ----------
st.markdown("### 🔥❄️ Número caliente / frío")

promedio = conteo.mean()

if apariciones > promedio:
    st.success("🔥 Número caliente")
elif apariciones > 0:
    st.info("⚪ Comportamiento promedio")
else:
    st.error("❄️ Número frío")

# ---------- PERIODOS ----------
st.markdown("### ⏳ Análisis por periodos")

for p in [50, 100, 500]:
    sub = df.tail(p)
    ap = int((sub["analisis"] == numero_usuario).sum())
    st.write(f"Últimos {p}: {ap} apariciones")

# ---------- ESCALERA ----------
st.markdown("### 🔢 Escalera")

def es_escalera(n):
    return len(n) >= 3 and all(int(n[i])+1 == int(n[i+1]) for i in range(len(n)-1))

st.success("✔ Es escalera") if es_escalera(numero_usuario) else st.info("No es escalera")

# ---------- PIRÁMIDE ----------
st.markdown("### 🔺 Pirámide")

st.success("✔ Es pirámide") if len(set(numero_usuario)) == 1 else st.info("No es pirámide")

# ---------- COMPARACIONES ----------
st.markdown("### 🔄 Comparaciones avanzadas")

n = int(numero_usuario)
similares = [str(n+i).zfill(digitos) for i in [-2, -1, 1, 2]]
st.write("Números cercanos:", ", ".join(similares))

# ---------- GANANCIA ----------
st.markdown("### 💵 Ganancia máxima posible")

pagos = {
    "Número inicial": 7,
    "Número final": 7,
    "Par inicial": 50,
    "Par final": 50,
    "Directa 3": 500,
    "Directa 4": 5000,
    "Directa 5": 50000,
}

ganancia = apuesta * multi * pagos[modalidad]
st.success(f"Ganancia máxima posible: ${ganancia:,.2f}")

# ---------- FOOTER ----------
st.caption("Análisis basado en comportamiento histórico del TRIS.")
st.caption("Pronósticos Lucky 🍀")
