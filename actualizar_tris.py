import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

URL = "https://www.resultadostris.com/"
CSV_LOCAL = "Tris.csv"

print("🔎 Iniciando actualización TRIS...")

# ---------------- LEER CSV LOCAL ----------------
try:
    df_local = pd.read_csv(CSV_LOCAL)
    df_local["CONCURSO"] = df_local["CONCURSO"].astype(int)
    ultimo_concurso = df_local["CONCURSO"].max()
except Exception as e:
    print("❌ Error leyendo Tris.csv:", e)
    sys.exit(1)

print(f"📄 Último concurso local: {ultimo_concurso}")

# ---------------- LEER WEB ----------------
try:
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
except Exception as e:
    print("❌ Error accediendo a la web:", e)
    sys.exit(0)

soup = BeautifulSoup(response.text, "html.parser")

# ---------------- EXTRAER RESULTADOS ----------------
resultados = []

# Cada resultado está en bloques con números y texto
for fila in soup.find_all("div", class_="resultado"):
    texto = fila.get_text(" ", strip=True)

    # Ejemplo esperado:
    # "7 7 6 0 7 Tris Medio Día 35443 03/01/2026"
    partes = texto.split()

    try:
        numeros = partes[0:5]
        concurso = int(partes[-2])
        fecha = partes[-1]

        if concurso <= ultimo_concurso:
            continue

        fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

        resultados.append({
            "CONCURSO": concurso,
            "FECHA": fecha_dt.strftime("%d/%m/%Y"),
            "R1": int(numeros[0]),
            "R2": int(numeros[1]),
            "R3": int(numeros[2]),
            "R4": int(numeros[3]),
            "R5": int(numeros[4])
        })

    except Exception:
        continue

if not resultados:
    print("ℹ️ No hay sorteos nuevos.")
    sys.exit(0)

# ---------------- GUARDAR ----------------
df_nuevos = pd.DataFrame(resultados)
df_final = pd.concat([df_local, df_nuevos], ignore_index=True)
df_final = df_final.sort_values("CONCURSO")

df_final.to_csv(CSV_LOCAL, index=False)

print(f"✅ Se agregaron {len(df_nuevos)} sorteos nuevos.")
print(f"🏁 Último concurso ahora: {df_final['CONCURSO'].max()}")
