from datetime import datetime
from util.database import Database


class inscripcionModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def buscar_persona_por_identificador(self, identificador: str):
        """
        Busca a una persona por DNI/NIE o número de socio.
        """
        identificador = identificador.strip()
        
        if identificador.isdigit():
            query = "SELECT * FROM Persona WHERE numero_socio = ?"
            res = self.db.executeQuery(query, int(identificador))
            if res:
                return res[0]

        query = "SELECT * FROM Persona WHERE UPPER(dni_nie) = UPPER(?)"
        res = self.db.executeQuery(query, identificador)
        return res[0] if res else None

    def listar_actividades_disponibles(self, tipo_persona: str):
        """
        Lista las actividades cuya oferta corresponda según las fechas del tipo de persona.
        """
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        if tipo_persona.lower() == 'socio':
            query = """
                SELECT a.id_actividad, c.nombre AS categoria, a.nivel,
                       a.hora_inicio, a.hora_fin, a.dia_actividad, inst.nombre AS instalacion,
                       a.plazas,
                       (SELECT COUNT(*) FROM Inscripcion WHERE id_actividad = a.id_actividad AND estado = 'confirmada') AS plazas_ocupadas
                FROM Actividad a
                JOIN Categoria c ON a.id_categoria = c.id_categoria
                LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
                JOIN Oferta o ON a.id_oferta = o.id_oferta
                WHERE ? BETWEEN o.apertura_socios AND o.cierre_socios
            """
        else:
            query = """
                SELECT a.id_actividad, c.nombre AS categoria, a.nivel,
                       a.hora_inicio, a.hora_fin, a.dia_actividad, inst.nombre AS instalacion,
                       a.plazas,
                       (SELECT COUNT(*) FROM Inscripcion WHERE id_actividad = a.id_actividad AND estado = 'confirmada') AS plazas_ocupadas
                FROM Actividad a
                JOIN Categoria c ON a.id_categoria = c.id_categoria
                LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
                JOIN Oferta o ON a.id_oferta = o.id_oferta
                WHERE ? BETWEEN o.apertura_no_socios AND o.cierre_no_socios
            """
        return self.db.executeQuery(query, fecha_actual)

    def obtener_inscripcion_activa(self, id_persona: int, id_actividad: int):
        """
        Comprueba si la persona ya tiene una inscripción activa (confirmada o en espera).
        """
        query = """
            SELECT * FROM Inscripcion 
            WHERE id_persona = ? AND id_actividad = ? AND estado <> 'cancelada'
        """
        res = self.db.executeQuery(query, id_persona, id_actividad)
        return res[0] if res else None

    def calcular_plazas_libres(self, id_actividad: int):
        """
        Devuelve las plazas libres en una actividad.
        """
        query_total = "SELECT plazas FROM Actividad WHERE id_actividad = ?"
        res_total = self.db.executeQuery(query_total, id_actividad)
        if not res_total:
            return 0
        
        plazas_totales = res_total[0]["plazas"]
        
        query_confirmadas = """
            SELECT COUNT(*) AS total 
            FROM Inscripcion 
            WHERE id_actividad = ? AND estado = 'confirmada'
        """
        confirmadas = self.db.executeQuery(query_confirmadas, id_actividad)[0]["total"]
        
        return plazas_totales - confirmadas

    
    def realizar_inscripcion(self, id_persona: int, id_actividad: int, estado: str):
        """
        Inserta la inscripción y recupera de forma infalible el ID real generado 
        evitando que devuelva 0 o None.
        """
        query = """
            INSERT INTO Inscripcion (id_persona, id_actividad, estado, fecha_solicitud)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        """
        self.db.executeUpdateQuery(query, id_persona, id_actividad, estado)
        
        # Búsqueda directa del último ID real insertado para esta persona y actividad
        query_id = """
            SELECT id_inscripcion 
            FROM Inscripcion 
            WHERE id_persona = ? AND id_actividad = ? 
            ORDER BY id_inscripcion DESC 
            LIMIT 1
        """
        res = self.db.executeQuery(query_id, id_persona, id_actividad)
        if res and len(res) > 0:
            row = res[0]
            # Extrae el valor sin importar si viene como diccionario o tupla
            return row['id_inscripcion'] if isinstance(row, dict) else row[0]
            
        return None

    def obtener_resumen_inscripcion(self, id_inscripcion: int):
        """
        Devuelve los detalles completos de la inscripción para el justificante.
        """
        query = """
            SELECT 
                i.id_inscripcion, 
                p.dni_nie, 
                p.nombre AS nombre, 
                p.tipo AS tipo,
                c.nombre AS actividad, 
                a.nivel,
                inst.nombre AS instalacion,
                a.hora_inicio, 
                a.hora_fin, 
                i.estado, 
                i.fecha_solicitud
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Actividad a ON i.id_actividad = a.id_actividad
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
            WHERE i.id_inscripcion = ?
        """
        res = self.db.executeQuery(query, id_inscripcion)
        return res[0] if res else None