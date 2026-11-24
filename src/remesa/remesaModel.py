import calendar
import os
from datetime import date

from util.database import Database
from util.paths import OUTPUT_DIR

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


class RemesaYaEmitida(Exception):
    """Indica que la remesa del mes indicado ya se emitió anteriormente."""


class remesaModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def existe_remesa(self, anio: int, mes: int) -> bool:
        res = self.db.executeQuery("SELECT 1 FROM Remesa WHERE anio = ? AND mes = ?", anio, mes)
        return bool(res)

    def emitir_remesa(self, anio: int, mes: int, fecha_emision: date | None = None):
        """
        Genera un recibo por cada inscripción confirmada en una actividad que se imparte en el mes indicado.
        Lanza RemesaYaEmitida si la remesa de ese mes ya existe (y no genera nada).
        Devuelve la lista de recibos generados.
        """
        if self.existe_remesa(anio, mes):
            raise RemesaYaEmitida(f"La remesa de {MESES[mes - 1]} de {anio} ya fue emitida.")

        fecha = (fecha_emision or date.today()).isoformat()
        inicio_mes = date(anio, mes, 1).isoformat()
        fin_mes = date(anio, mes, calendar.monthrange(anio, mes)[1]).isoformat()

        id_remesa = self.db.executeUpdateQuery(
            "INSERT INTO Remesa (anio, mes, fecha_emision) VALUES (?, ?, ?)", anio, mes, fecha)

        self.db.executeUpdateQuery("""
            INSERT INTO Recibo (id_remesa, id_inscripcion, importe, cuenta_bancaria, fecha_emision, estado)
            SELECT ?, i.id_inscripcion,
                   CASE WHEN p.tipo = 'socio' THEN a.precio_socio ELSE a.precio_no_socio END,
                   p.cuenta_bancaria, ?, 'emitido'
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Actividad a ON i.id_actividad = a.id_actividad
            WHERE i.estado = 'confirmada'
              AND a.fecha_inicio <= ? AND a.fecha_fin >= ?
            ORDER BY i.id_inscripcion
        """, id_remesa, fecha, fin_mes, inicio_mes)

        return self.obtener_recibos(id_remesa)

    def obtener_recibos(self, id_remesa: int):
        return self.db.executeQuery("""
            SELECT r.id_recibo, p.dni_nie, p.nombre,
                   c.nombre || COALESCE(' ' || a.nivel, '') AS actividad,
                   r.importe, r.cuenta_bancaria, r.fecha_emision, r.estado
            FROM Recibo r
            JOIN Inscripcion i ON r.id_inscripcion = i.id_inscripcion
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Actividad a ON i.id_actividad = a.id_actividad
            JOIN Categoria c ON a.id_categoria = c.id_categoria
            WHERE r.id_remesa = ?
            ORDER BY r.id_recibo
        """, id_remesa)

    @staticmethod
    def nombre_fichero(mes: int) -> str:
        return f"remesa_{MESES[mes - 1]}.txt"

    @staticmethod
    def exportar(recibos, mes: int) -> str:
        """Escribe una línea por recibo (campos separados por ';') en la carpeta outputs. Devuelve la ruta."""
        ruta = os.path.join(OUTPUT_DIR, remesaModel.nombre_fichero(mes))
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            for r in recibos:
                f.write(";".join([str(r["id_recibo"]), r["dni_nie"], r["nombre"], r["actividad"],
                                  f"{r['importe']:.2f}", r["cuenta_bancaria"] or "", r["fecha_emision"]]) + "\n")
        return ruta
