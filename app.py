import streamlit as st
import pandas as pd
from itertools import permutations

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="Pronósticos Lucky – TRIS",
    layout="wide"
)

st.title("🎲 Pronósticos Lucky – TRIS")
st.write("Análisis estadístico basado únicamente en el histórico oficial del TRIS.")

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

# ---------------- PREMIOS OFICIALES ----------------
premios_tris = {
    "Directa 5": 50000,
    "Directa 4": 5000,
    "Directa 3": 500,
    "Par final": 50,
    "Par inicial": 50,
    "Número final": 5,
    "Número inicial": 5
}

premios_multiplicador = {
    "Directa 5": 200000,
    "Directa 4": 20000,
    "Directa 3": 2000,
    "Par final": 200,
    "Par inicial": 200,
    "Número final": 20,
    "Número inicial": 20
}

# ---------------- SELECCIÓN DE MODALIDAD ----------------
st.subheader("🎯 Modalidad a analizar")

modalidad = st.selectbox(
    "Selecciona la modalidad:",
    list(premios_tris.keys())
)

# ---------------- EXTRACCIÓN DE JUGADA ----------------
def extraer_valor(row):
    try:
        if modalidad == "Directa 5":
            return f"{int(row.R1)}{int(row.R2)}{int(row.R3)}{int(row.R4)}{int(row.R5)}"
        if modalidad == "Directa 4":
            return f"{int(row.R2)}{int(row.R3)}{int(row.R4)}{int(row.R5)}"
        if modalidad == "Directa 3":
            return f"{int(row.R3)}{int(row.R4)}{int(row.R5)}"
        if modalidad == "Par inicial":
            return f"{int(row.R1)}{int(row.R2)}"
        if modalidad == "Par final":
            return f"{int(row.R4)}{int(row.R5)}"
        if modalidad == "Número inicial":
            return f"{int(row.R1)}"
        if modalidad == "Número final":
            return f"{int(row.R5)}"
    except:
        return None

df["JUGADA"] = df.apply(extraer_valor, axis=1)
df_modalidad = df.dropna(subset=["JUGADA"])

# ---------------- ENTRADAS DEL USUARIO ----------------
st.subheader("📊 Análisis estadístico y cálculo de premio")

seleccion = st.text_input("Ingresa el número a analizar:")
apuesta_tris = st.number_input("Apuesta TRIS ($)", min_value=0, step=1, value=1)
apuesta_multi = st.number_input("Apuesta Multiplicador ($)", min_value=0, step=1, value=0)

if seleccion and seleccion.isdigit():
    data = df_modalidad[df_modalidad["JUGADA"] == seleccion]
    apariciones = len(data)

    if apariciones > 0:
        ultima_fecha = data["FECHA"].max()
        ultimo_concurso = data["CONCURSO"].max()
        sorteos_sin_salir = df_modalidad["CONCURSO"].max() - ultimo_concurso
    else:
        ultima_fecha = None
        sorteos_sin_salir = "N/A"

    st.write(f"**Apariciones:** {apariciones} de {total_sorteos} sorteos analizados")
    st.write(f"**Última vez:** {ultima_fecha.date() if ultima_fecha is not None else 'Nunca'}")
    st.write(f"**Sorteos sin salir:** {sorteos_sin_salir}")

    # ---------------- CÁLCULO DE PREMIO ----------------
    st.markdown("### 💰 Cálculo del premio máximo (oficial TRIS)")

    premio_tris = apuesta_tris * premios_tris[modalidad]
    premio_multi = apuesta_multi * premios_multiplicador[modalidad]
    premio_total = premio_tris + premio_multi

    st.write(f"Premio TRIS: **${premio_tris:,.2f}**")
    st.write(f"Premio Multiplicador: **${premio_multi:,.2f}**")
    st.success(f"🏆 **Premio máximo total: ${premio_total:,.2f}**")

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

if seleccion and seleccion.isdigit():
    similares = generar_similares_inteligentes(seleccion)
    tabla = []

    for s in similares:
        d = df_modalidad[df_modalidad["JUGADA"] == s]
        tabla.append({
            "Número": s,
            "Apariciones": f"{len(d)} de {total_sorteos}",
            "Última fecha": d["FECHA"].max().date() if len(d) > 0 else "Nunca",
            "Sorteos sin salir": df_modalidad["CONCURSO"].max() - d["CONCURSO"].max() if len(d) > 0 else "N/A"
        })

    st.dataframe(pd.DataFrame(tabla))

# ---------------- RECOMENDACIONES LUCKY ----------------
st.subheader("🍀 Recomendaciones Lucky")

ranking = []

for j, g in df_modalidad.groupby("JUGADA"):
    apar = len(g)
    ult = g["CONCURSO"].max()
    sin = df_modalidad["CONCURSO"].max() - ult
    ranking.append((j, sin))

ranking = sorted(ranking, key=lambda x: x[1], reverse=True)[:3]

for r in ranking:
    st.write(
        f"🔹 **{r[0]}** — Lleva **{r[1]} sorteos** sin aparecer según el histórico."
    )
