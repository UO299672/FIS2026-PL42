from datetime import date, datetime
from util.database import Database
from util.validation import ValidationError


def parsear_fecha(valor: str, campo: str) -> date:
    """
    Convierte una fecha en formato dd/mm/aaaa a date. Lanza ValidationError si no es válida.
    """
    try:
        return datetime.strptime(valor.strip(), "%d/%m/%Y").date()
    except ValueError as error:
        raise ValidationError(f"La fecha de {campo} debe tener el formato dd/mm/aaaa y ser una fecha válida.") from error


def formatear_fecha(valor):
    """
    Pasa una fecha guardada en la BD (YYYY-MM-DD) a dd/mm/aaaa para mostrarla.
    """
    if not valor:
        return "-"
    return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")


def comprobar_antes_de_primera_sesion(fecha: date, primera_sesion: date, campo: str) -> None:
    if fecha >= primera_sesion:
        raise ValidationError(f"La fecha de {campo} debe ser anterior a la primera sesión de las actividades "
                              f"({primera_sesion.strftime('%d/%m/%Y')}).")


def comprobar_cierre_tras_apertura(apertura: date, cierre: date, periodo: str) -> None:
    if cierre < apertura:
        raise ValidationError(f"El cierre del periodo de {periodo} no puede ser anterior a su apertura "
                              f"({apertura.strftime('%d/%m/%Y')}).")


def comprobar_no_socios_tras_socios(apertura_socios: date, apertura_no_socios: date) -> None:
    if apertura_no_socios <= apertura_socios:
        raise ValidationError("El periodo de no socios debe comenzar estrictamente después de la apertura "
                              f"del periodo de socios ({apertura_socios.strftime('%d/%m/%Y')}).")


def validar_periodos(apertura_socios: date, cierre_socios: date,
                     apertura_no_socios: date, cierre_no_socios: date, primera_sesion: date) -> None:
    """
    Comprueba las reglas de los periodos de inscripción. Lanza ValidationError con el motivo.
    """
    comprobar_antes_de_primera_sesion(apertura_socios, primera_sesion, "apertura de socios")
    comprobar_cierre_tras_apertura(apertura_socios, cierre_socios, "socios")
    comprobar_antes_de_primera_sesion(cierre_socios, primera_sesion, "cierre de socios")
    comprobar_no_socios_tras_socios(apertura_socios, apertura_no_socios)
    comprobar_antes_de_primera_sesion(apertura_no_socios, primera_sesion, "apertura de no socios")
    comprobar_cierre_tras_apertura(apertura_no_socios, cierre_no_socios, "no socios")
    comprobar_antes_de_primera_sesion(cierre_no_socios, primera_sesion, "cierre de no socios")


class periodosModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def listar_ofertas(self):
        """
        Lista las ofertas con sus periodos de inscripción actuales y su número de actividades.
        """
        query = """
            SELECT o.id_oferta, o.anio, o.apertura_socios, o.cierre_socios,
                   o.apertura_no_socios, o.cierre_no_socios,
                   (SELECT COUNT(*) FROM Actividad WHERE id_oferta = o.id_oferta) AS actividades
            FROM Oferta o
            ORDER BY o.anio
        """
        return self.db.executeQuery(query)

    def obtener_oferta(self, id_oferta: int):
        query = "SELECT * FROM Oferta WHERE id_oferta = ?"
        res = self.db.executeQuery(query, id_oferta)
        return res[0] if res else None

    def guardar_periodos(self, id_oferta: int, apertura_socios: date, cierre_socios: date,
                         apertura_no_socios: date, cierre_no_socios: date, primera_sesion: date) -> None:
        """
        Valida y registra los periodos de inscripción de la oferta.
        Si las fechas no son válidas lanza ValidationError y no se guarda nada.
        """
        validar_periodos(apertura_socios, cierre_socios, apertura_no_socios, cierre_no_socios, primera_sesion)
        query = """
            UPDATE Oferta
            SET apertura_socios = ?, cierre_socios = ?, apertura_no_socios = ?, cierre_no_socios = ?
            WHERE id_oferta = ?
        """
        self.db.executeUpdateQuery(query, apertura_socios.isoformat(), cierre_socios.isoformat(),
                                   apertura_no_socios.isoformat(), cierre_no_socios.isoformat(), id_oferta)
