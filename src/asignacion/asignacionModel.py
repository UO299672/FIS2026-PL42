from util.database import Database
from util.validation import DIAS_SEMANA, ValidationError


def hora_a_minutos(hora: str) -> int:
    """Convierte 'HH:MM' (o 'HH:MM:SS') en minutos desde las 00:00."""
    partes = hora.split(":")
    return int(partes[0]) * 60 + int(partes[1])


def dias_de_actividad(valor) -> set[int]:
    """
    Devuelve los días (1 = lunes ... 7 = domingo) en los que se realiza la actividad.
    Admite tanto el número de día como una lista de nombres separados por comas
    (por ejemplo 'Lunes,Miércoles').
    """
    if valor is None:
        return set()
    if isinstance(valor, int):
        return {valor}
    dias = set()
    for parte in str(valor).split(","):
        parte = parte.strip()
        if not parte:
            continue
        if parte.isdigit():
            dias.add(int(parte))
        elif parte in DIAS_SEMANA:
            dias.add(DIAS_SEMANA.index(parte) + 1)
    return dias


def formatear_dias(valor) -> str:
    return ", ".join(DIAS_SEMANA[d - 1] for d in sorted(dias_de_actividad(valor))) or "-"


def se_solapan(a, b) -> bool:
    """Dos actividades se solapan si comparten algún día y sus franjas horarias se cruzan."""
    if not dias_de_actividad(a["dia_actividad"]) & dias_de_actividad(b["dia_actividad"]):
        return False
    return (hora_a_minutos(a["hora_inicio"]) < hora_a_minutos(b["hora_fin"])
            and hora_a_minutos(b["hora_inicio"]) < hora_a_minutos(a["hora_fin"]))


def describir_actividad(act) -> str:
    nivel = f" ({act['nivel']})" if act.get("nivel") else ""
    return (f"#{act['id_actividad']} {act['categoria']}{nivel}, {formatear_dias(act['dia_actividad'])} "
            f"{act['hora_inicio']}-{act['hora_fin']}")


class ConflictoInstalacionError(ValidationError):
    """La instalación ya está ocupada por otra actividad en la franja de la actividad."""

    def __init__(self, conflicto):
        self.conflicto = conflicto
        super().__init__(f"La instalación está ocupada por la actividad {describir_actividad(conflicto)}.")


_SELECT_ACTIVIDAD = """
    SELECT a.id_actividad, a.id_oferta, o.anio, c.nombre AS categoria, a.nivel,
           a.dia_actividad, a.hora_inicio, a.hora_fin, a.plazas,
           a.id_instalacion, i.nombre AS instalacion
      FROM Actividad a
      JOIN Oferta o         ON o.id_oferta = a.id_oferta
      JOIN Categoria c      ON c.id_categoria = a.id_categoria
      LEFT JOIN Instalacion i ON i.id_instalacion = a.id_instalacion
"""


class asignacionModel:
    def __init__(self, db_name="CompanyDB.db"):
        self.db = Database(db_name)

    def listar_actividades(self):
        return self.db.executeQuery(_SELECT_ACTIVIDAD + " ORDER BY o.anio, a.id_actividad")

    def obtener_actividad(self, id_actividad: int):
        rows = self.db.executeQuery(_SELECT_ACTIVIDAD + " WHERE a.id_actividad = ?", id_actividad)
        return rows[0] if rows else None

    def listar_instalaciones(self):
        return self.db.executeQuery("SELECT id_instalacion, nombre FROM Instalacion ORDER BY id_instalacion")

    def obtener_instalacion(self, id_instalacion: int):
        rows = self.db.executeQuery("SELECT id_instalacion, nombre FROM Instalacion WHERE id_instalacion = ?",
                                    id_instalacion)
        return rows[0] if rows else None

    def buscar_conflicto(self, actividad, id_instalacion: int):
        """
        Devuelve la primera actividad de la misma oferta asignada a la instalación que coincide
        con la actividad en algún día y franja horaria, o None si la instalación está libre.
        """
        candidatas = self.db.executeQuery(
            _SELECT_ACTIVIDAD + " WHERE a.id_instalacion = ? AND a.id_oferta = ? AND a.id_actividad <> ?"
                                " ORDER BY a.id_actividad",
            id_instalacion, actividad["id_oferta"], actividad["id_actividad"])
        return next((otra for otra in candidatas if se_solapan(actividad, otra)), None)

    def asignar_instalacion(self, id_actividad: int, id_instalacion: int):
        """
        Asigna la instalación a la actividad si está libre en todos sus días y horario.
        Lanza ConflictoInstalacionError (con la actividad en conflicto) si no lo está.
        Devuelve la actividad actualizada.
        """
        actividad = self.obtener_actividad(id_actividad)
        if actividad is None:
            raise ValidationError("No existe ninguna actividad con ese ID.")
        if self.obtener_instalacion(id_instalacion) is None:
            raise ValidationError("No existe ninguna instalación con ese ID.")

        conflicto = self.buscar_conflicto(actividad, id_instalacion)
        if conflicto is not None:
            raise ConflictoInstalacionError(conflicto)

        self.db.executeUpdateQuery("UPDATE Actividad SET id_instalacion = ? WHERE id_actividad = ?",
                                   id_instalacion, id_actividad)
        return self.obtener_actividad(id_actividad)
