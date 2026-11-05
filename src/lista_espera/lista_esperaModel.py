from util.database import Database


class lista_esperaModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def tiene_horario_coincidente(self, id_persona: int, id_actividad: int,
                                  estados=("confirmada", "en espera")) -> bool:
        """True si la persona tiene, en otra actividad de la misma oferta, una inscripcion
        en alguno de los estados indicados cuyo horario se solapa con el de id_actividad."""
        marcas = ",".join("?" for _ in estados)
        query = f"""
            SELECT 1
              FROM Actividad nueva
              JOIN Actividad otra ON otra.id_oferta = nueva.id_oferta
                                 AND otra.dia_actividad = nueva.dia_actividad
                                 AND otra.id_actividad <> nueva.id_actividad
                                 AND otra.hora_inicio < nueva.hora_fin
                                 AND otra.hora_fin > nueva.hora_inicio
              JOIN Inscripcion i ON i.id_actividad = otra.id_actividad
             WHERE nueva.id_actividad = ? AND i.id_persona = ? AND i.estado IN ({marcas})
             LIMIT 1
        """
        return bool(self.db.executeQuery(query, id_actividad, id_persona, *estados))

    def obtener_lista(self, id_actividad: int):
        """Lista de espera ordenada: primero las solicitudes del periodo de socios y despues
        las del periodo general; dentro de cada periodo, por fecha y hora de solicitud."""
        query = """
            SELECT i.id_inscripcion, i.id_persona, i.fecha_solicitud
              FROM Inscripcion i
              JOIN Actividad a ON a.id_actividad = i.id_actividad
              JOIN Oferta o    ON o.id_oferta = a.id_oferta
             WHERE i.id_actividad = ? AND i.estado = 'en espera'
             ORDER BY CASE WHEN date(i.fecha_solicitud) <= o.cierre_socios THEN 0 ELSE 1 END,
                      i.fecha_solicitud, i.id_inscripcion
        """
        return self.db.executeQuery(query, id_actividad)

    def posicion(self, id_inscripcion: int):
        """Posicion (1 = la primera) en la lista de espera de su actividad, o None si no esta en espera."""
        res = self.db.executeQuery(
            "SELECT id_actividad FROM Inscripcion WHERE id_inscripcion = ? AND estado = 'en espera'",
            id_inscripcion)
        if not res:
            return None
        for n, ins in enumerate(self.obtener_lista(res[0]["id_actividad"]), start=1):
            if ins["id_inscripcion"] == id_inscripcion:
                return n
        return None

    def promocionar(self, id_actividad: int):
        """Confirma a la primera persona de la lista que cumpla las condiciones. Se omite a quien
        tenga ya otra actividad confirmada con horario coincidente. Devuelve el id de la inscripcion
        promocionada, o None si nadie puede ocupar la plaza (que queda libre)."""
        for ins in self.obtener_lista(id_actividad):
            if self.tiene_horario_coincidente(ins["id_persona"], id_actividad, ("confirmada",)):
                continue
            self.db.executeUpdateQuery(
                "UPDATE Inscripcion SET estado = 'confirmada' WHERE id_inscripcion = ?",
                ins["id_inscripcion"])
            return ins["id_inscripcion"]
        return None
