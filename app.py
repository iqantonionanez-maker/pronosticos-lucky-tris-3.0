import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pronósticos Lucky", layout="centered")

# ---------- ESTILO LIMPIO ----------
st.markdown("""
<style>
body { background-color: white; color: black; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ---------- CARGA CSV ----------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Tris.csv")

    for c in ["R1","R2","R3","R4","R5"]:
        df[c] = df[c].astype(int).astype(str)

    df["NUMERO"] = df["R1"]+df["R2"]+df["R3"]+df["R4"]+df["R5"]
    df["PAR_FINAL"] = df["R4"] + df["R5"]
    df["PAR_INICIAL"] = df["R1"] + df["R2"]
    df["D3"] = df["R3"] + df["R4"] + df["R5"]
    df["D4"] = df["R2"] + df["R3"] + df["R4"] + df["R5"]
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")

    return df.sort_values("FECHA")

df = cargar_datos()

# ---------- UI ----------
st.markdown("<h1 style='text-align:center'>🎲 Pronósticos Lucky</h1>", unsafe_allow_html=True)
st.caption("Análisis estadístico del TRIS (solo informativo)")
st.success(f"Sorteos cargados correctamente: {len(df)}")

numero = st.text_input("Ingresa el número").strip()
modalidad = st.selectbox(
    "Selecciona la modalidad",
    ["Par final","Par inicial","Número final","Número inicial","Directa 3","Directa 4","Directa 5"]
)

# ---------- ANÁLISIS ----------
if numero.isdigit():

    if modalidad == "Par final":
        parte = numero[-2:]
        resultados = df[df["PAR_FINAL"] == parte]

    elif modalidad == "Par inicial":
        parte = numero[:2]
        resultados = df[df["PAR_INICIAL"] == parte]

    elif modalidad == "Número final":
        parte = numero[-1]
        resultados = df[df["R5"] == parte]

    elif modalidad == "Número inicial":
        parte = numero[:1]
        resultados = df[df["R1"] == parte]

    elif modalidad == "Directa 3":
        parte = numero[-3:]
        resultados = df[df["D3"] == parte]

    elif modalidad == "Directa 4":
        parte = numero[-4:]
        resultados = df[df["D4"] == parte]

    else:  # Directa 5
        parte = numero.zfill(5)
        resultados = df[df["NUMERO"] == parte]

    st.subheader("📊 Análisis estadístico")
    st.write(f"**Número analizado:** {parte}")
    st.write(f"**Apariciones históricas:** {len(resultados)}")

    if len(resultados) > 0:
        ultima = resultados.iloc[-1]["FECHA"]
        st.write(f"**Última vez que salió:** {ultima.strftime('%d/%m/%Y')}")
    else:
        st.write("**Última vez que salió:** Nunca ha salido")

    # ---------- CALIENTE / FRÍO ----------
    promedio = len(df) / 100
    if len(resultados) >= promedio * 1.2:
        st.success("🔥 Número caliente — aparece ≥20% más que el promedio")
    elif len(resultados) <= promedio * 0.8:
        st.info("❄️ Número frío — aparece ≥20% menos que el promedio")
    else:
        st.write("⚪ Comportamiento promedio")

    # ---------- SIMILARES ----------
    st.subheader("🔄 Números similares")
    base = int(parte)
    for i in range(-2,3):
        n = str(base+i).zfill(len(parte))
        r = df[df["PAR_FINAL"] == n] if modalidad=="Par final" else df[df["NUMERO"].str.endswith(n)]
        fecha = r.iloc[-1]["FECHA"].strftime("%d/%m/%Y") if len(r)>0 else "Nunca"
        st.write(f"• {n} → {len(r)} apariciones | Última vez: {fecha}")

# ---------- DISCLAIMER ----------
st.markdown("---")
st.caption("⚠️ Análisis estadístico. No garantiza premios.")
st.markdown("🍀 **Pronósticos Lucky — suerte informada**")
