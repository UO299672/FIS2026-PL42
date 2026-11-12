from tabulate import tabulate

from util.unexpectedException import UnexpectedException
from util.validation import DIAS_SEMANA
from .demandaModel import demandaModel


class demandaView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = demandaModel(db_name)

    def run(self):
        try:
            self.consultar_demanda()
        except UnexpectedException:
            print("Error de acceso a la base de datos. Inténtelo de nuevo.\n")

    def consultar_demanda(self):
        print("\n==========================================")
        print("   DEMANDA POR DÍA Y FRANJA HORARIA")
        print("==========================================")

        ofertas = self.model.listar_ofertas()
        if not ofertas:
            print("No hay ofertas registradas.\n")
            return

        print("\nOfertas:")
        print(tabulate([[o["id_oferta"], o["anio"], o["actividades"]] for o in ofertas],
                       headers=["ID", "Año", "Actividades"], tablefmt="grid"))

        valor = input("\nIntroduzca el ID de la oferta ('c' para cancelar): ").strip()
        if valor.lower() == 'c' or not valor:
            print("Operación cancelada.\n")
            return
        if not valor.isdigit():
            print("El ID de la oferta debe ser un número entero.\n")
            return
        oferta = self.model.obtener_oferta(int(valor))
        if not oferta:
            print("No existe ninguna oferta con ese ID.\n")
            return

        categorias = self.model.listar_categorias()
        print("\nCategorías disponibles (opcional):")
        print("[0] Todas las categorías")
        for c in categorias:
            print(f"[{c['id_categoria']}] {c['nombre']}")
        valor = input("Seleccione una categoría (0 o Enter = todas, 'c' para cancelar): ").strip()
        if valor.lower() == 'c':
            print("Operación cancelada.\n")
            return
        id_categoria = None
        nombre_categoria = "Todas"
        if valor and valor != "0":
            categoria = next((c for c in categorias if str(c["id_categoria"]) == valor), None)
            if categoria is None:
                print("La categoría indicada no existe.\n")
                return
            id_categoria = categoria["id_categoria"]
            nombre_categoria = categoria["nombre"]

        demanda = self.model.consultar_demanda(oferta["id_oferta"], id_categoria)
        if not demanda:
            print(f"\nLa oferta {oferta['anio']} no tiene actividades programadas.\n")
            return
        self._mostrar_demanda(oferta["anio"], nombre_categoria, demanda)

    def _mostrar_demanda(self, anio, categoria, demanda):
        print(f"\n=== Demanda de la oferta {anio} - Categoría: {categoria} ===")
        print("Demanda = inscripciones confirmadas + en espera. "
              "Relación = demanda / plazas ofertadas.")

        for dia, franjas in demanda.items():
            print(f"\n{DIAS_SEMANA[dia - 1]}")
            if all(f["sin_oferta"] for f in franjas):
                print("  Sin oferta")
                continue
            filas = [self._fila(f) for f in franjas]
            print(tabulate(filas, headers=["Franja", "Demanda", "Plazas", "Relación", "Observaciones"],
                           tablefmt="grid"))

    @staticmethod
    def _fila(franja):
        if franja["sin_oferta"]:
            return [franja["franja"], "-", "-", "-", "SIN OFERTA"]
        relacion = f"{franja['relacion']:.0%}" if franja["relacion"] is not None else "-"
        observacion = {"mas": "MÁS DEMANDA", "menos": "MENOS DEMANDA"}.get(franja["destacada"], "")
        return [franja["franja"], franja["demanda"], franja["plazas"], relacion, observacion]
