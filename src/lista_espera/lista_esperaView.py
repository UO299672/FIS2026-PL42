import sys
from .lista_esperaModel import lista_esperaModel
import warnings
from tabulate import tabulate
warnings.filterwarnings("ignore")

class lista_esperaView:
    def __init__(self):
        self.tienda: lista_esperaView = lista_esperaModel()
        self.gestoropciones = { "1": self.ejemplo,
                                "3": self.quit}
        
    def display_lista_espera_menu(self):
        print("""Opciones de usuario: \n
            1.- 
            2.- Salir
            """)

    def run (self):
        while True:
            self.display_lista_espera_menu()
            choice = input("Seleccione una opción: ").strip()
            accion = self.gestoropciones.get(choice)
            if accion:
                resultado = accion()
                if resultado == 1:
                    break
            else:
                print("Opción inválida.\n")

    def quit(self):
        print("Cerrando opciones\n")
        return 1