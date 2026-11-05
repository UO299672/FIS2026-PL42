import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from util.database import Database
from lista_espera.lista_esperaModel import lista_esperaModel
from cancelacion.cancelacionModel import cancelacionModel


class ListaEsperaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = Database(self.tmp.name)
        self.db.executeScript(os.path.join(ROOT, "resources", "schema.sql"))
        self.db.executeScript(os.path.join(ROOT, "resources", "data.sql"))
        self.lista = lista_esperaModel(self.tmp.name)
        self.canc = cancelacionModel(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def _estado(self, id_inscripcion):
        return self.db.executeQuery(
            "SELECT estado FROM Inscripcion WHERE id_inscripcion = ?", id_inscripcion)[0]["estado"]

    def _en_espera(self, id_persona, id_actividad, fecha):
        return self.db.executeUpdateQuery(
            "INSERT INTO Inscripcion (id_persona, id_actividad, estado, fecha_solicitud) "
            "VALUES (?, ?, 'en espera', ?)", id_persona, id_actividad, fecha)

    def test_posicion_y_orden(self):
        # Actividad 1 (llena): Pablo (socio, inscripcion 4) en espera desde el 26/08
        nueva = self._en_espera(6, 1, "2026-09-09 10:00:00")  # Carlos, no socio, periodo general
        self.assertEqual(self.lista.posicion(4), 1)
        self.assertEqual(self.lista.posicion(nueva), 2)
        self.assertIsNone(self.lista.posicion(1))  # confirmada: no esta en lista

    def test_promocion_actualiza_posiciones(self):
        nueva = self._en_espera(6, 1, "2026-09-09 10:00:00")
        self.canc.cancelar_inscripcion(1)  # cancela Ana (confirmada)
        self.assertEqual(self._estado(4), "confirmada")  # Pablo, el primero
        self.assertEqual(self.lista.posicion(nueva), 1)  # el resto sube

    def test_se_omite_a_quien_tiene_horario_coincidente(self):
        # Pablo confirma otra actividad que se solapa con la 1 (lunes 09:00-10:00)
        self.db.executeUpdateQuery(
            "INSERT INTO Actividad (id_oferta, id_categoria, id_instalacion, nivel, hora_inicio, hora_fin, "
            "dia_actividad, plazas) VALUES (1, 6, 2, NULL, '09:30', '10:30', 1, 5)")
        self.db.executeUpdateQuery(
            "INSERT INTO Inscripcion (id_persona, id_actividad, estado, fecha_solicitud) "
            "VALUES (4, 13, 'confirmada', '2026-08-31 10:00:00')")
        siguiente = self._en_espera(5, 1, "2026-08-27 10:00:00")  # Lucia, tambien socia
        self.canc.cancelar_inscripcion(1)
        self.assertEqual(self._estado(4), "en espera")      # omitido
        self.assertEqual(self._estado(siguiente), "confirmada")  # se continua con la siguiente

    def test_si_nadie_cumple_la_plaza_queda_libre(self):
        self.db.executeUpdateQuery(
            "INSERT INTO Actividad (id_oferta, id_categoria, id_instalacion, nivel, hora_inicio, hora_fin, "
            "dia_actividad, plazas) VALUES (1, 6, 2, NULL, '09:30', '10:30', 1, 5)")
        self.db.executeUpdateQuery(
            "INSERT INTO Inscripcion (id_persona, id_actividad, estado, fecha_solicitud) "
            "VALUES (4, 13, 'confirmada', '2026-08-31 10:00:00')")
        res = self.canc.cancelar_inscripcion(1)
        self.assertFalse(res["promocionado"])
        self.assertEqual(self._estado(4), "en espera")

    def test_horario_coincidente(self):
        # Ana (1) esta confirmada en la 1 (lunes 09:00-10:00) y en la 2 (lunes 18:00-19:30)
        self.assertTrue(self.lista.tiene_horario_coincidente(1, 8))    # lunes 19:00-20:00 pisa la 2
        self.assertFalse(self.lista.tiene_horario_coincidente(1, 6))   # jueves: otro dia
        self.assertFalse(self.lista.tiene_horario_coincidente(1, 1))   # la misma actividad no cuenta
        # 10:00-11:00 solo roza el final de la 1 (10:00): no se solapa
        self.db.executeUpdateQuery(
            "INSERT INTO Actividad (id_oferta, id_categoria, id_instalacion, nivel, hora_inicio, hora_fin, "
            "dia_actividad, plazas) VALUES (1, 6, 2, NULL, '10:00', '11:00', 1, 5)")
        self.assertFalse(self.lista.tiene_horario_coincidente(1, 13))


if __name__ == "__main__":
    unittest.main()
