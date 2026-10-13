import sys

default_limit = 1000
sys.setrecursionlimit(default_limit * 10)

import App.logic as logic
from DataStructures.List import array_list as al

FILES = [
    "chocolate_sale_100_elementos.csv",
    "chocolate_sale_20_ptc.csv",
    "chocolate_sale_40_ptc.csv",
    "chocolate_sale_60_ptc.csv",
    "chocolate_sale_80_ptc.csv",
    "chocolate_sale_100_ptc.csv",
]


def new_logic():
    """
        Se crea una instancia del controlador
    """
    control = logic.new_logic()
    return control


def print_menu():
    print("\nBienvenido")
    print("0- Cargar información")
    print("1- Ejecutar Requerimiento 1")
    print("2- Ejecutar Requerimiento 2 (pendiente: Mateo)")
    print("3- Ejecutar Requerimiento 3 (no asignado a este equipo)")
    print("4- Ejecutar Requerimiento 4")
    print("5- Ejecutar Requerimiento 5")
    print("6- Ejecutar Requerimiento 6 (pendiente: Mateo)")
    print("7- Salir")


# ---------------------------------------------------------------------------
# Utilidades de impresion (sin librerias externas)
# ---------------------------------------------------------------------------

def money(value):
    return "$%.2f" % value


def print_table(headers, rows):
    """Imprime una tabla con bordes. rows es una lista de listas."""
    table = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in table:
        for j, cell in enumerate(row):
            if len(cell) > widths[j]:
                widths[j] = len(cell)
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(line)
    print("| " + " | ".join(h.ljust(widths[j]) for j, h in enumerate(headers)) + " |")
    print(line)
    for row in table:
        print("| " + " | ".join(c.ljust(widths[j]) for j, c in enumerate(row)) + " |")
    print(line)


def read_int(message):
    return int(input(message).strip())


def read_float(message):
    return float(input(message).strip())


def head_tail(lst, limit=20, part=10):
    """
    Si la lista tiene mas de `limit` elementos, retorna (primeros `part`, ultimos `part`, True);
    en caso contrario retorna (todos, None, False).
    """
    total = al.size(lst)
    if total > limit:
        first = [al.get_element(lst, i) for i in range(part)]
        last = [al.get_element(lst, i) for i in range(total - part, total)]
        return first, last, True
    return [al.get_element(lst, i) for i in range(total)], None, False


def print_orders(lst, headers, to_row):
    """Imprime los pedidos de lst; si son mas de 20, solo los primeros 10 y los ultimos 10."""
    if al.size(lst) == 0:
        return
    first, last, cut = head_tail(lst)
    if not cut:
        print_table(headers, [to_row(o) for o in first])
    else:
        print("Primeros 10 de %d pedidos:" % al.size(lst))
        print_table(headers, [to_row(o) for o in first])
        print("Últimos 10 de %d pedidos:" % al.size(lst))
        print_table(headers, [to_row(o) for o in last])


def not_loaded(control):
    if al.size(control["orders"]) == 0:
        print("Primero debe cargar la información (opción 0).")
        return True
    return False


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def load_data(control):
    """
    Carga los datos
    """
    if al.size(control["orders"]) > 0:
        print("Los datos ya fueron cargados. Reinicie el programa para cargar otro archivo.")
        return None

    print("Archivos disponibles:")
    for i, name in enumerate(FILES):
        print("  %d- %s" % (i + 1, name))
    choice = input("Seleccione el archivo (Enter = 1): ").strip()
    idx = int(choice) - 1 if choice != "" else 0
    if idx < 0 or idx >= len(FILES):
        print("Opción de archivo inválida.")
        return None
    filename = FILES[idx]

    print("Cargando información de %s ....\n" % filename)
    res = logic.load_data(control, filename)

    print("Reporte de carga de datos")
    print("--------------------------")
    print("Tiempo de carga (lectura + tablas de hash): %.3f ms" % res["time_load"])
    print("Tiempo de ordenamiento por Amount desc:     %.3f ms" % res["time_sort"])
    print("Total de pedidos cargados: %d" % res["total"])
    print("Pedidos por canal de venta:")
    print_table(["Channel", "Pedidos"],
                [[c, n] for c, n in [al.get_element(res["channels"], i)
                                     for i in range(al.size(res["channels"]))]])
    print("Fecha más antigua: %s    Fecha más reciente: %s\n" % (res["min_date"], res["max_date"]))

    headers = ["Order_ID", "Product", "Country", "Channel", "Order_Date",
               "Boxes_Shipped", "Price_per_Box", "Amount"]

    def row(o):
        return [o["Order_ID"], o["Product"], o["Country"], o["Channel"], o["Order_Date"],
                o["Boxes_Shipped"], money(o["Price_per_Box"]), money(o["Amount"])]

    print("-- Pedido con Amount mínimo --")
    print_table(headers, [row(res["min_order"])])
    print("-- Pedido con Amount máximo --")
    print_table(headers, [row(res["max_order"])])
    print("-- Primeros 5 pedidos (Amount descendente) --")
    print_table(headers, [row(al.get_element(res["first_5"], i)) for i in range(al.size(res["first_5"]))])
    print("-- Últimos 5 pedidos (Amount descendente) --")
    print_table(headers, [row(al.get_element(res["last_5"], i)) for i in range(al.size(res["last_5"]))])
    return res


def print_data(control, id):
    """
        Función que imprime un dato dado su ID
    """
    pass


# ---------------------------------------------------------------------------
# Requerimientos
# ---------------------------------------------------------------------------

def print_req_1(control):
    """
        Función que imprime la solución del Requerimiento 1 en consola
    """
    if not_loaded(control):
        return
    year = read_int("Año del pedido (YYYY): ")
    month = read_int("Mes del pedido (1-12): ")
    if month < 1 or month > 12:
        print("El mes debe estar entre 1 y 12.")
        return
    disc_min = read_float("Descuento mínimo (%): ")
    disc_max = read_float("Descuento máximo (%): ")
    if disc_min > disc_max:
        print("El descuento mínimo no puede ser mayor que el máximo.")
        return

    start = logic.get_time()
    res = logic.req_1(control, year, month, disc_min, disc_max)
    end = logic.get_time()

    print("\n--- Resultados Requerimiento 1 ---")
    print("Tiempo de ejecución: %.3f ms" % logic.delta_time(start, end))
    print("Pedidos que cumplen el filtro: %d" % res["count"])
    if res["count"] == 0:
        print("No se encontraron pedidos con esos parámetros.")
        return
    print("Monto total recaudado: %s" % money(res["total_amount"]))
    print("Promedio Price_per_Box: %s" % money(res["avg_price"]))
    print("Promedio Boxes_Shipped: %.2f\n" % res["avg_boxes"])

    headers = ["Order_ID", "Product", "Country", "Channel", "Order_Date",
               "Discount_Pct", "Price_per_Box", "Boxes_Shipped", "Amount"]
    print_orders(res["orders"], headers,
                 lambda o: [o["Order_ID"], o["Product"], o["Country"], o["Channel"],
                            o["Order_Date"], "%.1f%%" % o["Discount_Pct"],
                            money(o["Price_per_Box"]), o["Boxes_Shipped"], money(o["Amount"])])


def print_req_2(control):
    """
        Función que imprime la solución del Requerimiento 2 en consola
    """
    # TODO (Mateo): pedir los parámetros, medir el tiempo e imprimir el resultado del Req. 2
    print("El Requerimiento 2 aún no está implementado.")

def print_req_3(control):
    """
        Función que imprime la solución del Requerimiento 3 en consola
    """
    print("El Requerimiento 3 no fue asignado a este equipo (grupo de 2 integrantes).")


def print_req_4(control):
    """
        Función que imprime la solución del Requerimiento 4 en consola
    """
    if not_loaded(control):
        return
    product = input("Producto: ").strip()
    country = input("País: ").strip()

    start = logic.get_time()
    res = logic.req_4(control, product, country)
    end = logic.get_time()

    print("\n--- Resultados Requerimiento 4 ---")
    print("Tiempo de ejecución: %.3f ms" % logic.delta_time(start, end))
    if res is None:
        print("No se encontró ningún pedido con el producto '%s' y el país '%s'." % (product, country))
        return
    print("Pedidos que cumplen el filtro: %d" % res["count"])
    print_table(["Característica", "Promedio"], [
        ["Price_per_Box", money(res["avg_price"])],
        ["Discount_Pct", "%.2f%%" % res["avg_discount"]],
        ["Marketing_Spend", money(res["avg_marketing"])],
        ["Boxes_Shipped", "%.2f" % res["avg_boxes"]],
    ])
    rows = []
    for label, o in (("Top 1", res["top1"]), ("Top 2", res["top2"])):
        if o is not None:
            rows.append([label, o["Order_ID"], o["Channel"], o["Order_Date"],
                         o["Boxes_Shipped"], money(o["Amount"])])
    print("-- Los 2 pedidos de mayor Amount --")
    print_table(["Puesto", "Order_ID", "Channel", "Order_Date", "Boxes_Shipped", "Amount"], rows)


def print_req_5(control):
    """
        Función que imprime la solución del Requerimiento 5 en consola
    """
    if not_loaded(control):
        return
    n = read_int("Número N de productos: ")
    if n <= 0:
        print("N debe ser mayor que cero.")
        return
    country = input("País: ").strip()
    date_from = input("Fecha inicial (YYYY-MM-DD): ").strip()
    date_to = input("Fecha final (YYYY-MM-DD): ").strip()

    start = logic.get_time()
    res = logic.req_5(control, n, country, date_from, date_to)
    end = logic.get_time()

    print("\n--- Resultados Requerimiento 5 ---")
    print("Tiempo de ejecución: %.3f ms" % logic.delta_time(start, end))
    print("Pedidos que cumplen el filtro: %d" % res["count"])
    if res["count"] == 0:
        print("No se encontraron pedidos con esos parámetros.")
        return
    print("Productos diferentes encontrados: %d" % res["distinct_products"])
    print("Recaudo total: %s\n" % money(res["total_amount"]))
    rows = []
    for i in range(al.size(res["top"])):
        p = al.get_element(res["top"], i)
        rows.append([p["Product"], p["orders"], p["boxes"], money(p["amount"]),
                     money(p["avg_price"]), "%.2f%%" % p["avg_discount"], money(p["marketing"])])
    print_table(["Product", "Pedidos", "Total Boxes_Shipped", "Recaudo total",
                 "Price_per_Box prom.", "Discount_Pct prom.", "Marketing_Spend total"], rows)


def print_req_6(control):
    """
        Función que imprime la solución del Requerimiento 6 en consola
    """
    # TODO (Mateo): pedir los parámetros, medir el tiempo e imprimir el resultado del Req. 6
    print("El Requerimiento 6 aún no está implementado.")


# Se crea la lógica asociado a la vista
control = new_logic()


# main del ejercicio
def main():
    """
    Menu principal
    """
    working = True
    # ciclo del menu
    while working:
        print_menu()
        inputs = input('Seleccione una opción para continuar\n').strip()
        try:
            option = int(inputs)
        except ValueError:
            print("Opción errónea, vuelva a elegir.\n")
            continue
        try:
            if option == 0:
                load_data(control)
            elif option == 1:
                print_req_1(control)
            elif option == 2:
                print_req_2(control)
            elif option == 3:
                print_req_3(control)
            elif option == 4:
                print_req_4(control)
            elif option == 5:
                print_req_5(control)
            elif option == 6:
                print_req_6(control)
            elif option == 7:
                working = False
                print("\nGracias por utilizar el programa")
            else:
                print("Opción errónea, vuelva a elegir.\n")
        except ValueError:
            print("Entrada inválida: revise que los números estén bien escritos.\n")
    sys.exit(0)
