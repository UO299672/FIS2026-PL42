from datetime import date

from util.database import Database
from util.validation import DIAS_SEMANA
from calendario.calendarioModel import ESTADO_OCUPA_PLAZA, _normalizar

ESTADOS = ["confirmada", "en espera", "cancelada"]


class consultaModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)
        
    # ---------- Valores seleccionables en la búsqueda ----------

    def listar_categorias(self):
        rows = self.db.executeQuery("SELECT nombre FROM Categoria ORDER BY id_categoria")
        return [r["nombre"] for r in rows]

    def listar_niveles(self):
        rows = self.db.executeQuery(
            "SELECT DISTINCT nivel FROM Actividad WHERE nivel IS NOT NULL ORDER BY nivel")
        return [r["nivel"] for r in rows]

    def listar_instalaciones(self):
        rows = self.db.executeQuery("SELECT nombre FROM Instalacion ORDER BY id_instalacion")
        return [r["nombre"] for r in rows]

    # ---------- Actividades ----------

    def buscar_actividades(self, categoria: str = "", nivel: str = "", instalacion: str = ""):
        """Actividades que cumplen los filtros indicados (texto contenido, sin distinguir
        tildes ni mayúsculas). Los filtros vacíos se ignoran. Incluye plazas y periodos de su oferta."""
        query = """
            SELECT a.id_actividad,
                   o.anio,
                   c.nombre AS categoria,
                   a.nivel,
                   inst.nombre AS instalacion,
                   a.dia_actividad,
                   a.hora_inicio,
                   a.hora_fin,
                   a.plazas,
                   (SELECT COUNT(*)
                      FROM Inscripcion i
                     WHERE i.id_actividad = a.id_actividad
                       AND i.estado = ?) AS plazas_ocupadas,
                   o.apertura_socios, o.cierre_socios,
                   o.apertura_no_socios, o.cierre_no_socios
              FROM Actividad a
              JOIN Oferta o    ON o.id_oferta = a.id_oferta
              JOIN Categoria c ON c.id_categoria = a.id_categoria
              LEFT JOIN Instalacion inst ON inst.id_instalacion = a.id_instalacion
             ORDER BY o.anio, a.id_actividad
        """
        filtros = [(categoria, "categoria"), (nivel, "nivel"), (instalacion, "instalacion")]
        resultado = []
        for act in self.db.executeQuery(query, ESTADO_OCUPA_PLAZA):
            if all(_normalizar(texto) in _normalizar(act[campo] or "")
                   for texto, campo in filtros if texto.strip()):
                act["plazas_libres"] = max(act["plazas"] - act["plazas_ocupadas"], 0)
                resultado.append(act)
        return resultado

    @staticmethod
    def estado_periodo(apertura: str, cierre: str, hoy: date = None) -> str:
        """'no abierto', 'abierto' o 'cerrado' según la fecha (formato AAAA-MM-DD)."""
        """'no abierto', 'abierto', 'cerrado' o 'sin definir' (formato AAAA-MM-DD)."""
        if not apertura or not cierre:
            return "sin definir"
        hoy = (hoy or date.today()).isoformat()
        if hoy < apertura:
            return "no abierto"
        if hoy > cierre:
            return "cerrado"
        return "abierto"

    def obtener_inscritos(self, id_actividad: int):
        """Personas con inscripción confirmada (las que ocupan plaza) en la actividad."""
        query = """
            SELECT p.nombre, p.dni_nie, i.fecha_solicitud
              FROM Inscripcion i
              JOIN Persona p ON p.id_persona = i.id_persona
             WHERE i.id_actividad = ? AND i.estado = ?
             ORDER BY i.fecha_solicitud, i.id_inscripcion
        """
        return self.db.executeQuery(query, id_actividad, ESTADO_OCUPA_PLAZA)

    # ---------- Personas ----------

    def buscar_personas(self, texto: str):
        """Personas cuyo DNI/NIE coincide exactamente o cuyo nombre contiene el texto."""
        texto = texto.strip()
        if not texto:
            return []
        personas = self.db.executeQuery("SELECT * FROM Persona ORDER BY nombre")
        return [p for p in personas
                if p["dni_nie"].upper() == texto.upper()
                or _normalizar(texto) in _normalizar(p["nombre"])]

    def obtener_inscripciones(self, id_persona: int, estado: str = None):
        """Inscripciones de la persona, opcionalmente filtradas por estado."""
        query = """
            SELECT i.id_inscripcion,
                   c.nombre AS actividad,
                   a.nivel,
                   inst.nombre AS instalacion,
                   a.dia_actividad,
                   a.hora_inicio,
                   a.hora_fin,
                   i.estado,
                   i.fecha_solicitud
              FROM Inscripcion i
              JOIN Actividad a ON a.id_actividad = i.id_actividad
              JOIN Categoria c ON c.id_categoria = a.id_categoria
              LEFT JOIN Instalacion inst ON inst.id_instalacion = a.id_instalacion
             WHERE i.id_persona = ? AND (? IS NULL OR i.estado = ?)
             ORDER BY i.fecha_solicitud, i.id_inscripcion
        """
        return self.db.executeQuery(query, id_persona, estado, estado)

    @staticmethod
    def nombre_dia(dia) -> str:
        """Nombre del día a partir de dia_actividad (1 = lunes ... 7 = domingo)."""
        if isinstance(dia, int) and 1 <= dia <= 7:
            return DIAS_SEMANA[dia - 1]
        return str(dia)
