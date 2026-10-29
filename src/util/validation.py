from datetime import datetime


class ValidationError(ValueError):
    """Indica que un valor de entrada no cumple una regla de validación."""


DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def validate_option(value: str, options: list[str]) -> str:
    """Devuelve la opción elegida por su número (empezando en 1)."""
    try:
        index = int(value.strip())
    except ValueError as error:
        raise ValidationError("Debe introducir el número de una de las opciones.") from error

    if not 1 <= index <= len(options):
        raise ValidationError(f"La opción debe estar entre 1 y {len(options)}.")
    return options[index - 1]


def validate_days(value: str) -> str:
    """Recibe los números de los días separados por comas (ej: 1,3,5) y devuelve sus nombres."""
    parts = [part for part in value.replace(" ", "").split(",") if part]
    if not parts:
        raise ValidationError("Debe indicar al menos un día de la semana.")

    days = []
    for part in parts:
        day = validate_option(part, DIAS_SEMANA)
        if day in days:
            raise ValidationError(f"El día {day} está repetido.")
        days.append(day)
    days.sort(key=DIAS_SEMANA.index)
    return ",".join(days)


def validate_time(value: str) -> str:
    try:
        parsed = datetime.strptime(value.strip(), "%H:%M")
    except ValueError as error:
        raise ValidationError("La hora debe tener el formato HH:MM.") from error
    return parsed.strftime("%H:%M")


def validate_time_range(start_time: str, end_time: str) -> None:
    if end_time <= start_time:
        raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")


def validate_places(value: str) -> int:
    try:
        places = int(value.strip())
    except ValueError as error:
        raise ValidationError("El número de plazas debe ser un número entero.") from error

    if places <= 0:
        raise ValidationError("El número de plazas debe ser mayor que cero.")
    return places
