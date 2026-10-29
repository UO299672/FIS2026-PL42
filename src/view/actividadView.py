import logging

from src.util.actividadDAO import NIVELES, ActividadDAO
from src.util.unexpectedException import UnexpectedException
from src.util.validation import (DIAS_SEMANA, ValidationError, validate_days, validate_option,
                                 validate_places, validate_time, validate_time_range)

logger = logging.getLogger(__name__)


def ask(prompt, validator):
    '''Pide un valor por consola hasta que pasa la validación.'''
    while True:
        try:
            return validator(input(prompt))
        except ValidationError as e:
            print(f"  Error: {e}")


def show_options(options):
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")


def add_actividad(db):
    '''Añade una nueva actividad a la oferta actual y muestra los datos registrados.'''
    dao = ActividadDAO(db)
    try:
        oferta = dao.get_oferta_actual()
        if oferta is None:
            print("No hay ninguna oferta con las inscripciones pendientes de abrir.")
            return
        print(f"\nNueva actividad para la oferta {oferta['anio']}")

        categorias = dao.get_categorias()
        nombres = [c["nombre"] for c in categorias]
        print("Categoría:")
        show_options(nombres)
        nombre = ask("Seleccione la categoría: ", lambda v: validate_option(v, nombres))
        id_categoria = categorias[nombres.index(nombre)]["id_categoria"]

        print("Nivel:")
        show_options(NIVELES)
        nivel = ask("Seleccione el nivel: ", lambda v: validate_option(v, NIVELES))

        print("Días de la semana:")
        show_options(DIAS_SEMANA)
        dias = ask("Seleccione los días separados por comas (ej: 1,3,5): ", validate_days)

        while True:
            hora_inicio = ask("Hora de inicio (HH:MM): ", validate_time)
            hora_fin = ask("Hora de fin (HH:MM): ", validate_time)
            try:
                validate_time_range(hora_inicio, hora_fin)
                break
            except ValidationError as e:
                print(f"  Error: {e}")

        plazas = ask("Número de plazas disponibles: ", validate_places)

        id_actividad = dao.insert_actividad(oferta["id_oferta"], id_categoria, nivel, dias,
                                            hora_inicio, hora_fin, plazas)
        actividad = dao.get_actividad(id_actividad)
    except UnexpectedException:
        print("Se ha producido un error inesperado al acceder a los datos.")
        return

    print("\nActividad registrada:")
    print(f"  Id:         {actividad['id_actividad']}")
    print(f"  Oferta:     {actividad['anio']}")
    print(f"  Categoría:  {actividad['categoria']}")
    print(f"  Nivel:      {actividad['nivel']}")
    print(f"  Días:       {actividad['dia_actividad'].replace(',', ', ')}")
    print(f"  Horario:    {actividad['hora_inicio']} - {actividad['hora_fin']}")
    print(f"  Plazas:     {actividad['plazas']}\n")
