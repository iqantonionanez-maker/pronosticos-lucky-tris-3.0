import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("🔎 Iniciando actualización TRIS...")

# 1️⃣ Leer CSV actual
df = pd.read_csv("Tris.csv")

ultimo_concurso_csv = df["CONCURSO"].max()
print(f"📄 Último concurso en CSV: {ultimo_concurso_csv}")

# 2️⃣ Fuente externa (HTML simple)
URL = "https://resultados.gob.mx/loteria/tris"
response = requests.get(URL, timeout=30)

if response.status_code != 200:
    print("❌ No se pudo acceder a la página de resultados")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

tabla = soup.find("table")
if not tabla:
    print("❌ No se encontró la tabla de resultados")
    exit()

filas = tabla.find_all("tr")[1:]

nuevos_registros = []

for fila in filas:
    cols = [c.text.strip() for c in fila.find_all("td")]

    if len(cols) < 7:
        continue

    concurso = int(cols[0])
    fecha = datetime.strptime(cols[1], "%d/%m/%Y")

    if concurso <= ultimo_concurso_csv:
        continue

    r1, r2, r3, r4, r5 = map(int, cols[2:7])

    nuevos_registros.append({
        "CONCURSO": concurso,
        "FECHA": fecha.strftime("%d/%m/%Y"),
        "R1": r1,
        "R2": r2,
        "R3": r3,
        "R4": r4,
        "R5": r5
    })

if not nuevos_registros:
    print("ℹ️ No hay sorteos nuevos para agregar")
    exit()

df_nuevos = pd.DataFrame(nuevos_registros)
df_final = pd.concat([df, df_nuevos], ignore_index=True)
df_final = df_final.sort_values("CONCURSO")

df_final.to_csv("Tris.csv", index=False)

print(f"✅ Sorteos nuevos agregados: {len(nuevos_registros)}")
print(f"🏁 Último concurso ahora: {df_final['CONCURSO'].max()}")
