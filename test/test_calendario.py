import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from util.database import DataBase
from calendario.calendarioModel import calendarioModel


class CalendarioModelTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        db = DataBase(self.tmp.name)
        db.executeScript(os.path.join(ROOT, "resources", "schema.sql"))
        db.executeScript(os.path.join(ROOT, "resources", "data.sql"))
        self.model = calendarioModel(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def _dia(self, cal, fecha_iso):
        for semana in cal["semanas"]:
            for dia in semana:
                if dia["fecha"].isoformat() == fecha_iso:
                    return dia
        self.fail(f"{fecha_iso} no está en el calendario")

    def test_busca_instalacion_por_id_y_nombre(self):
        self.assertEqual(self.model.buscar_instalacion("1")["nombre"], "Piscina")
        self.assertEqual(self.model.buscar_instalacion("  pabellon ")["id_instalacion"], 4)
        self.assertIsNone(self.model.buscar_instalacion("Inexistente"))

    def test_actividad_ocupada_con_plazas(self):
        cal = self.model.obtener_calendario_mensual(1, 2026, 10)
        dia = self._dia(cal, "2026-10-05")  # lunes
        idx = cal["franjas"].index((9 * 60, 10 * 60))
        entradas = dia["franjas"][idx]
        self.assertEqual(len(entradas), 1)
        act = entradas[0]["actividad"]
        self.assertEqual((act["categoria"], act["nivel"]), ("Natación", "Inicial"))
        # 3 confirmadas; la 'en espera' no cuenta
        self.assertEqual((act["plazas_ocupadas"], act["plazas"]), (3, 3))

    def test_cancelada_no_ocupa_plaza(self):
        acts = {a["id_actividad"]: a for a in self.model.obtener_actividades(1, 2026)}
        self.assertEqual(acts[3]["plazas_ocupadas"], 2)

    def test_franja_libre(self):
        cal = self.model.obtener_calendario_mensual(1, 2026, 10)
        dia = self._dia(cal, "2026-10-06")  # martes, la piscina no tiene nada
        self.assertTrue(all(not f for f in dia["franjas"]))

    def test_actividad_de_dos_franjas_marca_continuacion(self):
        cal = self.model.obtener_calendario_mensual(1, 2026, 10)
        dia = self._dia(cal, "2026-10-05")  # lunes 18:00-19:30
        i18 = cal["franjas"].index((18 * 60, 19 * 60))
        i19 = cal["franjas"].index((19 * 60, 20 * 60))
        self.assertTrue(dia["franjas"][i18][0]["primera"])
        self.assertFalse(dia["franjas"][i19][0]["primera"])

    def test_dias_fuera_de_mes_sin_actividades(self):
        cal = self.model.obtener_calendario_mensual(1, 2026, 10)
        dia = self._dia(cal, "2026-09-28")  # lunes de septiembre
        self.assertFalse(dia["en_mes"])
        self.assertTrue(all(not f for f in dia["franjas"]))

    def test_instalacion_sin_actividades_y_anio_sin_oferta(self):
        cal = self.model.obtener_calendario_mensual(5, 2026, 10)
        self.assertEqual(cal["actividades"], [])
        self.assertIsNone(self.model.obtener_oferta_por_anio(2030))

    def test_oferta_del_anio_correcto(self):
        self.assertEqual(len(self.model.obtener_actividades(1, 2027)), 1)


if __name__ == "__main__":
    unittest.main()
