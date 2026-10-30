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
    try:
        initialize_database()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

    while True:
        print("\n==========================================")
        print("     GESTIÓN DE INSCRIPCIONES (HU-06)     ")
        print("==========================================")
        print("1. Inscribirse en una actividad")
        print("2. Salir")

        choice = input("Seleccione una opción: ").strip()

        if choice == '1':
            try:
                vista = inscripcionView()
                vista.run()
            except Exception as e:
                print(f"Error en el módulo de inscripción: {e}")
        elif choice == '2':
            print("Saliendo del programa...\n")
            break
        else:
            print("Opción inválida. Inténtelo de nuevo.\n")


if __name__ == "__main__":
    main()