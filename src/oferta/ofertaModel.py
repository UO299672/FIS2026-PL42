from datetime import datetime
from util.database import Database

class ofertaModel:
    def __init__(self, db_path="CompanyDB.db"):
        self.db = Database(db_path)

    def obtener_categorias(self):
        """Obtiene las categorías para mostrarlas en el menú de filtros."""
        query = "SELECT id_categoria, nombre FROM Categoria"
        return self.db.executeQuery(query)

    def buscar_persona_por_identificador(self, identificador: str):
        """Busca a la persona para saber si es socio o no socio (HU-11)."""
        identificador = identificador.strip()
        if identificador.isdigit():
            query = "SELECT * FROM Persona WHERE numero_socio = ?"
            res = self.db.executeQuery(query, int(identificador))
        else:
            query = "SELECT * FROM Persona WHERE UPPER(dni_nie) = UPPER(?)"
            res = self.db.executeQuery(query, identificador)
        return res[0] if res else None

    def buscar_actividades_filtradas(self, categoria_id=None, nivel=None, dia=None):
        """
        Aplica los filtros combinables y recupera las actividades con sus instalaciones
        y ofertas definidas. Calcula las plazas ocupadas en tiempo real.
        """
        query = """
            SELECT 
                a.id_actividad, 
                c.nombre AS categoria, 
                a.nivel, 
                a.dia_actividad, 
                a.hora_inicio, 
                a.hora_fin, 
                i.nombre AS instalacion, 
                o.apertura_socios, 
                o.cierre_socios, 
                o.apertura_no_socios, 
                o.cierre_no_socios,
                a.plazas AS plazas_totales,
                (SELECT COUNT(*) FROM Inscripcion ins WHERE ins.id_actividad = a.id_actividad AND ins.estado = 'confirmada') AS plazas_ocupadas
            FROM Actividad a
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            JOIN Instalacion i ON a.id_instalacion = i.id_instalacion
            JOIN Oferta o ON a.id_oferta = o.id_oferta
            WHERE a.id_instalacion IS NOT NULL 
              AND o.apertura_socios IS NOT NULL
        """
        params = []
        
        if categoria_id:
            query += " AND a.id_categoria = ?"
            params.append(categoria_id)
        if nivel:
            query += " AND UPPER(a.nivel) = UPPER(?)"
            params.append(nivel)
        if dia:
            query += " AND a.dia_actividad = ?"
            params.append(dia)
            
        resultados = self.db.executeQuery(query, *params)
        
        # Procesar plazas libres y estado para la vista
        actividades_procesadas = []
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        for row in resultados:
            act = dict(row)
            act["plazas_libres"] = act["plazas_totales"] - act["plazas_ocupadas"]
            
            # Comprobar si está abierta HOY (socios o no socios)
            abierta_socios = act["apertura_socios"] <= fecha_actual <= act["cierre_socios"] if act["apertura_socios"] and act["cierre_socios"] else False
            abierta_no_socios = act["apertura_no_socios"] <= fecha_actual <= act["cierre_no_socios"] if act["apertura_no_socios"] and act["cierre_no_socios"] else False
            
            act["abierta_hoy"] = abierta_socios or abierta_no_socios
            actividades_procesadas.append(act)
            
        return actividades_procesadas