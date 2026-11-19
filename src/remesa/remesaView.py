from util.unexpectedException import UnexpectedException
from util.validation import ValidationError, validate_month
from .remesaModel import remesaModel, RemesaYaEmitida, MESES


class remesaView:
    def __init__(self, db_name="CompanyDB.db"):
        self.model = remesaModel(db_name)

    def run(self):
        try:
            self.emitir()
        except UnexpectedException:
            print("Error de acceso a la base de datos. Intentelo de nuevo.\n")

    def emitir(self):
        print("\n==========================================")
        print("      EMITIR REMESA MENSUAL DE RECIBOS")
        print("==========================================")

        while True:
            valor = input("Mes y año de la remesa (AAAA-MM, 'c' para cancelar): ").strip()
            if valor.lower() == 'c' or not valor:
                print("Operacion cancelada.")
                return
            try:
                anio, mes = validate_month(valor)
                break
            except ValidationError as e:
                print(f"  {e}")

        try:
            recibos = self.model.emitir_remesa(anio, mes)
        except RemesaYaEmitida as e:
            print(f"{e} No se ha generado nada.")
            return

        fichero = self.model.exportar(recibos, mes)

        total = sum(r["importe"] for r in recibos)
        print("\n==========================================")
        print(f"  RESUMEN REMESA {MESES[mes - 1].upper()} {anio}")
        print("==========================================")
        print(f"Recibos generados : {len(recibos)}")
        print(f"Importe total     : {total:.2f} €")
        print(f"Fichero exportado : {fichero}")
