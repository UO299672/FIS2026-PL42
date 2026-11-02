from cancelacion.cancelacionModel import cancelacionModel

class cancelacionView:
    def __init__(self):
        self.model = cancelacionModel()

    def ejecutar(self):
        print("\n==========================================")
        print("      CANCELACIÓN DE INSCRIPCIÓN          ")
        print("==========================================")
        
        identificador = input("Ingrese DNI/NIE o Número de socio: ").strip()
        if not identificador:
            print("❌ Debe introducir un identificador válido.")
            return

        persona = self.model.buscar_persona_por_identificador(identificador)
        if not persona:
            print("❌ No se encontró ninguna persona con ese identificador.")
            return

        print(f"\nUsuario: {persona['nombre']} ({persona['tipo'].capitalize()})")

        inscripciones = self.model.obtener_inscripciones_cancelables(persona['id_persona'])
        if not inscripciones:
            print("ℹ️ No tiene inscripciones activas ('confirmada' o 'en espera') para cancelar.")
            return

        print("\nInscripciones activas disponibles para cancelar:")
        print("-" * 65)
        for idx, ins in enumerate(inscripciones, start=1):
            nivel_str = f" ({ins['nivel']})" if ins['nivel'] else ""
            instalacion_str = f" en {ins['instalacion']}" if ins['instalacion'] else ""
            print(f"[{idx}] {ins['actividad']}{nivel_str}{instalacion_str}")
            print(f"    Horario: Día {ins['dia_actividad']} ({ins['hora_inicio']} - {ins['hora_fin']}) | Estado: {ins['estado'].upper()}")
            print("-" * 65)

        opcion = input("\nSeleccione el número de la inscripción a cancelar (0 para salir): ").strip()
        if not opcion.isdigit() or int(opcion) < 0 or int(opcion) > len(inscripciones):
            print("❌ Opción no válida.")
            return

        idx_sel = int(opcion)
        if idx_sel == 0:
            print("Operación cancelada por el usuario.")
            return

        ins_seleccionada = inscripciones[idx_sel - 1]
        id_inscripcion = ins_seleccionada['id_inscripcion']

        confirmacion = input(f"¿Está seguro de que desea cancelar la inscripción a '{ins_seleccionada['actividad']}'? (s/n): ").strip().lower()
        if confirmacion != 's':
            print("Operación abortada.")
            return

        resultado = self.model.cancelar_inscripcion(id_inscripcion)
        if resultado.get("exito"):
            resumen = self.model.obtener_resumen_cancelacion(id_inscripcion)
            print("\n==========================================")
            print("      JUSTIFICANTE DE CANCELACIÓN         ")
            print("==========================================")
            print(f"ID Inscripción : {resumen['id_inscripcion']}")
            print(f"Usuario        : {resumen['persona']} ({resumen['dni_nie']})")
            print(f"Actividad      : {resumen['actividad']}")
            print(f"Estado Final   : {resumen['estado'].upper()}")
            print("==========================================")
            print("✅ La inscripción ha sido cancelada correctamente.")
            if resultado.get("promocionado"):
                print("ℹ️ Se ha promocionado automáticamente al primer usuario en lista de espera.")
        else:
            print("❌ Ocurrió un error al intentar cancelar la inscripción.")