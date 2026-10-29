from src.util.database import Database
from src.util.validation import validate_date, validate_time, validate_string

def formulario_actividad():
    nombre = input("Ingrese el nombre de la actividad: ")
    fecha = input("Ingrese la fecha de la actividad (YYYY-MM-DD): ")
    hora_inicio = input("Ingrese la hora de inicio (HH:MM): ")
    hora_fin = input("Ingrese la hora de fin (HH:MM): ")
    plazas_ofertadas = input("Ingrese el número de plazas ofertadas: ")
    return nombre, fecha, hora_inicio, hora_fin, plazas_ofertadas

def añadir_actividad(nombre: str, fecha: str, hora_inicio: str, hora_fin: str, plazas_ofertadas: int) -> None:
    """Añade una nueva actividad a la base de datos."""
    nombre, fecha, hora_inicio, hora_fin, plazas_ofertadas = formulario_actividad()  # Solicita los datos al usuario

    nombre_validado = validate_string(nombre)
    fecha_validada = validate_date(fecha)
    hora_inicio_validada = validate_time(hora_inicio)
    hora_fin_validada = validate_time(hora_fin)
    try:
        plazas_ofertadas_validadas = int(plazas_ofertadas)
    except ValueError:
        raise ValueError("El número de plazas ofertadas debe ser un entero.")
    if hora_fin_validada <= hora_inicio_validada:
        raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

    db = Database()
    db.insert_actividad(nombre_validado, fecha_validada, hora_inicio_validada, hora_fin_validada)

