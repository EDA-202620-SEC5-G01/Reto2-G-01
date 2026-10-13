"""
Reto 2 - Analisis de ventas de chocolate (ISIS-1225 2026-20)

Logica del reto: carga de datos y requerimientos.

Estructuras usadas (todas implementadas en el curso, ver carpeta DataStructures):
  * array_list            -> lista principal de pedidos, buckets de los indices y listas de resultados.
  * map_linear_probing    -> INDICES PERMANENTES construidos durante la carga (pocas llaves, sin borrados).
  * map_separate_chaining -> MAPAS TEMPORALES de agrupacion dentro de cada consulta (llaves desconocidas a priori).
  * merge_sort (array_list) -> unico ordenamiento usado (O(n log n) en el peor caso).

Indices construidos en la carga (llave -> array_list de pedidos):
  by_month            "YYYY-MM"           -> pedidos del mes                (Req. 1)
  by_country          "Country"           -> pedidos del pais               (Req. 2 y 5)
  by_product          "Product"           -> pedidos del producto           (Req. 6, pendiente)
  by_product_country  "Product|Country"   -> pedidos de la combinacion      (Req. 4)
  by_channel          "Channel"           -> numero de pedidos del canal    (reporte de carga)
"""
import csv
import os
import time

csv.field_size_limit(2147483647)

from DataStructures.List import array_list as al
from DataStructures.Map import map_linear_probing as lp
from DataStructures.Map import map_separate_chaining as sc

data_dir = os.path.dirname(os.path.realpath(__file__)) + "/../Data"


# ----------------------------------------------------------------------------
# Creacion del catalogo
# ----------------------------------------------------------------------------

def new_logic():
    """
    Crea el catalogo con la lista principal y los indices (tablas de hash).
    Linear Probing con factor de carga maximo 0.5: el numero de llaves distintas
    es pequeno y acotado (24 meses, 5 paises, 12 productos, 60 combinaciones,
    3 canales) y nunca se eliminan llaves. Si aparecieran mas llaves, el mapa
    hace rehash automaticamente.
    """
    catalog = {
        "orders": al.new_list(),
        "by_month": lp.new_map(48, 0.5),
        "by_country": lp.new_map(16, 0.5),
        "by_product": lp.new_map(32, 0.5),
        "by_product_country": lp.new_map(256, 0.5),
        "by_channel": lp.new_map(8, 0.5),
    }
    return catalog


# ----------------------------------------------------------------------------
# Criterios de ordenamiento: retornan True si a debe ir ANTES que b
# ----------------------------------------------------------------------------

def cmp_amount_desc(a, b):
    """Amount descendente; empate: Order_ID ascendente (carga)."""
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]


def cmp_req1(a, b):
    """Discount_Pct desc, Amount desc, Order_ID asc."""
    if a["Discount_Pct"] != b["Discount_Pct"]:
        return a["Discount_Pct"] > b["Discount_Pct"]
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]


def cmp_req4(a, b):
    """Amount desc, Marketing_Spend asc, Order_ID asc."""
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    if a["Marketing_Spend"] != b["Marketing_Spend"]:
        return a["Marketing_Spend"] < b["Marketing_Spend"]
    return a["Order_ID"] < b["Order_ID"]


def cmp_req5(a, b):
    """Recaudo total desc, total de cajas desc, nombre del producto asc."""
    if a["amount"] != b["amount"]:
        return a["amount"] > b["amount"]
    if a["boxes"] != b["boxes"]:
        return a["boxes"] > b["boxes"]
    return a["Product"] < b["Product"]



# ----------------------------------------------------------------------------
# Utilidades de indexacion
# ----------------------------------------------------------------------------

def _index_add(index, key, order):
    """Agrega un pedido al bucket (array_list) asociado a key; lo crea si no existe."""
    bucket = lp.get(index, key)
    if bucket is None:
        bucket = al.new_list()
        lp.put(index, key, bucket)
    al.add_last(bucket, order)


def _top_slice(lst, n):
    """Primeros n elementos de una array_list (o todos si hay menos)."""
    total = al.size(lst)
    k = n if n < total else total
    if k <= 0:
        return al.new_list()
    return al.sub_list(lst, 0, k)


# ----------------------------------------------------------------------------
# Carga de datos
# ----------------------------------------------------------------------------

def load_data(catalog, filename):
    """
    Carga los datos del reto leyendo el CSV UNA sola vez.

    En el mismo recorrido se construyen la lista principal y todos los indices.
    Luego se ordena una copia de la lista principal (merge sort) para entregar
    los 5 primeros y los 5 ultimos pedidos por Amount descendente.

    Retorna un diccionario con el reporte de carga. Se reportan por separado el
    tiempo de lectura+indexacion y el tiempo del ordenamiento.
    """
    t_start = get_time()

    orders = catalog["orders"]
    path = data_dir + "/" + filename

    max_order = None
    min_order = None
    min_date = None
    max_date = None

    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            order = {
                "Order_ID": row["Order_ID"],
                "Product": row["Product"],
                "Country": row["Country"],
                "Channel": row["Channel"],
                "Order_Date": row["Order_Date"],
                "Discount_Pct": float(row["Discount_Pct"]),
                "Price_per_Box": float(row["Price_per_Box"]),
                "Marketing_Spend": float(row["Marketing_Spend"]),
                "Boxes_Shipped": int(row["Boxes_Shipped"]),
                "Amount": float(row["Amount"]),
            }
            al.add_last(orders, order)

            # --- indices (tablas de hash) ---
            _index_add(catalog["by_month"], order["Order_Date"][:7], order)
            _index_add(catalog["by_country"], order["Country"], order)
            _index_add(catalog["by_product"], order["Product"], order)
            _index_add(catalog["by_product_country"],
                       order["Product"] + "|" + order["Country"], order)
            count = lp.get(catalog["by_channel"], order["Channel"])
            lp.put(catalog["by_channel"], order["Channel"],
                   1 if count is None else count + 1)

            # --- extremos ---
            if max_order is None:
                max_order = order
                min_order = order
                min_date = order["Order_Date"]
                max_date = order["Order_Date"]
            else:
                if cmp_amount_desc(order, max_order):
                    max_order = order
                if cmp_amount_desc(min_order, order):
                    min_order = order
                if order["Order_Date"] < min_date:
                    min_date = order["Order_Date"]
                if order["Order_Date"] > max_date:
                    max_date = order["Order_Date"]

    t_load = delta_time(t_start, get_time())

    # --- ordenamiento de TODOS los pedidos por Amount desc (sobre una copia) ---
    t_sort_start = get_time()
    total = al.size(orders)
    sorted_orders = al.sub_list(orders, 0, total) if total > 0 else al.new_list()
    al.merge_sort(sorted_orders, cmp_amount_desc)
    t_sort = delta_time(t_sort_start, get_time())

    first_5 = al.new_list()
    last_5 = al.new_list()
    for i in range(0, min(5, total)):
        al.add_last(first_5, al.get_element(sorted_orders, i))
    for i in range(max(0, total - 5), total):
        al.add_last(last_5, al.get_element(sorted_orders, i))

    channels = al.new_list()
    keys = lp.key_set(catalog["by_channel"])
    for i in range(al.size(keys)):
        ch = al.get_element(keys, i)
        al.add_last(channels, (ch, lp.get(catalog["by_channel"], ch)))

    return {
        "time_load": t_load,
        "time_sort": t_sort,
        "total": total,
        "channels": channels,
        "min_date": min_date,
        "max_date": max_date,
        "min_order": min_order,
        "max_order": max_order,
        "first_5": first_5,
        "last_5": last_5,
    }


# ----------------------------------------------------------------------------
# Requerimientos
# ----------------------------------------------------------------------------

def req_1(catalog, year, month, disc_min, disc_max):
    """
    Req. 1 (individual): pedidos de un mes con Discount_Pct en [disc_min, disc_max].

    Acceso por hash: by_month["YYYY-MM"] entrega SOLO los pedidos del mes (no se
    recorre la lista principal). Dentro de ese bucket se filtra por descuento y
    se ordena el resultado con merge sort.
    """
    key = "%04d-%02d" % (year, month)
    bucket = lp.get(catalog["by_month"], key)

    result = al.new_list()
    total_amount = 0.0
    sum_price = 0.0
    sum_boxes = 0

    if bucket is not None:
        for i in range(al.size(bucket)):
            order = al.get_element(bucket, i)
            if disc_min <= order["Discount_Pct"] <= disc_max:
                al.add_last(result, order)
                total_amount += order["Amount"]
                sum_price += order["Price_per_Box"]
                sum_boxes += order["Boxes_Shipped"]

    count = al.size(result)
    if count > 1:
        al.merge_sort(result, cmp_req1)

    return {
        "count": count,
        "total_amount": total_amount,
        "avg_price": sum_price / count if count > 0 else 0.0,
        "avg_boxes": sum_boxes / count if count > 0 else 0.0,
        "orders": result,
    }


def req_2(catalog, country, boxes_min, boxes_max):
    """
    Req. 2 (individual - MATEO): pedidos de un pais con Boxes_Shipped en [boxes_min, boxes_max].

    Pista de diseno: el indice catalog["by_country"] (llave = pais, valor = array_list de
    pedidos) ya se construye en la carga. Ver req_1 y req_5 como ejemplos del patron.
    """
    # TODO (Mateo): implementar el requerimiento 2
    pass

def req_3(catalog):
    """
    Req. 3: no asignado (el equipo tiene 2 integrantes y resuelve 2 individuales).
    """
    return None


def req_4(catalog, product, country):
    """
    Req. 4 (grupal): estadisticas de una combinacion Producto-Pais y los 2 pedidos
    de mayor Amount.

    Acceso por hash: by_product_country["Product|Country"] entrega solo los pedidos
    de la combinacion. Una sola pasada sobre ese bucket; el top 2 se mantiene
    sin ordenar (O(m)).
    """
    bucket = lp.get(catalog["by_product_country"], product + "|" + country)
    if bucket is None or al.size(bucket) == 0:
        return None

    count = al.size(bucket)
    sum_price = 0.0
    sum_discount = 0.0
    sum_marketing = 0.0
    sum_boxes = 0
    top1 = None
    top2 = None

    for i in range(count):
        order = al.get_element(bucket, i)
        sum_price += order["Price_per_Box"]
        sum_discount += order["Discount_Pct"]
        sum_marketing += order["Marketing_Spend"]
        sum_boxes += order["Boxes_Shipped"]
        if top1 is None:
            top1 = order
        elif cmp_req4(order, top1):
            top2 = top1
            top1 = order
        elif top2 is None or cmp_req4(order, top2):
            top2 = order

    return {
        "count": count,
        "avg_price": sum_price / count,
        "avg_discount": sum_discount / count,
        "avg_marketing": sum_marketing / count,
        "avg_boxes": sum_boxes / count,
        "top1": top1,
        "top2": top2,
    }


def req_5(catalog, n, country, date_from, date_to):
    """
    Req. 5 (grupal): los N productos con mayor recaudo en un pais y un rango de fechas.

    by_country[country] -> filtro por fecha (ISO, comparable como texto) -> mapa
    temporal producto -> acumulados -> merge sort del ranking.
    """
    bucket = lp.get(catalog["by_country"], country)

    products = sc.new_map(16, 4)
    count = 0
    total_amount = 0.0

    if bucket is not None:
        for i in range(al.size(bucket)):
            order = al.get_element(bucket, i)
            if date_from <= order["Order_Date"] <= date_to:
                count += 1
                total_amount += order["Amount"]
                agg = sc.get(products, order["Product"])
                if agg is None:
                    agg = {"Product": order["Product"], "orders": 0, "boxes": 0,
                           "amount": 0.0, "sum_price": 0.0, "sum_discount": 0.0,
                           "marketing": 0.0}
                    sc.put(products, order["Product"], agg)
                agg["orders"] += 1
                agg["boxes"] += order["Boxes_Shipped"]
                agg["amount"] += order["Amount"]
                agg["sum_price"] += order["Price_per_Box"]
                agg["sum_discount"] += order["Discount_Pct"]
                agg["marketing"] += order["Marketing_Spend"]

    ranking = sc.value_set(products)
    if al.size(ranking) > 1:
        al.merge_sort(ranking, cmp_req5)
    top = _top_slice(ranking, n)

    for i in range(al.size(top)):
        agg = al.get_element(top, i)
        agg["avg_price"] = agg["sum_price"] / agg["orders"]
        agg["avg_discount"] = agg["sum_discount"] / agg["orders"]

    return {
        "count": count,
        "distinct_products": sc.size(products),
        "total_amount": total_amount,
        "top": top,
    }


def req_6(catalog, n, product, date_from, date_to):
    """
    Req. 6 (grupal - MATEO): los N paises con mayor eficiencia de mercadeo para un producto
    y un rango de fechas. Eficiencia = sum(Amount) / sum(Marketing_Spend).

    Pista de diseno: el indice catalog["by_product"] (llave = producto, valor = array_list
    de pedidos) ya se construye en la carga. Ver req_5 como ejemplo del patron
    "bucket -> filtro por fecha -> mapa temporal de agrupacion -> ordenamiento".
    """
    # TODO (Mateo): implementar el requerimiento 6
    pass


# ----------------------------------------------------------------------------
# Funciones para medir tiempos de ejecucion
# ----------------------------------------------------------------------------

def get_time():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter() * 1000)


def delta_time(start, end):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed
