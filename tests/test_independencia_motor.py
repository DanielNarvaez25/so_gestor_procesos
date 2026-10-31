"""El dominio se puede ejecutar sin importar la biblioteca gráfica."""
import subprocess
import sys
import unittest
from pathlib import Path


class IndependenciaTests(unittest.TestCase):
    def test_motor_sin_qt_y_generacion_reproducible(self):
        programa = '''
import sys
from simulacion.motor import MotorSimulacion
a, b = MotorSimulacion(seed=42), MotorSimulacion(seed=42)
for _ in range(5):
    assert a.agregar_aleatorio() == b.agregar_aleatorio()
while a.hay_trabajo:
    a.paso()
while b.hay_trabajo:
    b.paso()
assert a.reloj == b.reloj
assert a.linea.segmentos == b.linea.segmentos
assert a.extraer_eventos() == b.extraer_eventos()
assert not any(n.startswith(('PySide6', 'interfaz', 'aplicacion')) for n in sys.modules)
'''
        resultado = subprocess.run(
            [sys.executable, '-c', programa], cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
