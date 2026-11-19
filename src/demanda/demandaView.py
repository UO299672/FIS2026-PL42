from tabulate import tabulate
from demanda.demandaModel import demandaModel
from util.unexpectedException import UnexpectedException
from util.validation import DIAS_SEMANA, ValidationError, validate_option


class demandaView:
    def __init__(self, db_path="CompanyDB.db"):
        self.model = demandaModel(db_path)

    def run(self):
        try:
            self.consultar_demanda()
        except UnexpectedException as e:
            print(f"Error de acceso a la base de datos: {e}\n")

    def consultar_demanda(self):
        print("\n==========================================")
        print("    ANÁLISIS DE DEMANDA DE ACTIVIDADES    ")
        print("==========================================")

        # 1. Selección de una única oferta (actual o pasada/histórica)
        ofertas = self.model.obtener_ofertas_disponibles()
        if not ofertas:
            print("No hay ofertas actuales ni pasadas disponibles para consultar.")
            return

        print("\nOfertas (temporadas) disponibles:")
        opciones_ofertas = []
        for idx, oferta in enumerate(ofertas, start=1):
            fechas = (
                f"Socios: {oferta['apertura_socios']} a {oferta['cierre_socios']}"
                if oferta["apertura_socios"] and oferta["cierre_socios"]
                else "Histórica / Sin fechas definidas"
            )
            etiqueta = f"Temporada {oferta['anio']} ({oferta['tipo_temporada']}) - {fechas}"
            opciones_ofertas.append(etiqueta)
            print(f"  [{idx}] {etiqueta}")

        while True:
            sel_oferta = input("\nSeleccione una oferta ('c' para cancelar): ").strip()
            if sel_oferta.lower() == "c":
                print("Operación cancelada.")
                return
            try:
                validate_option(sel_oferta, opciones_ofertas)
                oferta_elegida = ofertas[int(sel_oferta) - 1]
                break
            except ValidationError as e:
                print(f"Error: {e}")

        # 2. Filtro opcional por categoría
        categorias = self.model.obtener_categorias()
        id_categoria = None
        nombre_categoria_filtro = "Todas"

        if categorias:
            print("\nFiltrar por categoría (Intro para ver todas):")
            opciones_categorias = [cat["nombre"] for cat in categorias]
            for idx, cat in enumerate(categorias, start=1):
                print(f"  [{idx}] {cat['nombre']}")

            while True:
                sel_cat = input("Seleccione categoría (Intro para todas, 'c' para cancelar): ").strip()
                if sel_cat.lower() == "c":
                    print("Operación cancelada.")
                    return
                if not sel_cat:
                    break
                try:
                    validate_option(sel_cat, opciones_categorias)
                    cat_elegida = categorias[int(sel_cat) - 1]
                    id_categoria = cat_elegida["id_categoria"]
                    nombre_categoria_filtro = cat_elegida["nombre"]
                    break
                except ValidationError as e:
                    print(f"Error: {e}")

        # 3. Porcentaje mínimo configurable para baja demanda (por defecto 50 %)
        while True:
            pct_str = input(
                "\nPorcentaje mínimo para baja demanda [Intro = 50 %] ('c' para cancelar): "
            ).strip()
            if pct_str.lower() == "c":
                print("Operación cancelada.")
                return
            if not pct_str:
                porcentaje_minimo = 50.0
                break
            try:
                porcentaje_minimo = float(pct_str.replace(",", "."))
                if not 0 <= porcentaje_minimo <= 100:
                    print("Error: El porcentaje debe estar entre 0 y 100.")
                    continue
                break
            except ValueError:
                print("Error: Debe introducir un valor numérico válido (ej: 50).")

        # 4. Obtener y mostrar tabla ordenada de mayor a menor demanda
        resultados = self.model.obtener_comparativa_demanda(
            id_oferta=oferta_elegida["id_oferta"],
            id_categoria=id_categoria,
            porcentaje_minimo=porcentaje_minimo,
        )

        print(
            f"\n--- COMPARATIVA DE DEMANDA | Temporada {oferta_elegida['anio']} "
            f"| Categoría: {nombre_categoria_filtro} | Umbral baja demanda: < {porcentaje_minimo:.1f}% ---"
        )

        if not resultados:
            print("No se encontraron actividades para la temporada y filtros seleccionados.")
            return

        tabla = []
        for act in resultados:
            dia_nombre = DIAS_SEMANA[act["dia_actividad"] - 1]
            nivel_txt = act["nivel"] if act["nivel"] else "Sin nivel"
            porcentaje_txt = (
                f"{act['porcentaje_demanda']:.2f} %"
                if act["porcentaje_demanda"] is not None
                else "N/A (0 plazas)"
            )

            if act["clasificacion"] == "Alta demanda":
                estado_txt = "ALTA DEMANDA"
            elif act["clasificacion"] == "Baja demanda":
                estado_txt = "BAJA DEMANDA"
            else:
                estado_txt = "Normal"

            tabla.append(
                {
                    "ID": act["id_actividad"],
                    "Actividad": f"{act['categoria']} ({nivel_txt})",
                    "Horario": f"{dia_nombre} {act['hora_inicio']}-{act['hora_fin']}",
                    "Plazas": act["plazas_ofertadas"],
                    "Confirmadas": act["confirmadas"],
                    "En espera": act["en_espera"],
                    "Demanda total": act["demanda_total"],
                    "Demanda/Plazas": porcentaje_txt,
                    "Clasificación": estado_txt,
                }
            )

        print(tabulate(tabla, headers="keys", tablefmt="grid"))