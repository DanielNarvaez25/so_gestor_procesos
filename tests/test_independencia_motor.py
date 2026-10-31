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
primer_motor, segundo_motor = MotorSimulacion(seed=42), MotorSimulacion(seed=42)
for _ in range(5):
    assert primer_motor.agregar_aleatorio() == segundo_motor.agregar_aleatorio()
while primer_motor.hay_trabajo:
    primer_motor.paso()
while segundo_motor.hay_trabajo:
    segundo_motor.paso()
assert primer_motor.reloj == segundo_motor.reloj
assert primer_motor.linea.segmentos == segundo_motor.linea.segmentos
assert primer_motor.extraer_eventos() == segundo_motor.extraer_eventos()
assert not any(nombre_modulo.startswith(('PySide6', 'interfaz', 'aplicacion')) for nombre_modulo in sys.modules)
'''
        resultado = subprocess.run(
            [sys.executable, '-c', programa], cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
