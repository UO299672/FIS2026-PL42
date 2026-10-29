import os
import sys
from datetime import date

from tabulate import tabulate

from util.unexpectedException import UnexpectedException
from util.validation import ValidationError, validate_month
from .calendarioModel import calendarioModel

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

ROJO, VERDE, GRIS = "\033[31m", "\033[32m", "\033[2m"
RESET = "\033[0m"
ANCHO_CELDA = 16

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
if USE_COLOR and os.name == "nt":
    os.system("")  # activa las secuencias ANSI en la consola de Windows


def _color(texto: str, codigo: str) -> str:
    if not USE_COLOR:
        return texto
    return "\n".join(f"{codigo}{linea}{RESET}" for linea in texto.split("\n"))


class calendarioView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = calendarioModel(db_name)
        self.gestoropciones = {"1": self.ver_calendario,
                               "2": self.quit}

    def display_menu(self):
        print("""Calendario de ocupación: \n
            1.- Ver calendario mensual de una instalación
            2.- Salir
            """)

    def run(self):
        while True:
            self.display_menu()
            choice = input("Seleccione una opción: ").strip()
            accion = self.gestoropciones.get(choice)
            if accion:
                try:
                    resultado = accion()
                except UnexpectedException:
                    print("Se ha producido un error inesperado al acceder a los datos. "
                          "Inténtelo de nuevo más tarde.\n")
                    continue
                if resultado == 1:
                    break
            else:
                print("Opción inválida.\n")

    # ---------- Entrada de datos ----------

    def _pedir_instalacion(self):
        while True:
            texto = input("ID o nombre de la instalación ('c' para cancelar): ").strip()
            if texto.lower() == 'c':
                return None
            inst = self.model.buscar_instalacion(texto)
            if inst:
                return inst
            print("  Instalación no encontrada.")

    def _pedir_mes(self):
        hoy = date.today()
        por_defecto = f"{hoy.year}-{hoy.month:02d}"
        while True:
            texto = input(f"Mes a consultar (AAAA-MM) [Enter = {por_defecto}, 'c' para cancelar]: ").strip()
            if texto.lower() == 'c':
                return None
            if not texto:
                texto = por_defecto
            try:
                return validate_month(texto)
            except ValidationError as error:
                print(f"  {error}")

    # ---------- Funcionalidad ----------

    def ver_calendario(self):
        instalaciones = self.model.listar_instalaciones()
        if not instalaciones:
            print("No hay instalaciones registradas.\n")
            return
        print(tabulate(instalaciones, headers="keys", tablefmt="grid"))

        inst = self._pedir_instalacion()
        if inst is None:
            return
        periodo = self._pedir_mes()
        if periodo is None:
            return
        anio, mes = periodo

        if not self.model.obtener_oferta_por_anio(anio):
            anios = ", ".join(str(a) for a in self.model.listar_anios_con_oferta()) or "ninguno"
            print(f"No existe oferta de actividades para el año {anio} (años con oferta: {anios}).\n")
            return

        calendario = self.model.obtener_calendario_mensual(inst["id_instalacion"], anio, mes)
        self._mostrar_calendario(inst, anio, mes, calendario)

    def _mostrar_calendario(self, inst, anio, mes, calendario):
        print(f"\n=== {inst['nombre']} - {MESES[mes - 1].capitalize()} {anio} ===")
        if not calendario["actividades"]:
            print(f"La instalación no tiene actividades asignadas en la oferta {anio}: todas las franjas están libres.")

        franjas = calendario["franjas"]
        for n, semana in enumerate(calendario["semanas"], start=1):
            cabeceras = ["Franja"] + [
                f"{DIAS_SEMANA[i]} {d['fecha']:%d/%m}" + ("" if d["en_mes"] else "*")
                for i, d in enumerate(semana)
            ]
            filas, ocupadas, libres = [], 0, 0
            for idx, (ini, fin) in enumerate(franjas):
                fila = [f"{ini // 60:02d}:00-{fin // 60:02d}:00"]
                for dia in semana:
                    entradas = dia["franjas"][idx]
                    if not dia["en_mes"]:
                        fila.append(_color("", GRIS))
                    elif entradas:
                        ocupadas += 1
                        fila.append(self._formatear_ocupada(entradas))
                    else:
                        libres += 1
                        fila.append(_color("LIBRE", VERDE))
                filas.append(fila)
            print(f"\nSemana {n}")
            print(tabulate(filas, headers=cabeceras, tablefmt="grid", stralign="left"))
            print(f"Franjas ocupadas: {ocupadas} | Franjas libres: {libres}")

        print("\nLeyenda: LIBRE = franja sin actividad | franja ocupada = #id de actividad, "
              "horario, categoría, nivel y plazas ocupadas/totales | (cont. #id) = la actividad continúa "
              "de la franja anterior | * = día fuera del mes\n")

    @staticmethod
    def _formatear_ocupada(entradas) -> str:
        bloques = []
        for e in entradas:
            act = e["actividad"]
            if e["primera"]:
                completa = act["plazas_ocupadas"] >= act["plazas"]
                lineas = [
                    f"#{act['id_actividad']} {act['hora_inicio']}-{act['hora_fin']}",
                    act["categoria"][:ANCHO_CELDA],
                    (f"Niv. {act['nivel']}" if act["nivel"] else "Sin nivel")[:ANCHO_CELDA],
                    f"{act['plazas_ocupadas']}/{act['plazas']} plazas" + (" COMPLETA" if completa else ""),
                ]
            else:
                lineas = [f"(cont. #{act['id_actividad']})"]
            bloques.append("\n".join(lineas))
        return _color("\n--\n".join(bloques), ROJO)

    def quit(self):
        print("Cerrando opciones\n")
        return 1
