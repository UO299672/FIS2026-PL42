from tabulate import tabulate

from util.unexpectedException import UnexpectedException
from .consultaModel import consultaModel, ESTADOS


class consultaView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = consultaModel(db_name)
        self.gestoropciones = {"1": self.consultar_actividad,
                               "2": self.consultar_persona,
                               "3": self.quit}

    def display_menu(self):
        print("""Consulta de actividades e inscripciones: \n
            1.- Consultar una actividad
            2.- Consultar las inscripciones de una persona
            3.- Salir
            """)

    def run(self):
        while True:
            self.display_menu()
            choice = input("Seleccione una opción: ").strip()
            accion = self.gestoropciones.get(choice)
            if accion:
                try:
                    resultado = accion()
                except UnexpectedException:
                    print("Se ha producido un error inesperado al acceder a los datos. "
                          "Inténtelo de nuevo más tarde.\n")
                    continue
                if resultado == 1:
                    break
            else:
                print("Opción inválida.\n")

    # ---------- Consulta de una actividad ----------

    def consultar_actividad(self):
        print("Indique al menos un criterio de búsqueda (Enter para omitirlo, 'c' para cancelar).")
        filtros = []
        for etiqueta, plural, opciones in (("Categoría", "Categorías", self.model.listar_categorias()),
                                           ("Nivel", "Niveles", self.model.listar_niveles()),
                                           ("Instalación", "Instalaciones", self.model.listar_instalaciones())):
            print(f"{plural} disponibles: {', '.join(opciones) or 'ninguna'}")
            texto = input(f"{etiqueta}: ").strip()
            if texto.lower() == 'c':
                return
            filtros.append(texto)
        if not any(filtros):
            print("Debe indicar al menos un criterio de búsqueda.\n")
            return

        actividades = self.model.buscar_actividades(*filtros)
        if not actividades:
            print("No se han encontrado actividades con esos criterios.\n")
            return
        for act in actividades:
            self._mostrar_actividad(act)

    def _mostrar_actividad(self, act):
        nivel = act["nivel"] or "Sin nivel"
        instalacion = act["instalacion"] or "Sin asignar"
        print(f"\n=== Actividad #{act['id_actividad']}: {act['categoria']} ({nivel}) - "
              f"{instalacion} - Oferta {act['anio']} ===")
        print(f"Horario: {self.model.nombre_dia(act['dia_actividad'])} "
              f"{act['hora_inicio']}-{act['hora_fin']}")
        print(f"Plazas: totales {act['plazas']} | ocupadas {act['plazas_ocupadas']} | "
              f"libres {act['plazas_libres']}")
        for etiqueta, apertura, cierre in (
                ("socios", act["apertura_socios"], act["cierre_socios"]),
                ("no socios", act["apertura_no_socios"], act["cierre_no_socios"])):
            estado = self.model.estado_periodo(apertura, cierre)
            fechas = f"{apertura} a {cierre} -> " if apertura and cierre else ""
            print(f"Periodo de inscripción {etiqueta}: {fechas}{estado.upper()}")

        inscritos = self.model.obtener_inscritos(act["id_actividad"])
        if not inscritos:
            print("Inscritos: no hay ninguna persona inscrita.")
            return
        print(f"Inscritos ({len(inscritos)}):")
        filas = [[i["nombre"], i["dni_nie"], i["fecha_solicitud"]] for i in inscritos]
        print(tabulate(filas, headers=["Nombre", "DNI/NIE", "Fecha de inscripción"], tablefmt="grid"))

    # ---------- Consulta de las inscripciones de una persona ----------

    def consultar_persona(self):
        texto = input("DNI/NIE o nombre de la persona ('c' para cancelar): ").strip()
        if texto.lower() == 'c':
            return
        if not texto:
            print("Debe introducir un DNI/NIE o un nombre.\n")
            return

        print("Filtrar por estado:")
        for n, estado in enumerate(ESTADOS, start=1):
            print(f"  {n}. {estado.capitalize()}")
        opcion = input("Seleccione un estado (Enter = todos): ").strip()
        estado = None
        if opcion:
            if not opcion.isdigit() or not 1 <= int(opcion) <= len(ESTADOS):
                print("Estado no válido.\n")
                return
            estado = ESTADOS[int(opcion) - 1]

        personas = self.model.buscar_personas(texto)
        if not personas:
            print("No se han encontrado personas con ese DNI/NIE o nombre.\n")
            return
        for persona in personas:
            self._mostrar_inscripciones(persona, estado)

    def _mostrar_inscripciones(self, persona, estado):
        print(f"\n=== {persona['nombre']} ({persona['dni_nie']}) - {persona['tipo'].capitalize()} ===")
        inscripciones = self.model.obtener_inscripciones(persona["id_persona"], estado)
        if not inscripciones:
            filtro = f" en estado '{estado}'" if estado else ""
            print(f"No se han encontrado inscripciones{filtro}.")
            return
        filas = []
        for ins in inscripciones:
            actividad = ins["actividad"] + (f" ({ins['nivel']})" if ins["nivel"] else "")
            horario = (f"{self.model.nombre_dia(ins['dia_actividad'])} "
                       f"{ins['hora_inicio']}-{ins['hora_fin']}")
            filas.append([actividad, ins["instalacion"] or "Sin asignar", horario,
                          ins["estado"].capitalize(), ins["fecha_solicitud"]])
        print(tabulate(filas, headers=["Actividad", "Instalación", "Horario", "Estado", "Fecha de solicitud"],
                       tablefmt="grid"))

    def quit(self):
        print("Cerrando opciones\n")
        return 1
