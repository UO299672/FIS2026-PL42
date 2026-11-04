from oferta.ofertaModel import ofertaModel

class ofertaView:
    def __init__(self):
        self.model = ofertaModel()

    def ejecutar(self):
        print("\n==========================================")
        print("     CONSULTA DE OFERTA DE ACTIVIDADES    ")
        print("==========================================")

        # 1. Identificación para saber los periodos aplicables
        identificador = input("Introduzca DNI/NIE o Nº Socio para mostrarle sus fechas ('c' para omitir): ").strip()
        tipo_persona = None
        
        if identificador.lower() != 'c' and identificador:
            persona = self.model.buscar_persona_por_identificador(identificador)
            if persona:
                tipo_persona = persona['tipo']
                print(f"Bienvenido/a, {persona['nombre']} (Tipo: {tipo_persona})")
            else:
                print("⚠️ Identificador no encontrado. Se mostrarán las fechas generales.")

        # 2. Filtros obligatorios combinables
        print("\n--- FILTROS DE BÚSQUEDA ---")
        print("Debe aplicar obligatoriamente al menos un filtro.")

        # Categoría
        categorias = self.model.obtener_categorias()
        print("\nCategorías disponibles:")
        for c in categorias:
            print(f"[{c['id_categoria']}] {c['nombre']}")
        cat_input = input("Seleccione ID de Categoría (intro para omitir): ").strip()
        categoria_id = int(cat_input) if cat_input.isdigit() else None

        # Nivel
        nivel = input("Seleccione Nivel (ej. Inicial, Intermedio, Avanzado - intro para omitir): ").strip()
        if not nivel:
            nivel = None

        # Día
        dia_input = input("Seleccione Día de la semana (1=Lunes ... 7=Domingo - intro para omitir): ").strip()
        dia = int(dia_input) if dia_input.isdigit() else None

        # Validación del filtro obligatorio
        if categoria_id is None and nivel is None and dia is None:
            print("\n❌ Error: Es obligatorio seleccionar al menos un filtro para realizar la consulta.")
            return

        # 3. Búsqueda y renderizado
        actividades = self.model.buscar_actividades_filtradas(categoria_id, nivel, dia)

        if not actividades:
            print("\nℹ️ No se han encontrado actividades que coincidan con los criterios seleccionados.")
            return

        # Filtrar por defecto las abiertas HOY
        actividades_abiertas = [a for a in actividades if a['abierta_hoy']]
        
        if not actividades_abiertas:
            print("\nℹ️ No hay actividades abiertas en la fecha actual para los filtros seleccionados.")
            return

        # Preparar tabla para mostrar
        tabla = []
        for act in actividades_abiertas:
            # Fechas aplicables según tipo de persona
            if tipo_persona == 'socio':
                periodo = f"{act['apertura_socios']} al {act['cierre_socios']}"
            elif tipo_persona == 'no socio':
                periodo = f"{act['apertura_no_socios']} al {act['cierre_no_socios']}"
            else:
                periodo = f"Soc: {act['apertura_socios']} al {act['cierre_socios']} | No soc: {act['apertura_no_socios']} al {act['cierre_no_socios']}"

            # Etiqueta de plazas
            if act['plazas_libres'] <= 0:
                estado_plazas = "Completa (Existe lista de espera)"
            else:
                estado_plazas = str(act['plazas_libres'])

            tabla.append([
                act['categoria'],
                act['nivel'] or '-',
                str(act['dia_actividad']),
                f"{act['hora_inicio']} - {act['hora_fin']}",
                act['instalacion'],
                periodo,
                estado_plazas
            ])

        # Imprimir resultados
        print("\n================================================================================================================")
        print("                                     OFERTA DE ACTIVIDADES DISPONIBLES                                          ")
        print("================================================================================================================")
        
        try:
            from tabulate import tabulate
            headers = ["Categoría", "Nivel", "Día", "Horario", "Instalación", "Periodo de Inscripción", "Plazas Libres"]
            print(tabulate(tabla, headers=headers, tablefmt="grid"))
        except ImportError:
            # Formato simple por si no está instalada la librería tabulate
            for fila in tabla:
                print(f"Cat: {fila[0]} | Nivel: {fila[1]} | Día: {fila[2]} | {fila[3]} | Inst: {fila[4]} | Plazas: {fila[6]}\n  -> Periodo: {fila[5]}\n" + "-"*80)