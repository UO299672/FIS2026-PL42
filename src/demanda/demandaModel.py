from util.database import Database
from util.validation import DIAS_SEMANA
from calendario.calendarioModel import hora_a_minutos

# Estados de inscripción que cuentan como demanda (confirmadas + lista de espera)
ESTADOS_DEMANDA = ("confirmada", "en espera")
# Duración de cada franja horaria en minutos
FRANJA_MINUTOS = 60


def formatear_minutos(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


class demandaModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    # ---------- Valores seleccionables ----------

    def listar_ofertas(self):
        """Ofertas con su número de actividades."""
        query = """
            SELECT o.id_oferta, o.anio,
                   (SELECT COUNT(*) FROM Actividad WHERE id_oferta = o.id_oferta) AS actividades
              FROM Oferta o
             ORDER BY o.anio
        """
        return self.db.executeQuery(query)

    def obtener_oferta(self, id_oferta: int):
        res = self.db.executeQuery("SELECT * FROM Oferta WHERE id_oferta = ?", id_oferta)
        return res[0] if res else None

    def listar_categorias(self):
        return self.db.executeQuery("SELECT id_categoria, nombre FROM Categoria ORDER BY id_categoria")

    # ---------- Demanda por día y franja horaria ----------

    def obtener_actividades(self, id_oferta: int):
        """Actividades de la oferta con su demanda (inscripciones confirmadas + en espera)."""
        marcas = ", ".join("?" for _ in ESTADOS_DEMANDA)
        query = f"""
            SELECT a.id_actividad, a.id_categoria, a.dia_actividad,
                   a.hora_inicio, a.hora_fin, a.plazas,
                   (SELECT COUNT(*)
                      FROM Inscripcion i
                     WHERE i.id_actividad = a.id_actividad
                       AND i.estado IN ({marcas})) AS demanda
              FROM Actividad a
             WHERE a.id_oferta = ?
        """
        return self.db.executeQuery(query, *ESTADOS_DEMANDA, id_oferta)

    @staticmethod
    def calcular_demanda(actividades, id_categoria: int = None):
        """
        Agrupa la demanda por día de la semana y franja horaria (de FRANJA_MINUTOS minutos).

        Una actividad cuenta en todas las franjas que solapa. Las franjas que se muestran
        abarcan desde la primera hora de inicio hasta la última hora de fin de la oferta
        completa (aunque se filtre por categoría), de modo que la rejilla es siempre la misma.
        Si se indica categoría, solo se suman las actividades de esa categoría.

        Devuelve {dia (1-7): [franja, ...]} donde cada franja es un diccionario con
        'franja', 'demanda', 'plazas', 'relacion' (demanda/plazas o None), 'sin_oferta'
        y 'destacada' ('mas', 'menos' o None).
        """
        if not actividades:
            return {}

        inicio = min(hora_a_minutos(a["hora_inicio"]) for a in actividades)
        fin = max(hora_a_minutos(a["hora_fin"]) for a in actividades)
        inicio -= inicio % FRANJA_MINUTOS
        fin += -fin % FRANJA_MINUTOS

        seleccion = [a for a in actividades if id_categoria is None or a["id_categoria"] == id_categoria]

        resultado = {}
        for dia in range(1, len(DIAS_SEMANA) + 1):
            franjas = []
            for desde in range(inicio, fin, FRANJA_MINUTOS):
                hasta = desde + FRANJA_MINUTOS
                solapadas = [a for a in seleccion
                             if a["dia_actividad"] == dia
                             and hora_a_minutos(a["hora_inicio"]) < hasta
                             and hora_a_minutos(a["hora_fin"]) > desde]
                demanda = sum(a["demanda"] for a in solapadas)
                plazas = sum(a["plazas"] for a in solapadas)
                franjas.append({
                    "franja": f"{formatear_minutos(desde)}-{formatear_minutos(hasta)}",
                    "demanda": demanda,
                    "plazas": plazas,
                    "relacion": demanda / plazas if plazas else None,
                    "sin_oferta": not solapadas,
                    "destacada": None,
                })
            resultado[dia] = franjas

        demandaModel._destacar(resultado)
        return resultado

    @staticmethod
    def _destacar(resultado):
        """Marca las franjas con oferta que tienen más y menos demanda total (todas las empatadas)."""
        con_oferta = [f for franjas in resultado.values() for f in franjas if not f["sin_oferta"]]
        if not con_oferta:
            return
        maxima = max(f["demanda"] for f in con_oferta)
        minima = min(f["demanda"] for f in con_oferta)
        if maxima == minima:
            return  # todas las franjas tienen la misma demanda: no hay nada que destacar
        for f in con_oferta:
            if f["demanda"] == maxima:
                f["destacada"] = "mas"
            elif f["demanda"] == minima:
                f["destacada"] = "menos"

    def consultar_demanda(self, id_oferta: int, id_categoria: int = None):
        return self.calcular_demanda(self.obtener_actividades(id_oferta), id_categoria)
