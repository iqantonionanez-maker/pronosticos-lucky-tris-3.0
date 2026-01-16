import streamlit as st
import pandas as pd
from itertools import permutations

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky – TRIS",
    layout="wide"
)

st.title("🎲 Pronósticos Lucky – TRIS")
st.write("Análisis estadístico y estimación de ganancia en el TRIS.")

st.markdown("""
**Disclaimer:**  
_Este análisis es únicamente estadístico e informativo.  
No garantiza premios ni resultados._
""")

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("Tris.csv")
    df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y", errors="coerce")
    return df.sort_values("CONCURSO")

df = load_data()
total_sorteos = df["CONCURSO"].nunique()

# ---------------- DATOS OFICIALES ----------------
premios_oficiales = {
    "Directa 5": 50000,
    "Directa 4": 5000,
    "Directa 3": 500,
    "Par inicial": 50,
    "Par final": 50,
    "Número inicial": 5,
    "Número final": 5
}

multiplicadores_oficiales = {
    "Directa 5": 200000,
    "Directa 4": 20000,
    "Directa 3": 2000,
    "Par inicial": 200,
    "Par final": 200,
    "Número inicial": 20,
    "Número final": 20
}

# ---------------- SELECCIÓN DE MODALIDAD ----------------
st.subheader("🎯 Modalidad y Apuesta")

modalidad = st.selectbox(
    "Selecciona la modalidad:",
    list(premios_oficiales.keys())
)

numero = st.text_input("Número a analizar:")
apuesta_base = st.number_input("Monto de apuesta (pesos):", min_value=1, step=1)

multiplicador_on = st.checkbox("Jugar con multiplicador?")
apuesta_multiplicador = 0

if multiplicador_on:
    apuesta_multiplicador = st.number_input("Monto para multiplicador (pesos):", min_value=1, step=1)

# ---------------- EXTRACCIÓN DE JUGADA ----------------
def extraer_valor(row):
    try:
        r1,r2,r3,r4,r5 = row.R1, row.R2, row.R3, row.R4, row.R5
        if modalidad == "Directa 5":
            return f"{int(r1)}{int(r2)}{int(r3)}{int(r4)}{int(r5)}"
        if modalidad == "Directa 4":
            return f"{int(r2)}{int(r3)}{int(r4)}{int(r5)}"
        if modalidad == "Directa 3":
            return f"{int(r3)}{int(r4)}{int(r5)}"
        if modalidad == "Par inicial":
            return f"{int(r1)}{int(r2)}"
        if modalidad == "Par final":
            return f"{int(r4)}{int(r5)}"
        if modalidad == "Número inicial":
            return f"{int(r1)}"
        if modalidad == "Número final":
            return f"{int(r5)}"
    except:
        return None

df["JUGADA"] = df.apply(extraer_valor, axis=1)
df_modalidad = df.dropna(subset=["JUGADA"])

# ---------------- ANÁLISIS ESTADÍSTICO ----------------
st.subheader("📊 Análisis estadístico")

if numero:
    data = df_modalidad[df_modalidad["JUGADA"] == numero]
    apariciones = len(data)

    if apariciones > 0:
        primera_fecha = data["FECHA"].min().date()
        ultima_fecha = data["FECHA"].max().date()
        ultimo_concurso = data["CONCURSO"].max()
        sorteos_sin_salir = df_modalidad["CONCURSO"].max() - ultimo_concurso
        promedio = total_sorteos / apariciones

        if sorteos_sin_salir >= promedio * 1.2:
            estado = "🔥 Caliente"
        elif sorteos_sin_salir <= promedio * 0.8:
            estado = "❄️ Frío"
        else:
            estado = "⚪ Promedio"
    else:
        primera_fecha = "Nunca"
        ultima_fecha = "Nunca"
        sorteos_sin_salir = "N/A"
        promedio = "N/A"
        estado = "Sin datos"

    st.write(f"**Apariciones:** {apariciones}")
    st.write(f"**Desde:** {primera_fecha}")
    st.write(f"**Última vez:** {ultima_fecha}")
    st.write(f"**Sorteos sin salir:** {sorteos_sin_salir}")
    st.write(f"**Promedio histórico:** {round(promedio, 2) if isinstance(promedio, float) else promedio}")
    st.write(f"**Clasificación:** {estado}")

# ---------------- CÁLCULO DE GANANCIA ----------------
st.subheader("💰 Estimación de Ganancia")

if numero and apuesta_base:
    premio_base_unitario = premios_oficiales[modalidad]
    premio_base_total = premio_base_unitario * apuesta_base

    st.write(f"**Estimación sin multiplicador:**")
    st.write(f"- Premio por unidad (según modalidad {modalidad}): ${premio_base_unitario:,} por peso")
    st.write(f"- Con una apuesta de {apuesta_base} pesos → **${premio_base_total:,} MXN**")

    if multiplicador_on:
        mult_max = multiplicadores_oficiales[modalidad]
        premio_mult_unitario = premio_base_unitario * mult_max
        premio_mult_total = premio_base_unitario * apuesta_multiplicador * mult_max
        cantidad_maxima = premio_base_total + premio_mult_total

        st.write("**Estimación con multiplicador:**")
        st.write(f"- Multiplicador máximo oficial para {modalidad}: ×{mult_max}")
        st.write(f"- Apuesta al multiplicador: {apuesta_multiplicador} pesos")
        st.write(f"- Premio de multiplicador posible (máximo): **${premio_mult_total:,} MXN**")
        st.write(f"💰 **Cantidad máxima potencial (suma): ${cantidad_maxima:,} MXN**")

# ---------------- TABLA OFICIAL DE PREMIOS Y MULTIPLICADORES ----------------
st.subheader("📋 Tabla oficial (Referencial)")

tabla_oficial = pd.DataFrame([
    {
        "Modalidad": m,
        "Premio por $1 (MXN)": premios_oficiales[m],
        "Multiplicador máximo": multiplicadores_oficiales[m]
    }
    for m in premios_oficiales
])

st.table(tabla_oficial)

# ---------------- NÚMEROS SIMILARES ----------------
st.subheader("🔄 Números similares")

def generar_similares_inteligentes(num):
    similares = []
    largo = len(num)
    digitos = list(num)

    perms = set("".join(p) for p in permutations(digitos, largo))
    perms.discard(num)

    for p in perms:
        if len(similares) < 5:
            similares.append(p)

    n = int(num)
    if len(similares) < 5:
        similares.append(str(n - 1).zfill(largo))
    if len(similares) < 5:
        similares.append(str(n + 1).zfill(largo))
    if len(similares) < 5:
        similares.append("0" + num)
    if len(similares) < 5:
        similares.append(num + "0")

    return list(dict.fromkeys(similares))[:5]

if numero and numero.isdigit():
    similares = generar_similares_inteligentes(numero)
    tabla = []

    for s in similares:
        d = df_modalidad[df_modalidad["JUGADA"] == s]
        if len(d) > 0:
            tabla.append({
                "Número": s,
                "Apariciones": len(d),
                "Última fecha": d["FECHA"].max().date(),
                "Sorteos sin salir": df_modalidad["CONCURSO"].max() - d["CONCURSO"].max(),
                "Promedio": round(total_sorteos / len(d), 2)
            })
        else:
            tabla.append({
                "Número": s,
                "Apariciones": 0,
                "Última fecha": "Nunca",
                "Sorteos sin salir": "N/A",
                "Promedio": "N/A"
            })

    st.dataframe(pd.DataFrame(tabla))

# ---------------- RECOMENDACIONES LUCKY ----------------
st.subheader("🍀 Recomendaciones Lucky")

ranking = []

for j, g in df_modalidad.groupby("JUGADA"):
    apar = len(g)
    ult = g["CONCURSO"].max()
    sin = df_modalidad["CONCURSO"].max() - ult
    prom = total_sorteos / apar
    score = sin / prom
    ranking.append((j, score, sin, prom))

ranking = sorted(ranking, key=lambda x: x[1], reverse=True)[:3]

for r in ranking:
    st.write(
        f"🔹 **{r[0]}** — Históricamente aparece cada {int(r[3])} sorteos "
        f"y actualmente lleva {r[2]} sin salir."
    )
