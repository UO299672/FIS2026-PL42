import os
import sys

# Asegurar que el directorio 'src' esté en el path de Python
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.database import Database
from inscripcion.inscripcionView import inscripcionView

ROOT_DIR = os.path.dirname(SRC_DIR)
DB_PATH = os.path.join(ROOT_DIR, "CompanyDB.db")
SCHEMA_PATH = os.path.join(ROOT_DIR, "resources", "schema.sql")
DATA_PATH = os.path.join(ROOT_DIR, "resources", "data.sql")


def initialize_database():
    db = Database(DB_PATH)
    db.executeScript(SCHEMA_PATH)
    db.executeScript(DATA_PATH)


def main():
    initialize_database()  # Initialize DB with schema and data on each run
        
    while True:    
        print("Panel de funcionalidades:")
        
        choice = input("Seleccione una opción: ").strip()
        


if __name__ == "__main__":
    main()
