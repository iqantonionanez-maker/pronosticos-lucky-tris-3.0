import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

CSV_LOCAL = "Tris.csv"
URL = "https://www.resultadostris.com/"

def obtener_ultimos_resultados():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    resultados = []

    # Cada sorteo está en una tabla
    filas = soup.select("table tbody tr")

    for fila in filas:
        cols = [c.get_text(strip=True) for c in fila.find_all("td")]

        if len(cols) < 5:
            continue

        concurso = int(cols[0])
        combinacion = cols[1].zfill(5)
        fecha = datetime.strptime(cols[2], "%d/%m/%Y").strftime("%d/%m/%Y")
        multiplicador = "SI" if "SI" in cols[3].upper() else "NO"

        resultados.append({
            "NPRODUCTO": 60,
            "CONCURSO": concurso,
            "R1": int(combinacion[0]),
            "R2": int(combinacion[1]),
            "R3": int(combinacion[2]),
            "R4": int(combinacion[3]),
            "R5": int(combinacion[4]),
            "FECHA": fecha,
            "Multiplicador": multiplicador
        })

    return pd.DataFrame(resultados)

def actualizar_tris():
    print("🔎 Iniciando actualización TRIS...")

    if os.path.exists(CSV_LOCAL):
        df_local = pd.read_csv(CSV_LOCAL)
        ultimo_concurso = df_local["CONCURSO"].max()
        print(f"📄 Último concurso local: {ultimo_concurso}")
    else:
        df_local = pd.DataFrame()
        ultimo_concurso = 0
        print("📄 No existe CSV local, se creará uno nuevo")

    df_web = obtener_ultimos_resultados()

    nuevos = df_web[df_web["CONCURSO"] > ultimo_concurso]

    if nuevos.empty:
        print("ℹ️ No hay sorteos nuevos")
        return

    print(f"🆕 Sorteos nuevos encontrados: {len(nuevos)}")

    df_final = pd.concat([df_local, nuevos], ignore_index=True)
    df_final = df_final.sort_values("CONCURSO", ascending=False)

    df_final.to_csv(CSV_LOCAL, index=False)
    print("✅ Tris.csv actualizado correctamente")

if __name__ == "__main__":
    actualizar_tris()
