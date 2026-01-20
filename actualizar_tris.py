import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.resultadostris.com/"
CSV_FILE = "Tris.csv"

print("🔎 Iniciando actualización TRIS...")

# -----------------------------
# Leer CSV local
# -----------------------------
df = pd.read_csv(CSV_FILE)
df["Concurso"] = df["Concurso"].astype(int)

ultimo_local = df["Concurso"].max()
print(f"📄 Último concurso local: {ultimo_local}")

# -----------------------------
# Obtener página web
# -----------------------------
resp = requests.get(URL, timeout=15)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# -----------------------------
# Extraer concursos
# -----------------------------
concursos = []

for td in soup.find_all("td"):
    texto = td.get_text(strip=True)
    if texto.isdigit():
        num = int(texto)
        if num > 10000:  # filtro seguro TRIS
            concursos.append(num)

if not concursos:
    print("❌ No se encontraron concursos en la página")
    exit()

ultimo_web = max(concursos)
print(f"🌐 Último concurso web detectado: {ultimo_web}")

# -----------------------------
# Comparar
# -----------------------------
if ultimo_web <= ultimo_local:
    print("ℹ️ No hay sorteos nuevos.")
    exit()

# -----------------------------
# Extraer filas completas
# -----------------------------
nuevos = []

filas = soup.find_all("tr")

for fila in filas:
    cols = [c.get_text(strip=True) for c in fila.find_all("td")]

    if len(cols) >= 6 and cols[0].isdigit():
        concurso = int(cols[0])

        if concurso > ultimo_local:
            try:
                nuevos.append({
                    "Concurso": concurso,
                    "Fecha": cols[1],
                    "N1": int(cols[2]),
                    "N2": int(cols[3]),
                    "N3": int(cols[4]),
                    "N4": int(cols[5])
                })
            except:
                continue

if not nuevos:
    print("⚠️ No se pudieron construir nuevos registros.")
    exit()

df_nuevos = pd.DataFrame(nuevos)
df_final = pd.concat([df, df_nuevos], ignore_index=True)

df_final.sort_values("Concurso", inplace=True)
df_final.to_csv(CSV_FILE, index=False)

print(f"✅ Actualizados {len(df_nuevos)} sorteos nuevos.")
print(f"📈 CSV ahora llega hasta el concurso {df_final['Concurso'].max()}")
