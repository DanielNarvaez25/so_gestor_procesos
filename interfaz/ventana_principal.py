"""Tablero de simulación: controles, colas y análisis de la ejecución."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
    QSplitter, QTabWidget, QVBoxLayout, QWidget, QScrollArea)
from aplicacion.controlador import ControladorSimulacion
from .componentes import bcp_campos
from .componentes.panel_bcp import BcpPanel
from .componentes.tabla_bcp import BcpTable
from .componentes.panel_cpu import CpuPanel
from .componentes.grafico_gantt import GanttView
from .componentes.formulario_proceso import ProcessForm
from .componentes.panel_colas import QueuePanel
from .componentes.resumen import Summary
from .componentes.barra_controles import Toolbar

class VentanaPrincipal(QMainWindow):
    def __init__(self, controlador: ControladorSimulacion | None = None):
        super().__init__()
        self.setWindowTitle("Gestor de procesos · PMA-QMG-P")
        self.resize(1440, 1040)
        self.setMinimumSize(1100, 820)
        self.controlador = controlador or ControladorSimulacion(self)
        root = QWidget()
        root.setObjectName("Root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 18, 22, 8)
        layout.setSpacing(14)
        hero = QWidget()
        hero.setObjectName("Hero")
        header = QHBoxLayout(hero)
        header.setContentsMargins(20, 16, 20, 16)
        brand = QLabel("P/")
        brand.setObjectName("Brand")
        brand.setAlignment(Qt.AlignCenter)
        brand.setFixedSize(48, 48)
        header.addWidget(brand)
        titles = QVBoxLayout()
        eyebrow = QLabel("LABORATORIO DE SISTEMAS OPERATIVOS")
        eyebrow.setObjectName("Eyebrow")
        titles.addWidget(eyebrow)
        titles.setSpacing(2)
        title = QLabel("Gestor de procesos")
        title.setObjectName("Title")
        subtitle = QLabel("PMA-QMG-P  /  Prioridad → Quantum → Orden de llegada")
        subtitle.setObjectName("Muted")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        self.estado = QLabel()
        self.estado.setObjectName("State")
        header.addWidget(self.estado)
        layout.addWidget(hero)
        self.toolbar = Toolbar()
        layout.addWidget(self.toolbar)
        self.summary = Summary()
        layout.addWidget(self.summary)

        self.sidebar = QWidget()
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        self.form = ProcessForm()
        side.addWidget(self.form)
        self.preparados = QueuePanel("EN ESPERA DE CPU", "Agrega un proceso para comenzar.")
        self.suspendidos = QueuePanel("ESPERANDO E/S", "No hay procesos bloqueados.")
        self.terminados = QueuePanel("FINALIZADOS", "Los procesos terminados aparecerán aquí.")
        self.colas = QTabWidget()
        for panel, title in [(self.preparados, "Listos"), (self.suspendidos, "E/S"), (self.terminados, "Fin")]:
            self.colas.addTab(panel, title)
        side.addWidget(self.colas, 1)
        self.sidebar.setMinimumWidth(270)

        self.cpu = CpuPanel()
        self.cpu.setMinimumHeight(215)
        self.bcp_ejecucion = BcpPanel("BCP · EN CPU", bcp_campos.EJECUCION)
        cpu_row = QWidget()
        cpu_layout = QHBoxLayout(cpu_row)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        cpu_layout.setSpacing(12)
        cpu_layout.addWidget(self.cpu, 3)
        cpu_layout.addWidget(self.bcp_ejecucion, 2)
        self.gantt = GanttView(self.controlador.motor.linea, self.controlador.motor.buscar)
        self.gantt.setMinimumHeight(240)
        self.bcp_seleccionado = BcpPanel("DETALLE DEL PROCESO SELECCIONADO", bcp_campos.SELECCIONADO, columnas=3)
        self.tabla_preparados = BcpTable("BCP · PREPARADOS", bcp_campos.TABLA_PREPARADOS)
        self.tabla_suspendidos = BcpTable("BCP · SUSPENDIDOS", bcp_campos.TABLA_SUSPENDIDOS)
        self.eventos = QPlainTextEdit()
        self.eventos.setReadOnly(True)
        self.eventos.setMaximumBlockCount(1000)
        self.eventos.setPlaceholderText("Aquí verás las decisiones del planificador y los cambios de estado.")
        self.detalles = QTabWidget()
        for panel, title in [(self.bcp_seleccionado, "Inspector"), (self.tabla_preparados, "BCP preparados"),
                             (self.tabla_suspendidos, "BCP suspendidos"), (self.eventos, "Eventos")]:
            self.detalles.addTab(panel, title)
        self.detalles.setMinimumHeight(155)
        dashboard = QSplitter(Qt.Vertical)
        dashboard.setChildrenCollapsible(False)
        for widget in (cpu_row, self.gantt, self.detalles):
            dashboard.addWidget(widget)
        dashboard.setSizes([230, 290, 190])
        dashboard.setStretchFactor(1, 1)
        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)
        body.addWidget(self.sidebar)
        body.addWidget(dashboard)
        body.setSizes([280, 1080])
        body.setStretchFactor(1, 1)
        layout.addWidget(body, 1)
        root.setMinimumHeight(960)
        pagina = QScrollArea()
        pagina.setWidgetResizable(True)
        pagina.setWidget(root)
        self.setCentralWidget(pagina)
        self.statusBar().showMessage("Listo para simular. Agrega un proceso o genera uno aleatorio.")

        self.controlador.conectar_vista(self)

    def mostrar(self, s, seleccion, corriendo):
        preparados = s.preparados_ordenados()
        self.preparados.actualizar(preparados, seleccion)
        self.suspendidos.actualizar(s.suspendidos, seleccion)
        self.terminados.actualizar(s.terminados, seleccion)
        for i, (title, queue) in enumerate([("Listos", preparados), ("E/S", s.suspendidos), ("Fin", s.terminados)]):
            self.colas.setTabText(i, f"{title} · {len(queue)}")
        self.cpu.actualizar(s.en_cpu)
        self.bcp_ejecucion.actualizar(s.en_cpu)
        self.bcp_seleccionado.actualizar(s.buscar(seleccion) if seleccion is not None else None)
        self.tabla_preparados.actualizar(preparados)
        self.tabla_suspendidos.actualizar(s.suspendidos)
        self.gantt.refrescar(s.reloj)
        self.summary.actualizar(s)
        hay_trabajo = bool(s.en_cpu or s.preparados or s.suspendidos)
        self.toolbar.set_corriendo(corriendo, hay_trabajo)
        self.estado.setText("●  En curso" if corriendo else "●  En pausa" if hay_trabajo else "✓  Completado" if s.terminados else "●  Sin procesos")

    def limpiar_eventos(self):
        self.eventos.clear()

    def mostrar_evento(self, mensaje):
        self.eventos.appendPlainText(mensaje)
        self.statusBar().showMessage(mensaje)
