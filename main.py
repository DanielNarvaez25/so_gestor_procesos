import sys

from PySide6.QtWidgets import QApplication

from aplicacion.controlador import ControladorSimulacion
from simulacion.motor import MotorSimulacion
from interfaz.ventana_principal import VentanaPrincipal
from interfaz.estilos.tema import aplicar_tema


def main():
    aplicacion = QApplication(sys.argv)
    aplicar_tema(aplicacion)
    motor = MotorSimulacion()
    controlador = ControladorSimulacion(motor=motor)
    ventana = VentanaPrincipal(controlador)
    ventana.show()
    sys.exit(aplicacion.exec())


if __name__ == "__main__":
    main()
