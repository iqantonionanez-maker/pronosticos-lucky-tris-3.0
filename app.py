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

# ---------------- SELECCIÓN DE MODALIDAD ----------------
st.subheader("🎯 Modalidad a analizar")

modalidad = st.selectbox(
    "Selecciona la modalidad:",
    [
        "Directa 5",
        "Directa 4",
        "Directa 3",
        "Par inicial",
        "Par final",
        "Número inicial",
        "Número final"
    ]
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

# ---------------- ANÁLISIS PRINCIPAL ----------------
st.subheader("📊 Análisis estadístico")

col1, col2, col3 = st.columns(3)

with col1:
    seleccion = st.text_input("Ingresa el número a analizar:")

with col2:
    apuesta_tris = st.number_input("Apuesta TRIS ($)", min_value=1, step=1)

with col3:
    apuesta_multi = st.number_input("Apuesta Multiplicador ($)", min_value=0, step=1)

if seleccion and seleccion.isdigit():
    data = df_modalidad[df_modalidad["JUGADA"] == seleccion]
    apariciones = len(data)

    if apariciones > 0:
        ultima_fecha = data["FECHA"].max()
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
        ultima_fecha = None
        sorteos_sin_salir = None
        promedio = None
        estado = "Sin datos"

    st.write(f"**Apariciones:** {apariciones}")
    st.write(f"**Última vez:** {ultima_fecha.date() if ultima_fecha is not None else 'Nunca'}")
    st.write(f"**Sorteos sin salir:** {sorteos_sin_salir if sorteos_sin_salir is not None else 'N/A'}")
    st.write(f"**Promedio histórico:** {round(promedio, 2) if promedio else 'N/A'}")
    st.write(f"**Clasificación:** {estado}")

    # -------- CÁLCULO DEL PREMIO --------
    st.markdown("### 💰 Cálculo del premio máximo")

    premio_tris = apuesta_tris * 70
    premio_multi = apuesta_multi * 70 * 5  # factor máximo informativo
    premio_total = premio_tris + premio_multi

    st.write(f"Premio TRIS: **${premio_tris:,.2f}**")
    st.write(f"Premio Multiplicador (máx): **${premio_multi:,.2f}**")
    st.success(f"🏆 **Premio máximo estimado: ${premio_total:,.2f}**")

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
