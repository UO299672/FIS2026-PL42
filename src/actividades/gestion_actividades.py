from src.util.database import Database
from src.util.validation import validate_date, validate_time, validate_string

def añadir_actividad(nombre: str, fecha: str, hora_inicio: str, hora_fin: str) -> None:
    """Añade una nueva actividad a la base de datos."""
    nombre_validado = validate_string(nombre)
    fecha_validada = validate_date(fecha)
    hora_inicio_validada = validate_time(hora_inicio)
    hora_fin_validada = validate_time(hora_fin)

    if hora_fin_validada <= hora_inicio_validada:
        raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

    db = Database()
    db.insert_actividad(nombre_validado, fecha_validada, hora_inicio_validada, hora_fin_validada)