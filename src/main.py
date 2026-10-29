from src.util.database import Database
from src.view.actividadView import add_actividad


def initialize_database(db_name="CompanyDB.db", schema_path="resources/schema.sql", data_path="resources/data.sql"):
    db = Database(db_name)
    db.executeScript(schema_path)  # Load schema
    db.executeScript(data_path)    # Load initial data
    return db

def main():
    db = initialize_database()  # Initialize DB with schema and data on each run

    while True:
        print("Panel de funcionalidades:")
        print("  1. Añadir actividad a la oferta actual")
        print("  0. Salir")

        choice = input("Seleccione una opción: ").strip()
        if choice == "1":
            add_actividad(db)
        elif choice == "0":
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
