import os

from tabulate import tabulate

from util.unexpectedException import UnexpectedException
from util.validation import ValidationError
from .importacionModel import importacionModel, COLUMNAS, SEPARADOR


class importacionView:
    def __init__(self):
        self.model = importacionModel()

    def run(self):
        try:
            self.validar_csv()
        except UnexpectedException:
            print("Se ha producido un error inesperado. Inténtelo de nuevo.\n")

    def validar_csv(self):
        print("\n==========================================")
        print("   VALIDAR FICHERO CSV DE INSCRIPCIONES")
        print("==========================================")
        print(f"Formato: UTF-8, separador '{SEPARADOR}', una fila por inscripción.")
        print(f"Cabecera: {SEPARADOR.join(COLUMNAS)}")

        ruta = input("\nRuta del fichero CSV ('c' para cancelar): ").strip().strip('"').strip("'")
        if ruta.lower() == 'c' or not ruta:
            print("Operación cancelada.\n")
            return
        if not os.path.isfile(ruta):
            print("No se ha encontrado ningún fichero en esa ruta.\n")
            return

        try:
            filas, inconsistencias = self.model.validar_fichero(ruta)
        except (ValidationError, OSError) as e:
            print(f"No se ha podido leer el fichero: {e}\n")
            return

        self._mostrar_informe(os.path.basename(ruta), filas, inconsistencias)

    @staticmethod
    def _mostrar_informe(nombre, filas, inconsistencias):
        print(f"\n=== Informe de inconsistencias: {nombre} ===")
        print(f"Filas de datos leídas: {filas}")
        if not inconsistencias:
            print("El fichero no contiene inconsistencias.\n")
            return
        print(f"Inconsistencias encontradas: {len(inconsistencias)}")
        filas_tabla = [[i["linea"], i["columna"], i["motivo"]] for i in inconsistencias]
        print(tabulate(filas_tabla, headers=["Línea", "Columna", "Motivo"], tablefmt="grid"))
        print()
