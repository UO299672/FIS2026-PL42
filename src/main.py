import os
import sys

# Permite arrancar tanto con "python src/main.py" como con "python -m src.main".
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.database import DataBase
from calendario.calendarioView import calendarioView

DB_PATH = os.path.join(ROOT_DIR, "CompanyDB.db")
SCHEMA_PATH = os.path.join(ROOT_DIR, "resources", "schema.sql")
DATA_PATH = os.path.join(ROOT_DIR, "resources", "data.sql")


def initialize_database(db_name=DB_PATH, schema_path=SCHEMA_PATH, data_path=DATA_PATH):
    db = DataBase(db_name)
    db.executeScript(schema_path)  # Load schema
    db.executeScript(data_path)    # Load initial data


def main():
    initialize_database()  # Initialize DB with schema and data on each run

    while True:
        print("Panel de funcionalidades:")
        print("1. Calendario de ocupación de instalaciones")
        print("2. Salir")

        choice = input("Seleccione una opción: ").strip()

        if choice == '1':
            calendarioView(DB_PATH).run()
        elif choice == '2':
            print("Saliendo del panel de funcionalidades...\n")
            break
        else:
            print("Opción inválida.\n")


if __name__ == "__main__":
    main()
