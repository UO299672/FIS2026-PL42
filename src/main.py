import os
import sys

# Asegurar que el directorio 'src' esté en el path de Python
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from util.database import Database
from calendario.calendarioView import calendarioView
from inscripcion.inscripcionView import inscripcionView
from cancelacion.cancelacionView import cancelacionView
from view.actividadView import add_actividad
from periodos.periodosView import periodosView
from oferta.ofertaView import ofertaView
from consulta.consultaView import consultaView
from asignacion.asignacionView import asignacionView

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
        print("          CENTRO DEPORTIVO                ")
        print("==========================================")
        print("1. Inscribirse en una actividad")
        print("2. Cancelar una inscripción")
        print("3. Añadir una actividad")
        print("4. Calendario de instalaciones")
        print("5. Definir periodos de inscripción de una oferta")
        print("6. Consultar la oferta de actividades")
        print("7. Consultar actividades e inscripciones")
        print("8. Asignar una instalación a una actividad")
        print("0. Salir")

        choice = input("Seleccione una opción: ").strip()

        if choice == '1':
            try:
                inscripcionView().run()
            except Exception as e:
                print(f"Error en el módulo de inscripción: {e}")
        elif choice == '2':
            try:
                cancelacionView().ejecutar()
            except Exception as e:
                print(f"Error en el módulo de cancelación: {e}")
        elif choice == '3':
            try:
                add_actividad(Database(DB_PATH))
            except Exception as e:
                print(f"Error al añadir la actividad: {e}")
        elif choice == '4':
            try:
                calendarioView().run()
            except Exception as e:
                print(f"Error al mostrar el calendario: {e}")
        elif choice == '5':
            try:
                periodosView().run()
            except Exception as e:
                print(f"Error en el módulo de periodos de inscripción: {e}")
        elif choice == '6':
            try:
                ofertaView().ejecutar()
            except Exception as e:
                print(f"Error en la consulta de oferta: {e}")
        elif choice == '7':
            try:
                consultaView().run()
            except Exception as e:
                print(f"Error en el módulo de consulta: {e}")
        elif choice == '8':
            try:
                asignacionView().run()
            except Exception as e:
                print(f"Error en el módulo de asignación de instalaciones: {e}")
        elif choice == '0':
            print("Saliendo del programa...\n")
            break
        else:
            print("Opción inválida. Inténtelo de nuevo.\n")


if __name__ == "__main__":
    main()
