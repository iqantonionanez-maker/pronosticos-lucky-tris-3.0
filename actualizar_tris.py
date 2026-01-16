import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.trisdehoy.mx/resultados"

def obtener_ultimo_sorteo():
    r = requests.get(URL, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    fila = soup.find("tr", class_="resultado-activo")
    if not fila:
        return None

    columnas = fila.find_all("td")
    concurso = int(columnas[0].text.strip())
    numeros = list(columnas[1].text.strip())

    return {
        "CONCURSO": concurso,
        "R1": int(numeros[0]),
        "R2": int(numeros[1]),
        "R3": int(numeros[2]),
        "R4": int(numeros[3]),
        "R5": int(numeros[4]),
        "FECHA": datetime.now().strftime("%d/%m/%Y")
    }

def actualizar_csv():
    df = pd.read_csv("Tris.csv")
    ultimo = obtener_ultimo_sorteo()

    if ultimo and ultimo["CONCURSO"] not in df["CONCURSO"].values:
        df = pd.concat([df, pd.DataFrame([ultimo])], ignore_index=True)
        df.to_csv("Tris.csv", index=False)

if __name__ == "__main__":
    actualizar_csv()
