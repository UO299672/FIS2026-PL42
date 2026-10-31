from tabulate import tabulate
from util.unexpectedException import UnexpectedException
from .inscripcionModel import inscripcionModel


class inscripcionView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = inscripcionModel(db_name)

    def run(self):
        try:
            self.inscribir_usuario()
        except UnexpectedException:
            print("Error de acceso a la base de datos. Intentelo de nuevo.\n")

    def inscribir_usuario(self):
        print("\n==========================================")
        print("   PROCESO DE INSCRIPCION A ACTIVIDAD (HU-06)")
        print("==========================================")
        
        identificador = input("Introduzca DNI/NIE o numero de socio ('c' para cancelar): ").strip()
        
        if identificador.lower() == 'c' or not identificador:
            print("Operacion cancelada.")
            return

        persona = self.model.buscar_persona_por_identificador(identificador)
        if not persona:
            print(" No se ha encontrado a ninguna persona con esa identificacion.")
            return

        print(f"\nBienvenido/a, {persona['nombre']} (Tipo: {persona['tipo']})")

        actividades = self.model.listar_actividades_disponibles(persona['tipo'])
        if not actividades:
            print(" Actualmente no hay ninguna actividad con periodo de inscripcion abierto para su tipo de usuario.")
            return

        print("\nActividades disponibles:")
        print(tabulate(actividades, headers="keys", tablefmt="grid"))

        id_act_str = input("\nIntroduzca el ID de la actividad en la que desea inscribirse ('c' para cancelar): ").strip()
        if id_act_str.lower() == 'c' or not id_act_str:
            print("Operacion cancelada.")
            return

        if not id_act_str.isdigit():
            print(" El ID de la actividad debe ser un numero entero.")
            return

        id_actividad = int(id_act_str)
        
        act_seleccionada = next((a for a in actividades if a['id_actividad'] == id_actividad), None)
        if not act_seleccionada:
            print(" El ID seleccionado no corresponde a ninguna actividad disponible actualmente.")
            return

        inscripcion_previa = self.model.obtener_inscripcion_activa(persona['id_persona'], id_actividad)
        if inscripcion_previa:
            print(f" Ya cuenta con una inscripcion activa en esta actividad (Estado actual: {inscripcion_previa['estado']}).")
            return

        plazas_libres = self.model.calcular_plazas_libres(id_actividad)
        
        if plazas_libres > 0:
            estado_final = "confirmada"
            print(f"\n Se han encontrado plazas disponibles ({plazas_libres} libres). Confirmando inscripcion...")
        else:
            print("\n La actividad seleccionada no tiene plazas libres.")
            respuesta = input("¿Desea apuntarse a la lista de espera? (S/N): ").strip().upper()
            if respuesta != 'S':
                print("Operacion cancelada.")
                return
            estado_final = "en espera"


        id_inscripcion = self.model.realizar_inscripcion(persona['id_persona'], id_actividad, estado_final)
        print(f"DEBUG - ID de inscripción devuelto: {id_inscripcion}") # <-- Mira qué sale aquí por consola

        resumen = self.model.obtener_resumen_inscripcion(id_inscripcion)
        if not resumen:
            print(f"Error: La consulta de resumen devolvió None para el ID: {id_inscripcion}")
            return


        #id_inscripcion = self.model.realizar_inscripcion(persona['id_persona'], id_actividad, estado_final)
        
        #resumen = self.model.obtener_resumen_inscripcion(id_inscripcion)
        print("\n==================================================")
        print("            JUSTIFICANTE DE INSCRIPCION           ")
        print("==================================================")
        print(f" ID Inscripcion : {resumen['id_inscripcion']}")
        print(f" Usuario        : {resumen['nombre']} (DNI: {resumen['dni_nie']})")
        print(f" Actividad      : {resumen['actividad']} - Nivel: {resumen['nivel'] or 'Sin nivel'}")
        print(f" Instalacion    : {resumen['instalacion'] or 'Sin asignar'}")
        print(f" Horario        : {resumen['hora_inicio']} a {resumen['hora_fin']}")
        print(f" Estado         : {resumen['estado']}")
        print(f" Fecha/Hora     : {resumen['fecha_solicitud']}")
        print("==================================================\n")