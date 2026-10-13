from DataStructures.List import array_list as al
from DataStructures.Map import map_entry as me
from DataStructures.Map import map_functions as mf
import random as rd

def new_map(num_elements,load_factor,prime=109345121):
    capacity = mf.next_prime(num_elements / load_factor)
    table = al.new_list()
    for i in range(capacity):
        al.add_last(table, al.new_list())
    return {
        'prime':prime,
        'capacity':capacity,
        'scale':rd.randint(1,prime-1),
        'shift':rd.randint(0,prime-1),
        'table':table,
        'current_factor':0,
        'limit_factor':load_factor,
        'size':0,
    }
    
def default_compare(key, entry)->int:
    """Función de comparación usando map_entry functions."""
    entry_key = me.get_key(entry)
    if key == entry_key:
        return 0
    elif key > entry_key:
        return 1
    return -1

def put(my_map, key, value):
    pos=mf.hash_value(my_map, key)
    bucket = al.get_element(my_map["table"], pos)
    for i in range(al.size(bucket)):
        entry = al.get_element(bucket, i)
        if default_compare(key, entry) == 0:
            me.set_value(entry, value)
            return my_map
    al.add_last(bucket, me.new_map_entry(key, value))
    my_map["size"] += 1
    my_map["current_factor"] = my_map["size"] / my_map["capacity"]
    if my_map["current_factor"] > my_map["limit_factor"]:
        my_map = rehash(my_map)
        return my_map
    
def get(my_map, key):
    pos=mf.hash_value(my_map, key)
    bucket = al.get_element(my_map["table"], pos)
    for i in range(al.size(bucket)):
        entry = al.get_element(bucket, i)
        if default_compare(key, entry) == 0:
            return me.get_value(entry)
    return None

def contains(my_map, key):
    pos=mf.hash_value(my_map, key)
    bucket = al.get_element(my_map["table"], pos)
    for i in range(al.size(bucket)):
        entry = al.get_element(bucket, i)
        if default_compare(key, entry) == 0:
            return True
    return False

def remove(my_map, key):
    pos=mf.hash_value(my_map, key)
    bucket = al.get_element(my_map["table"], pos)
    for i in range(al.size(bucket)):
        entry = al.get_element(bucket, i)
        if default_compare(key, entry) == 0:
            al.delete_element(bucket, i)
            my_map["size"] -= 1
            my_map["current_factor"] = my_map["size"] / my_map["capacity"]
            break
    return my_map   

def size(my_map):
    return my_map["size"]

def is_empty(my_map):
    return my_map["size"] == 0

def key_set(my_map):
    keys = al.new_list()
    for i in range(my_map["capacity"]):
        bucket = al.get_element(my_map["table"], i)
        for j in range(al.size(bucket)):
            entry = al.get_element(bucket, j)
            al.add_last(keys, me.get_key(entry))
    return keys

def value_set(my_map):
    values = al.new_list()
    for i in range(my_map["capacity"]):
        bucket= al.get_element(my_map["table"], i)
        for j in range(al.size(bucket)):
            entry = al.get_element(bucket, j)
            al.add_last(values, me.get_value(entry))
    return values

def rehash(my_map):
    new_capacity = mf.next_prime(my_map["capacity"] * 2)
    new_table = al.new_list()
    for i in range(new_capacity):
        al.add_last(new_table, al.new_list())
    old_table = my_map["table"]
    my_map["table"] = new_table
    my_map["capacity"] = new_capacity
    my_map["size"] = 0
    my_map["current_factor"] = 0.0
    for i in range(al.size(old_table)):
        bucket = al.get_element(old_table, i)
        for j in range(al.size(bucket)):
            entry = al.get_element(bucket, j)
            put(my_map, me.get_key(entry), me.get_value(entry))
    return my_map