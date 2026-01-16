# ---------------- NÚMEROS SIMILARES (LÓGICA DEFINITIVA) ----------------
st.subheader("🔄 Números similares")

from itertools import permutations

def generar_similares_inteligentes(num):
    similares = []
    largo = len(num)
    digitos = list(num)

    # 1️⃣ Permutaciones con los mismos dígitos
    perms = set(
        ["".join(p) for p in permutations(digitos, largo)]
    )
    perms.discard(num)

    for p in perms:
        if len(similares) < 5:
            similares.append(p)

    # 2️⃣ Vecinos (+1 / -1) si no alcanza
    n = int(num)
    if len(similares) < 5:
        similares.append(str(n - 1).zfill(largo))
    if len(similares) < 5:
        similares.append(str(n + 1).zfill(largo))

    # 3️⃣ Agregar 0 SOLO si aún no alcanza
    if len(similares) < 5:
        similares.append("0" + num)
    if len(similares) < 5:
        similares.append(num + "0")

    # Eliminar duplicados y limitar a 5
    similares = list(dict.fromkeys(similares))[:5]

    return similares

if seleccion and seleccion.isdigit():
    similares = generar_similares_inteligentes(seleccion)
    tabla = []

    for s in similares:
        d = df_modalidad[df_modalidad["JUGADA"] == s]
        if len(d) > 0:
            tabla.append({
                "Número": s,
                "Apariciones": len(d),
                "Última fecha": d["FECHA"].max().date(),
                "Sorteos sin salir": df_modalidad["CONCURSO"].max() - d["CONCURSO"].max(),
                "Promedio": round(total_sorteos / len(d), 2)
            })
        else:
            tabla.append({
                "Número": s,
                "Apariciones": 0,
                "Última fecha": "Nunca",
                "Sorteos sin salir": "N/A",
                "Promedio": "N/A"
            })

    st.dataframe(pd.DataFrame(tabla))
