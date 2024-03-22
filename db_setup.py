"""Configuración de la base de datos"""

import sqlite3 

try: #captura si hay un error
    print("Database Connection") #conexión a la base de datos
    db = sqlite3.connect("inventory.db") #

    print("Create Cursor")
    # cursor = conn.cursor()

    print("Create Table")
    db.execute("DROP TABLE IF EXISTS part_inventory_app") #borra la tabla si existe part_inventory_app, para empezar en ceros
    db.execute(
        "CREATE TABLE part_inventory_app (part_no VARCHAR PRIMARY KEY, quant INTEGER)"
    ) #crea la tabla part_inventory_app con dos columnas, part_no (clave primaria, única) y quant (cantindad, un entero)

    print("Insert Data") #inserta datos en la tabla
    data = [
        ("a42CLDR", 18194),
        ("b42CLDR", 18362),
        ("c42CLDR", 12362),
        ("d42CLDR", 128),
        ("e42CLDR", 1228),
    ] #Crea un lista de tuplas, cada tupla va a ser un registro en la tabla
    db.executemany("INSERT INTO part_inventory_app VALUES (?,?)", data) #que se ejecute muchas veces, hace un ciclo for reemplaza los ? por los valores de la tupla
    db.commit() #guarda los cambios en la base de datos en el disco

    print("Close Connection")
    db.close()

except Exception as e: 
    print(f"\tERROR: {str(e)}", flush=True) #si hay un error, imprime el error