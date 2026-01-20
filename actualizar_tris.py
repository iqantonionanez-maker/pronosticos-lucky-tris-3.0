import pandas as pd
import requests
import re
from datetime import datetime

CSV_FILE = "Tris.csv"
URL = "https://www.resultadostris.com/"

print("🔎 Iniciando actualización TRIS...")

# =========================
# 1. Leer CSV local
# =========================
df = pd.read_csv(CSV_FILE)
df["CONCURSO"] = df["CONCURSO"].astype(int)

ultimo_concurso = df["CONCURSO"].max()
print(f"📄 Último concurso local: {ultimo_concurso}")

# =========================
# 2. Descargar página
# =========================
response = requests.get(URL, timeout=30)
response.raise_for_status()

texto = response.text

# =========================
# 3. Extraer resultados con REGEX
# =========================
# Formato detectado:
# 7 7 6 0 7 Tris Medio Día 35443
patron = re.compile(
    r"(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d).*?(\d{5})"
)

matches = patron.findall(texto)

nuevos = []

for r1, r2, r3, r4, r5, concurso in matches:
    concurso = int(concurso)

    if concurso <= ultimo_concurso:
        continue

    nuevos.append({
        "NPRODUCTO": 60,
        "CONCURSO": concurso,
        "R1": int(r1),
        "R2": int(r2),
        "R3": int(r3),
        "R4": int(r4),
        "R5": int(r5),
        "FECHA": datetime.now().strftime("%d/%m/%Y"),
        "Multiplicador": "NO"   # luego lo automatizamos
    })

# =========================
# 4. Guardar
# =========================
if nuevos:
    df_nuevos = pd.DataFrame(nuevos)
    df_final = pd.concat([df, df_nuevos], ignore_index=True)
    df_final.sort_values("CONCURSO", inplace=True)
    df_final.to_csv(CSV_FILE, index=False)

    print(f"✅ Se agregaron {len(nuevos)} concursos nuevos")
    print(f"🔢 Último concurso ahora: {df_final['CONCURSO'].max()}")
else:
    print("ℹ️ No hay sorteos nuevos")
