"""Application to manage part inventory."""

import configparser
import json
import logging
import os
import sqlite3

from flask import Flask, g, redirect, render_template, request #g es un tipo diccionario que se usa para almacenar datos que se van a compartir entre las diferentes funciones de la aplicación

#
# Variable setup
#
app = Flask(__name__)
PARTLIST = []
MESSAGE = ""


#
# Logging setup
#
logging.basicConfig(
    filename="opdb-app.log", #archivo de texto que contiene todos los mensajes del programa
    format="%(asctime)s %(levelname)-8s [%(filename)-12s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S", #formato de la fecha
    level=logging.INFO, #nivel de los mensajes que se van a guardar en el archivo
)
log = logging.getLogger("inventory-app") #nombre del logger = inventory-app


#
# Database connection
#
def get_db(): #función que se conecta a la base de datos
    """Opens a new database connection if there is none yet for the current application context."""

    if "db" not in g: #si no hay una conexión a la base de datos

        try:
            log.info("Database Connection") #mensaje de información que nos estamos conectando a la base de datos
            g.db = sqlite3.connect("inventory.db") 
            g.db.row_factory = sqlite3.Row #objeto que se va a comportar como un diccionario

        except Exception as d: #d es la excepción
            raise Exception("Failed to connect to the database.") from d

    return g.db #si la base de datos existe en g, la devuelve, si no la busca en el disco


@app.teardown_appcontext #decorador que se ejecuta cuando la aplicación tenga un error
def teardown_db(exception):
    """Close database connection."""

    print(exception)
    db = g.pop("db", None)

    if db is not None: #
        db.close()
        log.info("Closed DB Connection")


#
# Inventory parts management
#
def getparts(): #función que se conecta a la base de datos y obtiene los datos de la tabla part_inventory_app
    """Retrieve current part inventory"""

    result = (
        get_db().execute("select part_no, quant from part_inventory_app").fetchall()
    )
    log.info("GETPARTS() - CURRENT PART INVENTORY:\n\t\t%s", result)
    return result


@app.route("/requestparts", methods=["POST"])
def requestparts():
    """Update part quantity for given part number."""

    global PARTLIST 
    global MESSAGE

    part_no = request.form["part_requested"] #obtiene el valor del campo part_requested del formulario, que es el número de parte que lo llena el usuario
    req_amt = request.form["amount_requested"]

    log.info("RECEIVED FORM DATA:\n\t\tPART = %s\n\t\tQUANTITY = %i", part_no, req_amt)

    if part_no and req_amt:

        req_amt = int(req_amt)
        db = get_db()

        result = db.execute(
            f"select quant from part_inventory_app where part_no = '{part_no}'"
        ).fetchone() #fetchone obtiene un solo registro de la base de datos

        log.info("REQUESTPARTS().results = %s", result)

        if result is not None:

            cur_val = result["QUANT"]
            print(f"cur_val = {cur_val}")

            if cur_val >= req_amt:
                new_amt = cur_val - req_amt
                print("new amount is " + str(new_amt))
                db.execute(
                    f'UPDATE part_inventory_app SET quant = {str(new_amt)} WHERE part_no = "{part_no}"'
                )
                db.commit()
                return redirect("/")
            else:
                MESSAGE = f"INSUFFICIENT QUANTITY FOR {part_no}: inventory = {cur_val}, requested {req_amt}"
                return render_template("index.html", partlist=PARTLIST, message=MESSAGE)
        else:
            MESSAGE = f"PART NOT FOUND: {part_no}"
            return render_template("index.html", partlist=PARTLIST, message=MESSAGE)
    else:
        MESSAGE = "INVALID PART NUMBER / QUANTITY"
        return render_template("index.html", partlist=PARTLIST, message=MESSAGE)


@app.route("/") #
def index():
    """Render index.html using parts from the database."""

    global PARTLIST #define cantidades
    global MESSAGE

    log.info("PAGE REFRESH")
    MESSAGE = ""
    PARTLIST = getparts()
    PARTLIST = [dict(row) for row in PARTLIST]
    return render_template("index.html", partlist=PARTLIST, message=MESSAGE)


if __name__ == "__main__":

    log.info("BEGIN PROGRAM")

    try:
        app.run(host="127.0.0.1", debug=True)
    except Exception as e:
        print(f"ERROR: unable to run application:\n {str(e)}")

    log.info("END PROGRAM")