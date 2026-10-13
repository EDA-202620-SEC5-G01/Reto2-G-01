"""
Comparacion experimental del Requerimiento 4: Reto 1 (listas) vs Reto 2 (tablas de hash).

Uso (desde cualquier carpeta):
    python benchmark_req4.py <ruta_al_repo_Reto1> [<ruta_al_repo_Reto2>]

Si no se da la ruta del Reto 2, se usa la carpeta donde esta este archivo.
Cada repo debe tener en su carpeta Data los archivos chocolate_sale_*.csv.

Para cada tamano de archivo se ejecutan 5 consultas distintas (las MISMAS en los dos
retos) y se mide solo el tiempo de req_4 (sin carga ni impresion). Cada combinacion
(reto, archivo) corre en un proceso aparte, porque ambos repos usan los paquetes
App y DataStructures con el mismo nombre.

Salida: resultados_req4.csv (una fila por ejecucion) y un resumen por consola.
"""
import csv
import json
import os
import subprocess
import sys

FILES = [
    ("chocolate_sale_20_ptc.csv", 0.2),
    ("chocolate_sale_40_ptc.csv", 0.4),
    ("chocolate_sale_60_ptc.csv", 0.6),
    ("chocolate_sale_80_ptc.csv", 0.8),
    ("chocolate_sale_100_ptc.csv", 1.0),
]

# Todas existen incluso en el archivo de 100 elementos, por lo tanto en todos los tamanos.
QUERIES = [
    ("70% Dark Bar", "Australia"),
    ("Truffle Gift Box", "Australia"),
    ("70% Dark Bar", "Brazil"),
    ("Milk Classic Bar", "Australia"),
    ("Truffle Gift Box", "Brazil"),
]


def worker(repo, filename):
    """Corre dentro del subproceso: carga el archivo y mide las 5 consultas."""
    os.chdir(repo)
    sys.path.insert(0, repo)
    sys.setrecursionlimit(10000)
    import App.logic as logic

    catalog = logic.new_logic()
    logic.load_data(catalog, filename)
    times = []
    for product, country in QUERIES:
        start = logic.get_time()
        res = logic.req_4(catalog, product, country)
        end = logic.get_time()
        if res is None:
            raise SystemExit("La consulta (%s, %s) no tiene resultados" % (product, country))
        times.append(logic.delta_time(start, end))
    print(json.dumps(times))


def run_worker(repo, filename):
    out = subprocess.run([sys.executable, os.path.abspath(__file__), "--worker", repo, filename],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("Fallo en %s / %s:\n%s" % (repo, filename, out.stderr or out.stdout))
    return json.loads(out.stdout.strip().splitlines()[-1])


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    reto1 = os.path.abspath(sys.argv[1])
    reto2 = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))

    rows = []
    summary = {}
    for filename, pct in FILES:
        for name, repo in (("Reto 1", reto1), ("Reto 2", reto2)):
            print("Ejecutando %s con %s ..." % (name, filename), flush=True)
            times = run_worker(repo, filename)
            summary[(name, pct)] = times
            for i, ((product, country), t) in enumerate(zip(QUERIES, times), start=1):
                rows.append([name, filename, pct, i, product, country, "%.6f" % t])

    with open("resultados_req4.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reto", "archivo", "porcentaje", "ejecucion", "producto", "pais", "ms"])
        w.writerows(rows)

    print("\nTiempos promedio de req_4 (ms), 5 ejecuciones por celda")
    print("%-10s %12s %12s" % ("Porcentaje", "Reto 1", "Reto 2"))
    for _, pct in FILES:
        a = sum(summary[("Reto 1", pct)]) / 5
        b = sum(summary[("Reto 2", pct)]) / 5
        print("%-10s %12.4f %12.4f" % (pct, a, b))
    print("\nGuardado: resultados_req4.csv")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--worker":
        worker(sys.argv[2], sys.argv[3])
    else:
        main()
