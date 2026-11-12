import csv
import re
from datetime import datetime

from util.validation import ValidationError, validate_time
from calendario.calendarioModel import _normalizar

SEPARADOR = ";"
COLUMNAS = ["dni_nie", "nombre", "actividad", "nivel", "dia",
            "hora_inicio", "hora_fin", "estado", "fecha_solicitud"]
OBLIGATORIAS = [c for c in COLUMNAS if c != "nivel"]
ESTADOS = ["confirmada", "en espera", "cancelada"]
ESTADO_CANCELADA = "cancelada"

FORMATO_HORA = "HH:MM"
FORMATO_FECHA_HORA = "YYYY-MM-DD HH:MM:SS"


def inconsistencia(linea, columna, motivo):
    return {"linea": linea, "columna": columna, "motivo": motivo}


def validar_hora(valor: str) -> bool:
    """HH:MM estricto (dos dígitos en cada parte) y hora real."""
    if not re.fullmatch(r"\d{2}:\d{2}", valor):
        return False
    try:
        validate_time(valor)
    except ValidationError:
        return False
    return True


def validar_fecha_hora(valor: str) -> bool:
    """YYYY-MM-DD HH:MM:SS estricto y fecha/hora reales."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", valor):
        return False
    try:
        datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    return True


def validar_dia(valor: str) -> bool:
    return valor.isdigit() and 1 <= int(valor) <= 7


class importacionModel:
    """Valida el contenido de un fichero CSV de inscripciones. No modifica la base de datos."""

    def validar_fichero(self, ruta: str):
        """
        Lee el fichero y devuelve (número de filas de datos, lista de inconsistencias).
        Cada inconsistencia es un diccionario con 'linea', 'columna' y 'motivo'.
        Lanza FileNotFoundError / ValidationError si el fichero no se puede leer.
        """
        try:
            with open(ruta, "r", encoding="utf-8-sig", newline="") as fichero:
                lector = csv.reader(fichero, delimiter=SEPARADOR)
                return self._validar(lector)
        except UnicodeDecodeError as error:
            raise ValidationError("El fichero no está codificado en UTF-8.") from error
        except csv.Error as error:
            raise ValidationError(f"El fichero no es un CSV válido: {error}") from error

    def _validar(self, lector):
        cabecera = next(lector, None)
        if cabecera is None:
            return 0, [inconsistencia(1, "-", "el fichero está vacío")]

        cabecera = [c.strip().lower() for c in cabecera]
        faltan = [c for c in COLUMNAS if c not in cabecera]
        if faltan:
            return 0, [inconsistencia(1, c, "falta la columna en la cabecera") for c in faltan]

        indice = {c: cabecera.index(c) for c in COLUMNAS}
        inconsistencias = []
        vistas = {}      # clave de inscripción -> primera línea en la que aparece
        filas = 0

        for fila in lector:
            if not any(campo.strip() for campo in fila):
                continue  # línea en blanco
            linea = lector.line_num
            filas += 1
            if len(fila) != len(cabecera):
                inconsistencias.append(inconsistencia(
                    linea, "-", f"número de columnas incorrecto (se esperaban {len(cabecera)}, hay {len(fila)})"))
                continue
            datos = {c: fila[indice[c]].strip() for c in COLUMNAS}
            inconsistencias += self._validar_fila(linea, datos)
            inconsistencias += self._comprobar_repetida(linea, datos, vistas)

        inconsistencias.sort(key=lambda i: i["linea"])
        return filas, inconsistencias

    @staticmethod
    def _validar_fila(linea, datos):
        errores = []

        # Campos obligatorios vacíos
        for columna in OBLIGATORIAS:
            if not datos[columna]:
                errores.append(inconsistencia(linea, columna, "campo obligatorio vacío"))

        # Datos incorrectos (solo si el campo no está vacío; el vacío ya se ha informado)
        horas_validas = {}
        for columna in ("hora_inicio", "hora_fin"):
            valor = datos[columna]
            if valor:
                horas_validas[columna] = validar_hora(valor)
                if not horas_validas[columna]:
                    errores.append(inconsistencia(linea, columna,
                                                  f"formato de hora no válido '{valor}' (debe ser {FORMATO_HORA})"))
        if horas_validas.get("hora_inicio") and horas_validas.get("hora_fin") \
                and datos["hora_inicio"] >= datos["hora_fin"]:
            errores.append(inconsistencia(linea, "hora_inicio",
                                          f"la hora de inicio ({datos['hora_inicio']}) no es anterior "
                                          f"a la de fin ({datos['hora_fin']})"))

        if datos["fecha_solicitud"] and not validar_fecha_hora(datos["fecha_solicitud"]):
            errores.append(inconsistencia(linea, "fecha_solicitud",
                                          f"formato de fecha no válido '{datos['fecha_solicitud']}' "
                                          f"(debe ser {FORMATO_FECHA_HORA})"))

        if datos["dia"] and not validar_dia(datos["dia"]):
            errores.append(inconsistencia(linea, "dia",
                                          f"día fuera de rango '{datos['dia']}' (debe ser un entero de 1 a 7)"))

        if datos["estado"] and datos["estado"] not in ESTADOS:
            errores.append(inconsistencia(linea, "estado",
                                          f"estado desconocido '{datos['estado']}' "
                                          f"(debe ser {', '.join(ESTADOS)})"))
        return errores

    @staticmethod
    def _comprobar_repetida(linea, datos, vistas):
        """Una misma persona no puede estar inscrita (sin cancelar) dos veces en la misma actividad."""
        if datos["estado"].lower() == ESTADO_CANCELADA:
            return []
        campos = [datos["dni_nie"], datos["actividad"], datos["nivel"], datos["dia"],
                  datos["hora_inicio"], datos["hora_fin"]]
        # Sin DNI/NIE o sin los datos de la actividad no se puede identificar la inscripción
        if not all(campos[i] for i in (0, 1, 3, 4, 5)):
            return []
        clave = tuple(_normalizar(c) for c in campos)
        if clave in vistas:
            return [inconsistencia(linea, "dni_nie",
                                   f"inscripción repetida: {datos['dni_nie']} ya está inscrita en la misma "
                                   f"actividad (línea {vistas[clave]})")]
        vistas[clave] = linea
        return []
