import os
import sys
import tempfile
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from util.database import Database
from consulta.consultaModel import consultaModel


class ConsultaModelTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        db = Database(self.tmp.name)
        db.executeScript(os.path.join(ROOT, "resources", "schema.sql"))
        db.executeScript(os.path.join(ROOT, "resources", "data.sql"))
        self.model = consultaModel(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_busca_actividad_por_categoria_nivel_e_instalacion(self):
        acts = self.model.buscar_actividades(categoria="natacion", nivel="inicial", instalacion="piscina")
        self.assertEqual({a["id_actividad"] for a in acts}, {1, 4, 12})
        acts = self.model.buscar_actividades(categoria="tenis", nivel="avanzado")
        self.assertEqual([a["id_actividad"] for a in acts], [10])

    def test_sin_resultados(self):
        self.assertEqual(self.model.buscar_actividades(categoria="esgrima"), [])

    def test_plazas(self):
        act = self.model.buscar_actividades(categoria="natacion", nivel="inicial", instalacion="piscina")[0]
        # actividad 1: 3 plazas, 3 confirmadas; la 'en espera' no ocupa plaza
        self.assertEqual((act["plazas"], act["plazas_ocupadas"], act["plazas_libres"]), (3, 3, 0))

    def test_estado_periodo(self):
        f = consultaModel.estado_periodo
        self.assertEqual(f("2026-08-25", "2026-09-05", date(2026, 8, 24)), "no abierto")
        self.assertEqual(f("2026-08-25", "2026-09-05", date(2026, 8, 25)), "abierto")
        self.assertEqual(f("2026-08-25", "2026-09-05", date(2026, 9, 5)), "abierto")
        self.assertEqual(f("2026-08-25", "2026-09-05", date(2026, 9, 6)), "cerrado")

    def test_inscritos_solo_confirmados(self):
        inscritos = self.model.obtener_inscritos(1)
        self.assertEqual([i["dni_nie"] for i in inscritos], ["12345678A", "23456789B", "34567890C"])
        self.assertEqual(self.model.obtener_inscritos(9 + 3), [])  # actividad 12 sin inscritos

    def test_busca_persona_por_dni_y_nombre(self):
        self.assertEqual(self.model.buscar_personas("12345678a")[0]["nombre"], "Ana García")
        self.assertEqual(self.model.buscar_personas("  garcia ")[0]["dni_nie"], "12345678A")
        self.assertEqual(self.model.buscar_personas("zzz"), [])

    def test_inscripciones_y_filtro_por_estado(self):
        # Ana (id 1): inscripciones 1, 5 y 10, todas confirmadas
        self.assertEqual(len(self.model.obtener_inscripciones(1)), 3)
        self.assertEqual(self.model.obtener_inscripciones(1, "cancelada"), [])
        # Elena (id 7): una cancelada
        canceladas = self.model.obtener_inscripciones(7, "cancelada")
        self.assertEqual([i["id_inscripcion"] for i in canceladas], [9])
        self.assertEqual(self.model.obtener_inscripciones(7, "confirmada"), [])


if __name__ == "__main__":
    unittest.main()
