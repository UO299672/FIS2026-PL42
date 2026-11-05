from tabulate import tabulate

from util.unexpectedException import UnexpectedException
from util.validation import ValidationError
from .asignacionModel import ConflictoInstalacionError, asignacionModel, describir_actividad, formatear_dias


class asignacionView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = asignacionModel(db_name)

    def run(self):
        try:
            self.asignar_instalacion()
        except UnexpectedException:
            print("Error de acceso a la base de datos. Intentelo de nuevo.\n")

    def pedir_id(self, texto: str):
        """Pide un ID numérico. Devuelve None si el responsable cancela."""
        while True:
            valor = input(f"{texto} ('c' para cancelar): ").strip()
            if valor.lower() == 'c' or not valor:
                return None
            if valor.isdigit():
                return int(valor)
            print("  El ID debe ser un numero entero.")

    def asignar_instalacion(self):
        print("\n==========================================")
        print("   ASIGNAR INSTALACION A UNA ACTIVIDAD")
        print("==========================================")

        actividades = self.model.listar_actividades()
        if not actividades:
            print(" No hay actividades registradas.")
            return
        print("\nActividades:")
        print(tabulate([{
            "id": a["id_actividad"],
            "oferta": a["anio"],
            "categoria": a["categoria"],
            "nivel": a["nivel"] or "-",
            "dias": formatear_dias(a["dia_actividad"]),
            "horario": f"{a['hora_inicio']} - {a['hora_fin']}",
            "instalacion": a["instalacion"] or "(sin asignar)",
        } for a in actividades], headers="keys", tablefmt="grid"))

        while True:
            id_actividad = self.pedir_id("\nIntroduzca el ID de la actividad")
            if id_actividad is None:
                print("Operacion cancelada.")
                return
            actividad = self.model.obtener_actividad(id_actividad)
            if actividad:
                break
            print("  No existe ninguna actividad con ese ID.")

        instalaciones = self.model.listar_instalaciones()
        if not instalaciones:
            print(" No hay instalaciones registradas.")
            return
        print(f"\nActividad seleccionada: {describir_actividad(actividad)}")
        if actividad["instalacion"]:
            print(f"Instalacion actual: {actividad['instalacion']}")
        print("\nInstalaciones:")
        print(tabulate([{"id": i["id_instalacion"], "nombre": i["nombre"]} for i in instalaciones],
                       headers="keys", tablefmt="grid"))

        while True:
            id_instalacion = self.pedir_id("\nIntroduzca el ID de la instalacion")
            if id_instalacion is None:
                print("Operacion cancelada.")
                return
            try:
                actividad = self.model.asignar_instalacion(id_actividad, id_instalacion)
                break
            except ConflictoInstalacionError as e:
                print(f"\n No se puede asignar la instalacion: {e}")
                print(" Elija otra instalacion.")
            except ValidationError as e:
                print(f"  {e}")

        print("\n==================================================")
        print("        INSTALACION ASIGNADA A LA ACTIVIDAD       ")
        print("==================================================")
        print(f" Id          : {actividad['id_actividad']}")
        print(f" Oferta      : {actividad['anio']}")
        print(f" Categoria   : {actividad['categoria']}")
        print(f" Nivel       : {actividad['nivel'] or '-'}")
        print(f" Dias        : {formatear_dias(actividad['dia_actividad'])}")
        print(f" Horario     : {actividad['hora_inicio']} - {actividad['hora_fin']}")
        print(f" Plazas      : {actividad['plazas']}")
        print(f" Instalacion : {actividad['instalacion']}")
        print("==================================================\n")
