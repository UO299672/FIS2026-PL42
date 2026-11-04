from tabulate import tabulate
from util.unexpectedException import UnexpectedException
from util.validation import ValidationError
from .periodosModel import (periodosModel, parsear_fecha, formatear_fecha, comprobar_antes_de_primera_sesion,
                            comprobar_cierre_tras_apertura, comprobar_no_socios_tras_socios)


def formatear_periodo(apertura, cierre):
    return f"{formatear_fecha(apertura)} - {formatear_fecha(cierre)}"


class periodosView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = periodosModel(db_name)

    def run(self):
        try:
            self.definir_periodos()
        except UnexpectedException:
            print("Error de acceso a la base de datos. Intentelo de nuevo.\n")

    def pedir_fecha(self, texto: str, campo: str, comprobar=None):
        """
        Pide una fecha dd/mm/aaaa hasta que sea válida y cumpla la comprobación indicada.
        Devuelve None si el responsable cancela.
        """
        while True:
            valor = input(f"{texto} (dd/mm/aaaa, 'c' para cancelar): ").strip()
            if valor.lower() == 'c' or not valor:
                return None
            try:
                fecha = parsear_fecha(valor, campo)
                if comprobar:
                    comprobar(fecha)
                return fecha
            except ValidationError as e:
                print(f"  {e} Introduzcala de nuevo.")

    def definir_periodos(self):
        print("\n==========================================")
        print("   DEFINIR PERIODOS DE INSCRIPCION")
        print("==========================================")

        ofertas = self.model.listar_ofertas()
        if not ofertas:
            print(" No hay ofertas registradas.")
            return

        tabla = [{
            "id": o["id_oferta"],
            "anio": o["anio"],
            "actividades": o["actividades"],
            "socios": formatear_periodo(o["apertura_socios"], o["cierre_socios"]),
            "no socios": formatear_periodo(o["apertura_no_socios"], o["cierre_no_socios"]),
        } for o in ofertas]
        print("\nOfertas:")
        print(tabulate(tabla, headers="keys", tablefmt="grid"))

        id_oferta_str = input("\nIntroduzca el ID de la oferta ('c' para cancelar): ").strip()
        if id_oferta_str.lower() == 'c' or not id_oferta_str:
            print("Operacion cancelada.")
            return
        if not id_oferta_str.isdigit():
            print(" El ID de la oferta debe ser un numero entero.")
            return

        oferta = self.model.obtener_oferta(int(id_oferta_str))
        if not oferta:
            print(" No existe ninguna oferta con ese ID.")
            return

        primera_sesion = self.pedir_fecha("\nFecha de la primera sesion de las actividades", "primera sesion")
        if primera_sesion is None:
            print("Operacion cancelada.")
            return

        print("\nPeriodo de inscripcion para socios")
        apertura_socios = self.pedir_fecha(
            "  Fecha de apertura", "apertura de socios",
            lambda f: comprobar_antes_de_primera_sesion(f, primera_sesion, "apertura de socios"))
        if apertura_socios is None:
            print("Operacion cancelada.")
            return
        cierre_socios = self.pedir_fecha(
            "  Fecha de cierre", "cierre de socios",
            lambda f: (comprobar_cierre_tras_apertura(apertura_socios, f, "socios"),
                       comprobar_antes_de_primera_sesion(f, primera_sesion, "cierre de socios")))
        if cierre_socios is None:
            print("Operacion cancelada.")
            return

        print("\nPeriodo de inscripcion para no socios")
        apertura_no_socios = self.pedir_fecha(
            "  Fecha de apertura", "apertura de no socios",
            lambda f: (comprobar_no_socios_tras_socios(apertura_socios, f),
                       comprobar_antes_de_primera_sesion(f, primera_sesion, "apertura de no socios")))
        if apertura_no_socios is None:
            print("Operacion cancelada.")
            return
        cierre_no_socios = self.pedir_fecha(
            "  Fecha de cierre", "cierre de no socios",
            lambda f: (comprobar_cierre_tras_apertura(apertura_no_socios, f, "no socios"),
                       comprobar_antes_de_primera_sesion(f, primera_sesion, "cierre de no socios")))
        if cierre_no_socios is None:
            print("Operacion cancelada.")
            return

        try:
            self.model.guardar_periodos(oferta["id_oferta"], apertura_socios, cierre_socios,
                                        apertura_no_socios, cierre_no_socios, primera_sesion)
        except ValidationError as e:
            print(f"\n Las fechas no son validas: {e}")
            print(" No se han guardado los datos.")
            return

        guardada = self.model.obtener_oferta(oferta["id_oferta"])
        print("\n==================================================")
        print("        PERIODOS DE INSCRIPCION REGISTRADOS       ")
        print("==================================================")
        print(f" Oferta         : {guardada['anio']}")
        print(f" Primera sesion : {primera_sesion.strftime('%d/%m/%Y')}")
        print(f" Socios         : {formatear_periodo(guardada['apertura_socios'], guardada['cierre_socios'])}")
        print(f" No socios      : {formatear_periodo(guardada['apertura_no_socios'], guardada['cierre_no_socios'])}")
        print("==================================================\n")
