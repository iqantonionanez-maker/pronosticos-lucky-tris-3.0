import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

print("🔎 Iniciando actualización TRIS...")

# ================= CONFIG =================
URL = "https://www.loteria-resultados.com/mexico/tris"
CSV_FILE = "Tris.csv"
TIMEOUT = 30
# ==========================================

# ---------- CARGAR CSV ----------
try:
    df = pd.read_csv(CSV_FILE)
    df["CONCURSO"] = df["CONCURSO"].astype(int)
    ultimo_concurso = df["CONCURSO"].max()
except Exception as e:
    print("❌ Error leyendo Tris.csv:", e)
    sys.exit(1)

print(f"📄 Último concurso en CSV: {ultimo_concurso}")

# ---------- OBTENER WEB ----------
try:
    response = requests.get(URL, timeout=TIMEOUT, headers={
        "User-Agent": "Mozilla/5.0"
    })
    response.raise_for_status()
except Exception as e:
    print("⚠️ No se pudo acceder a la fuente externa.")
    print("Motivo:", e)
    print("➡️ Se cancela actualización sin romper el CSV.")
    sys.exit(0)

soup = BeautifulSoup(response.text, "html.parser")

# ---------- EXTRAER RESULTADOS ----------
nuevos = []

tabla = soup.find("table")
if not tabla:
    print("⚠️ No se encontró la tabla de resultados.")
    sys.exit(0)

filas = tabla.find_all("tr")[1:]

for fila in filas:
    cols = fila.find_all("td")
    if len(cols) < 7:
        continue

    try:
        concurso = int(cols[0].text.strip())
        fecha = datetime.strptime(cols[1].text.strip(), "%d/%m/%Y")

        numeros = cols[2].text.strip().replace(" ", "")
        r = list(numeros)

        if concurso <= ultimo_concurso:
            continue

        nuevos.append({
            "CONCURSO": concurso,
            "FECHA": fecha.strftime("%d/%m/%Y"),
            "R1": r[0],
            "R2": r[1],
            "R3": r[2],
            "R4": r[3],
            "R5": r[4]
        })

    except Exception:
        continue

# ---------- GUARDAR ----------
if not nuevos:
    print("ℹ️ No hay sorteos nuevos.")
    sys.exit(0)

df_nuevos = pd.DataFrame(nuevos)
df_final = pd.concat([df, df_nuevos], ignore_index=True)
df_final = df_final.sort_values("CONCURSO")

df_final.to_csv(CSV_FILE, index=False)

print(f"✅ Actualización exitosa: {len(nuevos)} sorteos nuevos añadidos.")
print(f"🏁 Último concurso ahora: {df_final['CONCURSO'].max()}")
