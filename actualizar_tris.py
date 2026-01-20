import pandas as pd
from playwright.sync_api import sync_playwright
import os

CSV_LOCAL = "Tris.csv"
DOWNLOAD_DIR = "downloads"

def descargar_csv_oficial():
    print("🌐 Abriendo página oficial TRIS...")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto("https://www.loterianacional.gob.mx/Tris/resultados", timeout=60000)
        page.wait_for_load_state("networkidle")

        print("⬇️ Buscando enlace de descarga CSV...")

        with page.expect_download() as download_info:
            page.locator("a[href$='.csv']").first.click()

        download = download_info.value
        ruta_csv = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
        download.save_as(ruta_csv)

        browser.close()

    print(f"📁 CSV descargado: {ruta_csv}")
    return ruta_csv


def normalizar_csv(df):
    print("🧹 Normalizando estructura del CSV oficial...")

    df.columns = [c.strip() for c in df.columns]

    df = df.rename(columns={
        "Sorteo": "CONCURSO",
        "Fecha": "FECHA"
    })

    df["NPRODUCTO"] = 60

    df["Combinación Ganadora"] = df["Combinación Ganadora"].astype(str).str.zfill(5)

    df["R1"] = df["Combinación Ganadora"].str[0].astype(int)
    df["R2"] = df["Combinación Ganadora"].str[1].astype(int)
    df["R3"] = df["Combinación Ganadora"].str[2].astype(int)
    df["R4"] = df["Combinación Ganadora"].str[3].astype(int)
    df["R5"] = df["Combinación Ganadora"].str[4].astype(int)

    df["Multiplicador"] = df["Multiplicador"].astype(str).str.upper().replace({"SÍ": "SI"})

    df_final = df[[
        "NPRODUCTO",
        "CONCURSO",
        "R1", "R2", "R3", "R4", "R5",
        "FECHA",
        "Multiplicador"
    ]]

    return df_final


def actualizar_tris():
    print("🔎 Iniciando actualización TRIS...")

    if os.path.exists(CSV_LOCAL):
        df_local = pd.read_csv(CSV_LOCAL)
        ultimo_local = df_local["CONCURSO"].max()
        print(f"📄 Último concurso local: {ultimo_local}")
    else:
        df_local = pd.DataFrame()
        ultimo_local = 0
        print("📄 No existe CSV local, se creará uno nuevo")

    ruta_csv_oficial = descargar_csv_oficial()
    df_oficial_raw = pd.read_csv(ruta_csv_oficial)

    df_oficial = normalizar_csv(df_oficial_raw)

    nuevos = df_oficial[df_oficial["CONCURSO"] > ultimo_local]

    if nuevos.empty:
        print("ℹ️ No hay sorteos nuevos")
        return

    print(f"🆕 Nuevos sorteos encontrados: {len(nuevos)}")

    df_final = pd.concat([df_local, nuevos], ignore_index=True)
    df_final = df_final.sort_values("CONCURSO", ascending=False)

    df_final.to_csv(CSV_LOCAL, index=False)
    print("✅ Archivo TRIS actualizado correctamente")


if __name__ == "__main__":
    actualizar_tris()
