from util.database import Database

class cancelacionModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def buscar_persona_por_identificador(self, identificador: str):
        """Busca a una persona por número de socio (si es numérico) o por DNI/NIE."""
        identificador = identificador.strip()
        if identificador.isdigit():
            query = "SELECT * FROM Persona WHERE numero_socio = ?"
            res = self.db.executeQuery(query, int(identificador))
        else:
            query = "SELECT * FROM Persona WHERE UPPER(dni_nie) = UPPER(?)"
            res = self.db.executeQuery(query, identificador)
        return res[0] if res else None

    def obtener_inscripciones_cancelables(self, id_persona: int):
        """Devuelve las inscripciones activas ('confirmada' o 'en espera') del usuario."""
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
                i.fecha_solicitud
            FROM Inscripcion i
            JOIN Actividad a ON i.id_actividad = a.id_actividad
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
            WHERE i.id_persona = ? AND LOWER(i.estado) IN ('confirmada', 'en espera')
            ORDER BY i.fecha_solicitud DESC
        """
        return self.db.executeQuery(query, id_persona)

    def cancelar_inscripcion(self, id_inscripcion: int):
        """
        Cambia el estado de la inscripción a 'cancelada'.
        Si estaba 'confirmada', promociona automáticamente al primer usuario en 'en espera'.
        """
        # 1. Obtener estado e id_actividad de la inscripción a cancelar
        query_sel = "SELECT id_actividad, estado FROM Inscripcion WHERE id_inscripcion = ?"
        res_sel = self.db.executeQuery(query_sel, id_inscripcion)
        if not res_sel:
            return {"exito": False}

        id_actividad = res_sel[0]["id_actividad"]
        estado_anterior = res_sel[0]["estado"].lower()

        # 2. Actualizar estado a 'cancelada'
        query_update = "UPDATE Inscripcion SET estado = 'cancelada' WHERE id_inscripcion = ?"
        self.db.executeUpdateQuery(query_update, id_inscripcion)

        promocionado = False
        # 3. Si estaba confirmada, promocionar a la primera persona en lista de espera
        if estado_anterior == 'confirmada':
            query_espera = """
                SELECT id_inscripcion 
                FROM Inscripcion 
                WHERE id_actividad = ? AND LOWER(estado) = 'en espera' 
                ORDER BY fecha_solicitud ASC, id_inscripcion ASC 
                LIMIT 1
            """
            res_espera = self.db.executeQuery(query_espera, id_actividad)
            if res_espera:
                id_promovido = res_espera[0]["id_inscripcion"]
                query_promocionar = "UPDATE Inscripcion SET estado = 'confirmada' WHERE id_inscripcion = ?"
                self.db.executeUpdateQuery(query_promocionar, id_promovido)
                promocionado = True

        return {"exito": True, "promocionado": promocionado, "estado_anterior": estado_anterior}

    def obtener_resumen_cancelacion(self, id_inscripcion: int):
        """Devuelve los datos necesarios para generar el justificante de cancelación."""
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