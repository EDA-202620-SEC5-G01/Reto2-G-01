from DataStructures.List import array_list as al
from DataStructures.Map import map_entry as me
from DataStructures.Map import map_functions as mf
import random

def new_map(num_elements,load_factor,prime=109345121):
    capacity = mf.next_prime(num_elements / load_factor)
    table = al.new_list()
    for i in range(capacity):
        al.add_last(table, me.new_map_entry(None, None))
    return {
        'prime':prime,
        'capacity':capacity,
        'scale':random.randint(1,prime-1),
        'shift':random.randint(0,prime-1),
        'table':table,
        'current_factor':0,
        'limit_factor':load_factor,
        'size':0,
    }

def is_available(table, pos):
    """Verifica si la posición está disponible."""
    entry = al.get_element(table, pos)
    key = me.get_key(entry)
    if key is None or key == "__EMPTY__":
        return True
    return False
def default_compare(key, entry):
    """Función de comparación usando map_entry functions."""
    entry_key = me.get_key(entry)
    if key == entry_key:
        return 0
    elif key > entry_key:
        return 1
    return -1
def find_slot(my_map, key, hash_value):
    
    first_avail = None
    found = False
    ocupied = False
    pos = hash_value % my_map["capacity"]

    while not found:
        if is_available(my_map["table"], pos):
            if first_avail is None:
                first_avail = pos
            entry = al.get_element(my_map["table"], pos)
            if me.get_key(entry) is None:
                found = True
        else:
            entry = al.get_element(my_map["table"], pos)
            if default_compare(key, entry) == 0:
                first_avail = pos
                found = True
                ocupied = True

        if not found:
            pos = (pos + 1) % my_map["capacity"]

    return ocupied, first_avail
def hash_value(my_map, key):
    """Función hash optimizada usando map_functions."""
    return mf.hash_value(my_map, key)
def contains(my_map, key):
    """Verifica si una llave existe."""
    key_hash = hash_value(my_map, key)
    ocupied, pos = find_slot(my_map, key, key_hash)
    return ocupied
def get(my_map, key):
    """Obtiene el valor asociado a una llave."""
    key_hash = hash_value(my_map, key)
    ocupied, pos = find_slot(my_map, key, key_hash)

    if ocupied:
        tabla = my_map["table"]
        entry = al.get_element(tabla, pos)
        return me.get_value(entry)

    return None
def rehash(my_map):
    
    # Guardar elementos actuales
    old_table = my_map["table"]
    old_capacity = my_map["capacity"]

    # Crear nueva tabla con mayor capacidad
    new_capacity = mf.next_prime(old_capacity * 2)
    my_map["table"] = al.new_list()
    my_map["capacity"] = new_capacity
    my_map["size"] = 0
    my_map["current_factor"] = 0.0

    # Inicializar nueva tabla
    for i in range(new_capacity):
        al.add_last(my_map["table"], me.new_map_entry(None, None))

    # Reinsertar elementos válidos
    for i in range(al.size(old_table)):
        entry = al.get_element(old_table, i)
        key = me.get_key(entry)
        if key is not None and key != "__EMPTY__":
            value = me.get_value(entry)
            put(my_map, key, value)

    return my_map

def put(my_map,key,value):
    
    key_hash = hash_value(my_map, key)
    ocupied, pos = find_slot(my_map, key, key_hash)
    
    if ocupied:
        entry = al.get_element(my_map["table"], pos)
        me.set_value(entry, value)
    else:
        
        entry = me.new_map_entry(key, value)
        al.change_info(my_map["table"], pos, entry)
        my_map["size"] += 1
        my_map["current_factor"] = my_map["size"] / my_map["capacity"]
        if my_map["current_factor"] > my_map["limit_factor"]:
            my_map = rehash(my_map)

    return my_map


def size(my_map):
    """Retorna el tamaño del mapa."""
    return my_map["size"]

def remove(my_map, key):
    """Elimina una pareja llave-valor."""
    key_hash = hash_value(my_map, key)
    ocupied, pos = find_slot(my_map, key, key_hash)
    if ocupied:
        tabla = my_map["table"]
        entry = al.get_element(tabla, pos)
        me.set_key(entry, "__EMPTY__")
        me.set_value(entry, None)
        my_map["size"] -= 1
        my_map["current_factor"] = my_map["size"] / my_map["capacity"]
    return my_map

def is_empty(my_map):
    return my_map["size"] == 0

def key_set(my_map):
    keys = al.new_list()
    for i in range(my_map["capacity"]):
        entry = al.get_element(my_map["table"], i)
        key = me.get_key(entry)
        if key is not None and key != "__EMPTY__":
            al.add_last(keys, key)
    return keys

def value_set(my_map):
    values = al.new_list()
    for i in range(my_map["capacity"]):
        entry = al.get_element(my_map["table"], i)
        key = me.get_key(entry)
        if key is not None and key != "__EMPTY__":
            value = me.get_value(entry)
            al.add_last(values, me.get_value(entry))
    return values