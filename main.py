import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.theme import aplicar_tema


def main():
    app = QApplication(sys.argv)
    aplicar_tema(app)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
