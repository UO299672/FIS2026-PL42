import os
from datetime import date
from util.database import Database

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "CompanyDB.db",
)


class demandaModel:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db = Database(db_path)

class demandaModel:
    def __init__(self, db_path="CompanyDB.db"):
        self.db = Database(db_path)

    def obtener_ofertas_disponibles(self):
        """
        Devuelve únicamente la oferta (temporada) actual y las pasadas
        (incluidas las históricas importadas), excluyendo ofertas futuras.
        """
        anio_actual = date.today().year
        query = """
            SELECT id_oferta, anio, apertura_socios, cierre_socios,
                   apertura_no_socios, cierre_no_socios
            FROM Oferta
            WHERE anio <= ?
            ORDER BY anio DESC, id_oferta DESC
        """
        ofertas = self.db.executeQuery(query, anio_actual)
        for oferta in ofertas:
            oferta["tipo_temporada"] = (
                "Actual" if oferta["anio"] == anio_actual else "Pasada / Histórica"
            )
        return ofertas

    def obtener_categorias(self):
        """Obtiene todas las categorías disponibles para el filtro opcional."""
        query = "SELECT id_categoria, nombre FROM Categoria ORDER BY id_categoria"
        return self.db.executeQuery(query)

    def obtener_comparativa_demanda(
        self, id_oferta: int, id_categoria: int | None = None, porcentaje_minimo: float = 50.0
    ):
        """
        Calcula plazas ofertadas, confirmadas, en lista de espera, demanda total,
        porcentaje demanda/plazas y clasificación (Alta demanda / Baja demanda / Normal)
        para una única oferta y un filtro opcional de categoría.
        """
        query = """
            SELECT
                a.id_actividad,
                c.nombre AS categoria,
                a.nivel,
                a.dia_actividad,
                a.hora_inicio,
                a.hora_fin,
                inst.nombre AS instalacion,
                a.plazas AS plazas_ofertadas,
                COALESCE(SUM(CASE WHEN ins.estado = 'confirmada' THEN 1 ELSE 0 END), 0) AS confirmadas,
                COALESCE(SUM(CASE WHEN ins.estado = 'en espera' THEN 1 ELSE 0 END), 0) AS en_espera
            FROM Actividad a
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            LEFT JOIN Instalacion inst ON a.id_instalacion = inst.id_instalacion
            LEFT JOIN Inscripcion ins ON a.id_actividad = ins.id_actividad
            WHERE a.id_oferta = ?
        """
        params = [id_oferta]

        if id_categoria is not None:
            query += " AND a.id_categoria = ?"
            params.append(id_categoria)

        query += """
            GROUP BY
                a.id_actividad, c.nombre, a.nivel, a.dia_actividad,
                a.hora_inicio, a.hora_fin, inst.nombre, a.plazas
        """

        filas = self.db.executeQuery(query, *params)
        resultados = []

        for fila in filas:
            act = dict(fila)
            plazas = act["plazas_ofertadas"]
            confirmadas = act["confirmadas"]
            en_espera = act["en_espera"]
            demanda_total = confirmadas + en_espera

            act["demanda_total"] = demanda_total

            if plazas > 0:
                porcentaje = round((demanda_total / plazas) * 100, 2)
            else:
                porcentaje = None

            act["porcentaje_demanda"] = porcentaje

            # Clasificación según la HU:
            # - Alta demanda: tiene lista de espera o supera el 100 % de demanda sobre plazas.
            # - Baja demanda: no llega al porcentaje mínimo configurable (por defecto 50 %).
            if en_espera > 0 or (porcentaje is not None and porcentaje > 100.0) or (plazas == 0 and demanda_total > 0):
                act["clasificacion"] = "Alta demanda"
            elif porcentaje is not None and porcentaje < porcentaje_minimo:
                act["clasificacion"] = "Baja demanda"
            else:
                act["clasificacion"] = "Normal"

            resultados.append(act)

        # Ordenar de mayor a menor demanda (y porcentaje como desempate)
        resultados.sort(
            key=lambda x: (
                x["demanda_total"],
                x["porcentaje_demanda"] if x["porcentaje_demanda"] is not None else float("inf"),
                x["en_espera"],
            ),
            reverse=True,
        )

        return resultados