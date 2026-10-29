from datetime import date

NIVELES = ["Iniciación", "Medio", "Avanzado"]


class ActividadDAO:
    '''Acceso a datos necesario para añadir actividades a la oferta actual.'''

    def __init__(self, db):
        self.db = db

    def get_oferta_actual(self, today=None):
        '''Oferta cuyas inscripciones aún no se han abierto (la más próxima), o None.'''
        today = (today or date.today()).isoformat()
        rows = self.db.executeQuery(
            "SELECT * FROM Oferta WHERE apertura_socios > ? ORDER BY apertura_socios LIMIT 1", today)
        return rows[0] if rows else None

    def get_categorias(self):
        return self.db.executeQuery("SELECT id_categoria, nombre FROM Categoria ORDER BY id_categoria")

    def insert_actividad(self, id_oferta, id_categoria, nivel, dias, hora_inicio, hora_fin, plazas):
        return self.db.executeUpdateQuery(
            "INSERT INTO Actividad (id_oferta, id_categoria, nivel, dia_actividad, hora_inicio, hora_fin, plazas) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            id_oferta, id_categoria, nivel, dias, hora_inicio, hora_fin, plazas)

    def get_actividad(self, id_actividad):
        rows = self.db.executeQuery(
            "SELECT a.id_actividad, o.anio, c.nombre AS categoria, a.nivel, a.dia_actividad, "
            "a.hora_inicio, a.hora_fin, a.plazas "
            "FROM Actividad a JOIN Categoria c ON a.id_categoria = c.id_categoria "
            "JOIN Oferta o ON a.id_oferta = o.id_oferta WHERE a.id_actividad = ?", id_actividad)
        return rows[0] if rows else None
