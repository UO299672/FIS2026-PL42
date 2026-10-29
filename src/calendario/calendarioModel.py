import calendar
import unicodedata
from datetime import date

from util.database import DataBase

# Rango horario base que siempre se muestra (se amplía si hay actividades fuera de él)
HORA_APERTURA = 8
HORA_CIERRE = 22

# Solo las inscripciones en este estado ocupan plaza
ESTADO_OCUPA_PLAZA = 'confirmada'


def hora_a_minutos(hora: str) -> int:
    """Convierte 'HH:MM' (o 'HH:MM:SS') en minutos desde las 00:00."""
    partes = hora.split(":")
    return int(partes[0]) * 60 + int(partes[1])


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    return ' '.join(texto.split()).lower()


class calendarioModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = DataBase(db_name)

    # ---------- Acceso a datos ----------

    def listar_instalaciones(self):
        query = "SELECT id_instalacion, nombre FROM Instalacion ORDER BY id_instalacion"
        return self.db.executeQuery(query)

    def buscar_instalacion(self, texto: str):
        """Busca una instalación por id o por nombre (sin distinguir tildes ni mayúsculas)."""
        texto = texto.strip()
        for inst in self.listar_instalaciones():
            if texto == str(inst["id_instalacion"]) or _normalizar(texto) == _normalizar(inst["nombre"]):
                return inst
        return None

    def obtener_oferta_por_anio(self, anio: int):
        rows = self.db.executeQuery("SELECT * FROM Oferta WHERE anio = ?", anio)
        return rows[0] if rows else None

    def listar_anios_con_oferta(self):
        rows = self.db.executeQuery("SELECT anio FROM Oferta ORDER BY anio")
        return [r["anio"] for r in rows]

    def obtener_actividades(self, id_instalacion: int, anio: int):
        """Actividades de la oferta del año asignadas a la instalación, con sus plazas ocupadas."""
        query = """
            SELECT a.id_actividad,
                   c.nombre AS categoria,
                   a.nivel,
                   a.dia_actividad,
                   a.hora_inicio,
                   a.hora_fin,
                   a.plazas,
                   (SELECT COUNT(*)
                      FROM Inscripcion i
                     WHERE i.id_actividad = a.id_actividad
                       AND i.estado = ?) AS plazas_ocupadas
              FROM Actividad a
              JOIN Oferta o    ON o.id_oferta = a.id_oferta
              JOIN Categoria c ON c.id_categoria = a.id_categoria
             WHERE a.id_instalacion = ? AND o.anio = ?
             ORDER BY a.dia_actividad, a.hora_inicio
        """
        return self.db.executeQuery(query, ESTADO_OCUPA_PLAZA, id_instalacion, anio)

    # ---------- Construcción del calendario (lógica pura, sin E/S) ----------

    @staticmethod
    def calcular_franjas(actividades):
        """Franjas de una hora, desde HORA_APERTURA a HORA_CIERRE ampliadas si hace falta.
        Devuelve una lista de (inicio_min, fin_min)."""
        desde, hasta = HORA_APERTURA, HORA_CIERRE
        for act in actividades:
            desde = min(desde, hora_a_minutos(act["hora_inicio"]) // 60)
            hasta = max(hasta, -(-hora_a_minutos(act["hora_fin"]) // 60))  # techo
        return [(h * 60, (h + 1) * 60) for h in range(desde, hasta)]

    @staticmethod
    def construir_calendario_mensual(actividades, anio: int, mes: int):
        """
        Construye el calendario del mes. Las actividades se repiten cada semana en su día
        (dia_actividad: 1 = lunes ... 7 = domingo).

        Devuelve {'franjas': [(ini, fin), ...], 'semanas': [[dia, ...7], ...]} donde cada dia es
        {'fecha': date, 'en_mes': bool, 'franjas': [[entrada, ...], ...]} y cada entrada
        {'actividad': dict, 'primera': bool} (primera=True en la franja donde empieza la actividad).
        """
        franjas = calendarioModel.calcular_franjas(actividades)
        semanas = []
        for semana in calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes):
            dias = []
            for fecha in semana:
                en_mes = fecha.month == mes
                celdas = []
                for ini_f, fin_f in franjas:
                    entradas = []
                    if en_mes:
                        for act in actividades:
                            if act["dia_actividad"] != fecha.isoweekday():
                                continue
                            ini_a = hora_a_minutos(act["hora_inicio"])
                            fin_a = hora_a_minutos(act["hora_fin"])
                            if ini_a < fin_f and fin_a > ini_f:
                                entradas.append({"actividad": act, "primera": ini_f <= ini_a < fin_f})
                    celdas.append(entradas)
                dias.append({"fecha": fecha, "en_mes": en_mes, "franjas": celdas})
            semanas.append(dias)
        return {"franjas": franjas, "semanas": semanas}

    def obtener_calendario_mensual(self, id_instalacion: int, anio: int, mes: int):
        actividades = self.obtener_actividades(id_instalacion, anio)
        calendario = self.construir_calendario_mensual(actividades, anio, mes)
        calendario["actividades"] = actividades
        return calendario
