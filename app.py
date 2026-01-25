import streamlit as st
import pandas as pd
from itertools import permutations
from datetime import date

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

CSV_LOCAL = "Tris.csv"

# ----------- ESTILOS VISUALES (TEXTO NEGRO FORZADO) -----------
st.markdown("""
<style>

/* Fondo general */
.stApp {
    background-color: #1F9E35;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #168a2c;
}

/* FORZAR TODO TEXTO A NEGRO */
* {
    color: #000000 !important;
}

/* Inputs */
input, textarea {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border-radius: 12px;
}

/* Selectbox */
div[data-baseweb="select"] {
    background-color: #FFFFFF;
    border-radius: 12px;
}

/* Botones */
.stButton > button {
    background-color: #f4c430;
    color: #000000 !important;
    font-weight: bold;
    border-radius: 14px;
    padding: 10px 26px;
}

.stButton > button:hover {
    background-color: #d4a017;
}

/* Tarjetas */
.card {
    background-color: #FFFFFF;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.25);
}

</style>
""", unsafe_allow_html=True)



# ---------------- FUNCIONES AUXILIARES ----------------
def cargar_local():
    df = pd.read_csv(CSV_LOCAL)
    df["CONCURSO"] = df["CONCURSO"].astype(int)
    return df

def guardar(df):
    df = df.sort_values("CONCURSO", ascending=False)
    df.to_csv(CSV_LOCAL, index=False)

def normalizar_csv_externo(df):
    df.columns = [c.strip() for c in df.columns]

    df = df.rename(columns={
        "Sorteo": "CONCURSO",
        "Fecha": "FECHA"
    })

    if "Combinación Ganadora" in df.columns:
        df["Combinación Ganadora"] = df["Combinación Ganadora"].astype(str).str.zfill(5)
        df["R1"] = df["Combinación Ganadora"].str[0].astype(int)
        df["R2"] = df["Combinación Ganadora"].str[1].astype(int)
        df["R3"] = df["Combinación Ganadora"].str[2].astype(int)
        df["R4"] = df["Combinación Ganadora"].str[3].astype(int)
        df["R5"] = df["Combinación Ganadora"].str[4].astype(int)

    df["NPRODUCTO"] = 60
    if "Multiplicador" in df.columns:
        df["Multiplicador"] = df["Multiplicador"].str.upper().replace({"SÍ": "SI"})
    else:
        df["Multiplicador"] = "NO"

    return df[[
        "NPRODUCTO",
        "CONCURSO",
        "R1", "R2", "R3", "R4", "R5",
        "FECHA",
        "Multiplicador"
    ]]

# ---------------- ACTUALIZACIÓN DEL HISTÓRICO ----------------
with st.expander("🔄 Actualización del histórico", expanded=False):

    df_local = cargar_local()
    ultimo_concurso = df_local["CONCURSO"].max()
    st.info(f"📄 Último concurso registrado: {ultimo_concurso}")

    # ---- SUBIR CSV ----
    st.markdown("### 📤 Actualizar desde archivo oficial")
    archivo = st.file_uploader("Sube el CSV oficial del TRIS", type=["csv"])

    if archivo is not None:
        try:
            df_nuevo = pd.read_csv(archivo)
            df_nuevo = normalizar_csv_externo(df_nuevo)
            nuevos = df_nuevo[df_nuevo["CONCURSO"] > ultimo_concurso]

            if nuevos.empty:
                st.warning("No hay sorteos nuevos en el archivo.")
            else:
                df_final = pd.concat([df_local, nuevos], ignore_index=True)
                guardar(df_final)
                st.success(f"✅ Se agregaron {len(nuevos)} sorteos nuevos.")
                st.experimental_rerun()

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

    # ---- CAPTURA MANUAL ----
    st.markdown("### ✍️ Captura manual de sorteo")

    with st.form("captura_manual"):
        concurso_manual = ultimo_concurso + 1
        numero = st.text_input("Número ganador (5 dígitos)")
        multiplicador = st.selectbox("¿Salió multiplicador?", ["NO", "SI"])
        fecha = st.date_input("Fecha del sorteo", value=date.today())
        enviar = st.form_submit_button("Guardar sorteo")

        if enviar:
            if not numero.isdigit() or len(numero) != 5:
                st.error("El número debe tener exactamente 5 dígitos.")
            else:
                nuevo = {
                    "NPRODUCTO": 60,
                    "CONCURSO": concurso_manual,
                    "R1": int(numero[0]),
                    "R2": int(numero[1]),
                    "R3": int(numero[2]),
                    "R4": int(numero[3]),
                    "R5": int(numero[4]),
                    "FECHA": fecha.strftime("%d/%m/%Y"),
                    "Multiplicador": multiplicador
                }

                df_final = pd.concat([df_local, pd.DataFrame([nuevo])], ignore_index=True)
                guardar(df_final)
                st.success(f"✅ Sorteo {concurso_manual} agregado.")
                st.experimental_rerun()

# ---------------- CARGA DE DATOS ORIGINAL ----------------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_LOCAL)
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

seleccion = st.text_input("Ingresa el número a analizar:")

if seleccion and seleccion.isdigit():
    data = df_modalidad[df_modalidad["JUGADA"] == seleccion]

    apariciones_total = len(data)

    if apariciones_total > 0:
        ultimo_concurso = df_modalidad["CONCURSO"].max()

# Rangos de sorteos
ultimo_concurso = df_modalidad["CONCURSO"].max()

ult_100 = df_modalidad[df_modalidad["CONCURSO"] > ultimo_concurso - 100]
ult_1000 = df_modalidad[df_modalidad["CONCURSO"] > ultimo_concurso - 1000]
ult_10000 = df_modalidad[df_modalidad["CONCURSO"] > ultimo_concurso - 10000]

apar_100 = len(ult_100[ult_100["JUGADA"] == seleccion])
apar_1000 = len(ult_1000[ult_1000["JUGADA"] == seleccion])
apar_10000 = len(ult_10000[ult_10000["JUGADA"] == seleccion])

# Promedio redondeado
promedio = round(total_sorteos / apariciones_total)

# ---- FECHAS EN ESPAÑOL ----
meses_es = {
    1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR",
    5: "MAY", 6: "JUN", 7: "JUL", 8: "AGO",
    9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
}

ultimas_fechas = []
for f in (
    data.sort_values("FECHA", ascending=False)
    .head(5)["FECHA"]
):
    ultimas_fechas.append(
        f"{f.day:02d}-{meses_es[f.month]}-{str(f.year)[-2:]}"
    )

# ---- SALIDA EN PANTALLA ----
st.write("**Apariciones del número:**")
st.write(f"• Histórico total: **{apariciones_total} veces**")
st.write(f"• Últimos 10,000 sorteos: **{apar_10000} veces**")
st.write(f"• Últimos 1,000 sorteos: **{apar_1000} veces**")
st.write(f"• Últimos 100 sorteos: **{apar_100} veces**")

st.write(f"**Promedio histórico:** {promedio} sorteos")

st.write("**Últimas 5 fechas en que salió:**")
for f in ultimas_fechas:
    st.write(f"• {f}")


    else:
        st.warning("Este número no tiene apariciones en el histórico.")


# ---------------- CÁLCULO DE PREMIOS ----------------
st.subheader("💰 Cálculo de premio máximo posible")

apuesta = st.number_input("Monto de la apuesta ($)", min_value=1, step=1)
multiplicador = st.number_input("Monto del multiplicador ($)", min_value=0, step=1)

tabla_pagos = {
    "Directa 5": {"base": 50000, "multi": 200000},
    "Directa 4": {"base": 5000, "multi": 20000},
    "Directa 3": {"base": 500, "multi": 2000},
    "Par inicial": {"base": 50, "multi": 200},
    "Par final": {"base": 50, "multi": 200},
    "Número inicial": {"base": 5, "multi": 20},
    "Número final": {"base": 5, "multi": 20}
}

if seleccion and seleccion.isdigit():
    pago_base = tabla_pagos[modalidad]["base"] * apuesta
    pago_multi = tabla_pagos[modalidad]["multi"] * multiplicador
    total = pago_base + pago_multi

    st.success("🎯 **Desglose de premios**")
    st.write(f"**Modalidad:** {modalidad}")
    st.write(f"**Número jugado:** {seleccion}")
    st.write(f"**Premio base:** ${pago_base:,}")
    st.write(f"**Premio por multiplicador:** ${pago_multi:,}")
    st.write(f"### 🏆 **Premio total máximo posible:** ${total:,}")

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
