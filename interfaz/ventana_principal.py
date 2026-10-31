"""Tablero de simulación: controles, colas y análisis de la ejecución."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow,
    QSplitter, QTabWidget, QVBoxLayout, QWidget, QScrollArea)
from aplicacion.controlador import ControladorSimulacion
from .componentes import bcp_campos
from .componentes.panel_bcp import PanelBcp
from .componentes.panel_cpu import PanelCpu
from .componentes.grafico_gantt import HistorialCpu
from .componentes.formulario_proceso import FormularioProceso
from .componentes.panel_colas import PanelColas
from .componentes.resumen import ResumenSimulacion
from .componentes.barra_controles import BarraControles

class VentanaPrincipal(QMainWindow):
    def __init__(self, controlador: ControladorSimulacion | None = None):
        super().__init__()
        self.setWindowTitle("Gestor de procesos · PMA-QMG-P")
        self.resize(1440, 1040)
        self.setMinimumSize(1100, 820)
        self.controlador = controlador or ControladorSimulacion(self)
        contenedor_principal = QWidget()
        contenedor_principal.setObjectName("Root")
        distribucion_principal = QVBoxLayout(contenedor_principal)
        distribucion_principal.setContentsMargins(22, 18, 22, 8)
        distribucion_principal.setSpacing(14)
        distribucion_principal.addWidget(self._crear_cabecera())
        self.barra_controles = BarraControles()
        distribucion_principal.addWidget(self.barra_controles)
        self.resumen = ResumenSimulacion()
        distribucion_principal.addWidget(self.resumen)

        self._crear_panel_lateral()
        divisor_vertical = self._crear_panel_ejecucion()
        divisor_horizontal = QSplitter(Qt.Horizontal)
        divisor_horizontal.setChildrenCollapsible(False)
        divisor_horizontal.addWidget(self.panel_lateral)
        divisor_horizontal.addWidget(divisor_vertical)
        divisor_horizontal.setSizes([280, 1080])
        divisor_horizontal.setStretchFactor(1, 1)
        distribucion_principal.addWidget(divisor_horizontal, 1)
        contenedor_principal.setMinimumHeight(960)
        pagina = QScrollArea()
        pagina.setWidgetResizable(True)
        pagina.setWidget(contenedor_principal)
        self.setCentralWidget(pagina)
        self.statusBar().showMessage("Listo para simular. Agrega un proceso o genera uno aleatorio.")

        self.controlador.conectar_vista(self)

    def _crear_cabecera(self) -> QWidget:
        """Construye el título y la etiqueta del estado de la simulación."""
        cabecera = QWidget()
        cabecera.setObjectName("Hero")
        distribucion_cabecera = QHBoxLayout(cabecera)
        distribucion_cabecera.setContentsMargins(20, 16, 20, 16)
        etiqueta_marca = QLabel("P/")
        etiqueta_marca.setObjectName("Brand")
        etiqueta_marca.setAlignment(Qt.AlignCenter)
        etiqueta_marca.setFixedSize(48, 48)
        distribucion_cabecera.addWidget(etiqueta_marca)
        distribucion_titulos = QVBoxLayout()
        etiqueta_laboratorio = QLabel("LABORATORIO DE SISTEMAS OPERATIVOS")
        etiqueta_laboratorio.setObjectName("Eyebrow")
        distribucion_titulos.addWidget(etiqueta_laboratorio)
        distribucion_titulos.setSpacing(2)
        titulo = QLabel("Gestor de procesos")
        titulo.setObjectName("Title")
        subtitulo = QLabel("PMA-QMG-P  /  Prioridad → Quantum → Orden de llegada")
        subtitulo.setObjectName("Muted")
        distribucion_titulos.addWidget(titulo)
        distribucion_titulos.addWidget(subtitulo)
        distribucion_cabecera.addLayout(distribucion_titulos)
        distribucion_cabecera.addStretch()
        self.estado = QLabel()
        self.estado.setObjectName("State")
        distribucion_cabecera.addWidget(self.estado)
        return cabecera

    def _crear_panel_lateral(self) -> QWidget:
        """Agrupa el formulario y las pestañas de procesos por estado."""
        self.panel_lateral = QWidget()
        distribucion_panel_lateral = QVBoxLayout(self.panel_lateral)
        distribucion_panel_lateral.setContentsMargins(0, 0, 0, 0)
        distribucion_panel_lateral.setSpacing(12)
        self.formulario = FormularioProceso()
        distribucion_panel_lateral.addWidget(self.formulario)
        self.preparados = PanelColas("EN ESPERA DE CPU", "Agrega un proceso para comenzar.")
        self.suspendidos = PanelColas("ESPERANDO E/S", "No hay procesos bloqueados.")
        self.terminados = PanelColas("FINALIZADOS", "Los procesos terminados aparecerán aquí.")
        self.colas = QTabWidget()
        for panel, titulo in [(self.preparados, "Listos"), (self.suspendidos, "E/S"), (self.terminados, "Fin")]:
            self.colas.addTab(panel, titulo)
        distribucion_panel_lateral.addWidget(self.colas, 1)
        self.panel_lateral.setMinimumWidth(270)

        return self.panel_lateral

    def _crear_panel_ejecucion(self) -> QSplitter:
        """Coloca el proceso actual y su BCP encima del historial de CPU."""
        self.cpu = PanelCpu()
        self.cpu.setMinimumHeight(215)
        self.bcp_ejecucion = PanelBcp("BCP · EN CPU", bcp_campos.EJECUCION)
        contenedor_cpu = QWidget()
        distribucion_cpu = QHBoxLayout(contenedor_cpu)
        distribucion_cpu.setContentsMargins(0, 0, 0, 0)
        distribucion_cpu.setSpacing(12)
        distribucion_cpu.addWidget(self.cpu, 3)
        distribucion_cpu.addWidget(self.bcp_ejecucion, 2)
        self.historial_cpu = HistorialCpu(self.controlador.motor.linea, self.controlador.motor.buscar)
        self.historial_cpu.setMinimumHeight(360)
        divisor_vertical = QSplitter(Qt.Vertical)
        divisor_vertical.setChildrenCollapsible(False)
        for componente in (contenedor_cpu, self.historial_cpu):
            divisor_vertical.addWidget(componente)
        divisor_vertical.setSizes([230, 480])
        divisor_vertical.setStretchFactor(0, 0)
        divisor_vertical.setStretchFactor(1, 1)
        return divisor_vertical

    def mostrar(self, motor, seleccion, corriendo):
        preparados = motor.preparados_ordenados()
        self.preparados.actualizar(preparados, seleccion)
        self.suspendidos.actualizar(motor.suspendidos, seleccion)
        self.terminados.actualizar(motor.terminados, seleccion)
        for indice_pestana, (titulo, procesos) in enumerate([("Listos", preparados), ("E/S", motor.suspendidos), ("Fin", motor.terminados)]):
            self.colas.setTabText(indice_pestana, f"{titulo} · {len(procesos)}")
        # Con la CPU libre mostramos el primer preparado sin asignarle un turno.
        proceso_mostrado = motor.en_cpu
        vista_previa = False
        if proceso_mostrado is None:
            if len(preparados) > 0:
                proceso_mostrado = preparados[0]
                vista_previa = True

        self.cpu.actualizar(proceso_mostrado, vista_previa)
        if vista_previa:
            self.bcp_ejecucion.set_titulo("BCP · PRÓXIMO PROCESO")
        else:
            self.bcp_ejecucion.set_titulo("BCP · EN CPU")
        self.bcp_ejecucion.actualizar(proceso_mostrado)
        self.historial_cpu.refrescar(motor.reloj)
        self.resumen.actualizar(motor)
        hay_trabajo = motor.hay_trabajo
        self.barra_controles.set_corriendo(corriendo, hay_trabajo)
        if corriendo:
            texto_estado = "●  En curso"
        elif hay_trabajo:
            texto_estado = "●  En pausa"
        elif motor.terminados:
            texto_estado = "✓  Completado"
        else:
            texto_estado = "●  Sin procesos"
        self.estado.setText(texto_estado)

    def limpiar_eventos(self):
        self.statusBar().clearMessage()

    def mostrar_evento(self, mensaje):
        self.statusBar().showMessage(mensaje)
