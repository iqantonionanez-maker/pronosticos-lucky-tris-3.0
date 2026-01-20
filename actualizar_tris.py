import pandas as pd
import requests
import sys

print("🔎 Iniciando actualización TRIS...")

CSV_LOCAL = "Tris.csv"
CSV_REMOTO = "https://raw.githubusercontent.com/lotomexico/resultados-tris/main/tris.csv"

# ---------- LEER LOCAL ----------
try:
    df_local = pd.read_csv(CSV_LOCAL)
    df_local["CONCURSO"] = df_local["CONCURSO"].astype(int)
    ultimo_concurso = df_local["CONCURSO"].max()
except Exception as e:
    print("❌ Error leyendo Tris.csv:", e)
    sys.exit(1)

print(f"📄 Último concurso local: {ultimo_concurso}")

# ---------- LEER REMOTO ----------
try:
    df_remoto = pd.read_csv(CSV_REMOTO)
    df_remoto["CONCURSO"] = df_remoto["CONCURSO"].astype(int)
except Exception as e:
    print("⚠️ No se pudo leer el CSV remoto.")
    print("Motivo:", e)
    sys.exit(0)

# ---------- FILTRAR NUEVOS ----------
df_nuevos = df_remoto[df_remoto["CONCURSO"] > ultimo_concurso]

if df_nuevos.empty:
    print("ℹ️ No hay sorteos nuevos.")
    sys.exit(0)

# ---------- GUARDAR ----------
df_final = pd.concat([df_local, df_nuevos], ignore_index=True)
df_final = df_final.sort_values("CONCURSO")

df_final.to_csv(CSV_LOCAL, index=False)

print(f"✅ Se agregaron {len(df_nuevos)} sorteos nuevos.")
print(f"🏁 Último concurso ahora: {df_final['CONCURSO'].max()}")
