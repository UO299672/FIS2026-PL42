from datetime import datetime
from util.database import Database
from lista_espera.lista_esperaModel import lista_esperaModel

class cancelacionModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def buscar_persona_por_identificador(self, identificador: str):
        identificador = identificador.strip()
        if identificador.isdigit():
            query = "SELECT * FROM Persona WHERE numero_socio = ?"
            res = self.db.executeQuery(query, int(identificador))
        else:
            query = "SELECT * FROM Persona WHERE UPPER(dni_nie) = UPPER(?)"
            res = self.db.executeQuery(query, identificador)
        return res[0] if res else None

    def obtener_inscripciones_cancelables(self, id_persona: int):
        query = """
            SELECT 
                i.id_inscripcion, 
                c.nombre AS actividad, 
                a.nivel, 
                inst.nombre AS instalacion, 
                a.hora_inicio, 
                a.hora_fin, 
                a.dia_actividad, 
                i.estado, 
                i.fecha_solicitud,
                o.cierre_socios,
                o.cierre_no_socios
            FROM Inscripcion i
            JOIN Actividad a ON i.id_actividad = a.id_actividad
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            JOIN Oferta o ON a.id_oferta = o.id_oferta
            LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
            WHERE i.id_persona = ? AND LOWER(i.estado) IN ('confirmada', 'en espera')
            ORDER BY i.fecha_solicitud DESC
        """
        return self.db.executeQuery(query, id_persona)

    def es_cancelable_por_fecha(self, fecha_cierre_str: str) -> bool:
        """
        Verifica si la fecha actual es anterior al día 15 del último mes
        del periodo de la oferta (fecha_cierre_str).
        """
        try:
            fecha_cierre = datetime.strptime(fecha_cierre_str, "%Y-%m-%d")
            # El día 15 del último mes de la actividad:
            limite = datetime(fecha_cierre.year, fecha_cierre.month, 15)
            return datetime.now() < limite
        except Exception:
            return True

    def cancelar_inscripcion(self, id_inscripcion: int):
        query_sel = "SELECT id_actividad, estado FROM Inscripcion WHERE id_inscripcion = ?"
        res_sel = self.db.executeQuery(query_sel, id_inscripcion)
        if not res_sel:
            return {"exito": False}

        id_actividad = res_sel[0]["id_actividad"]
        estado_anterior = res_sel[0]["estado"].lower()

        query_update = "UPDATE Inscripcion SET estado = 'cancelada' WHERE id_inscripcion = ?"
        self.db.executeUpdateQuery(query_update, id_inscripcion)

        promocionado = False
        if estado_anterior == 'confirmada':
            promocionado = lista_esperaModel(self.db.db_path).promocionar(id_actividad) is not None

        return {
            "exito": True, 
            "promocionado": promocionado, 
            "estado_anterior": estado_anterior,
            "fecha_cancelacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def obtener_resumen_cancelacion(self, id_inscripcion: int):
        query = """
            SELECT 
                i.id_inscripcion, 
                p.dni_nie, 
                p.nombre AS persona, 
                p.tipo,
                c.nombre AS actividad, 
                a.nivel, 
                inst.nombre AS instalacion, 
                a.hora_inicio, 
                a.hora_fin, 
                i.estado
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Actividad a ON i.id_actividad = a.id_actividad
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
            WHERE i.id_inscripcion = ?
        """
        res = self.db.executeQuery(query, id_inscripcion)
        return res[0] if res else None