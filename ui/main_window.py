"""Tablero de simulación: controles, colas y análisis de la ejecución."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
    QSplitter, QTabWidget, QVBoxLayout, QWidget)
from core import scheduler
from core.simulation import Simulation
from utils.random_generator import datos_aleatorios
from .widgets import bcp_campos
from .widgets.bcp_panel import BcpPanel
from .widgets.bcp_table import BcpTable
from .widgets.cpu_panel import CpuPanel
from .widgets.gantt_view import GanttView
from .widgets.process_form import ProcessForm
from .widgets.queue_panel import QueuePanel
from .widgets.summary import Summary
from .widgets.toolbar import Toolbar

class MainWindow(QMainWindow):
    def __init__(self, sim: Simulation | None = None):
        super().__init__()
        self.setWindowTitle("Gestor de procesos · PMA-QMG-P")
        self.resize(1440, 960)
        self.setMinimumSize(1100, 820)
        self.sim = sim or Simulation(self)
        self._sel = None
        root = QWidget()
        root.setObjectName("Root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 18, 22, 8)
        layout.setSpacing(14)
        header = QHBoxLayout()
        brand = QLabel("P/")
        brand.setObjectName("Brand")
        brand.setAlignment(Qt.AlignCenter)
        brand.setFixedSize(48, 48)
        header.addWidget(brand)
        titles = QVBoxLayout()
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
        layout.addLayout(header)
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
        self.gantt = GanttView(self.sim.linea, self.sim.buscar)
        self.gantt.setMinimumHeight(150)
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
        dashboard.setSizes([215, 265, 200])
        dashboard.setStretchFactor(1, 1)
        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)
        body.addWidget(self.sidebar)
        body.addWidget(dashboard)
        body.setSizes([280, 1080])
        body.setStretchFactor(1, 1)
        layout.addWidget(body, 1)
        self.setCentralWidget(root)
        self.statusBar().showMessage("Listo para simular. Agrega un proceso o genera uno aleatorio.")

        t = self.toolbar
        t.alternar_form.connect(lambda: self.sidebar.setVisible(t._form.isChecked()))
        t.iniciar.connect(self._iniciar)
        t.pausar.connect(self._pausar)
        t.paso.connect(self.sim.paso)
        t.reiniciar.connect(self.sim.reiniciar)
        t.rata_cambiada.connect(self.sim.set_rata)
        t.velocidad_cambiada.connect(self.sim.set_velocidad)
        self.form.enviar.connect(self._agregar)
        self.form.aleatorio.connect(self._agregar_aleatorio)
        for w in (self.preparados, self.suspendidos, self.terminados, self.tabla_preparados, self.tabla_suspendidos):
            w.seleccionado.connect(self._seleccionar)
        self.sim.cambio.connect(self._refrescar)
        self.sim.reiniciado.connect(self._al_reiniciar)
        self.sim.evento.connect(self._evento)
        self._refrescar()

    def _agregar(self):
        p = self.sim.agregar_proceso(**self.form.datos())
        self._seleccionar(p.pid)
        self.form.limpiar()

    def _agregar_aleatorio(self):
        p = self.sim.agregar_proceso(self.form.nombre(), **datos_aleatorios())
        self._seleccionar(p.pid)
        self.form.limpiar()

    def _iniciar(self):
        self.sim.iniciar()
        self._refrescar()

    def _pausar(self):
        self.sim.pausar()
        self._refrescar()

    def _seleccionar(self, pid):
        self._sel = pid
        self._refrescar()

    def _al_reiniciar(self):
        self._sel = None
        self.eventos.clear()

    def _evento(self, msg):
        self.eventos.appendPlainText(msg)
        self.statusBar().showMessage(msg)

    def _refrescar(self):
        s = self.sim
        preparados = sorted(s.preparados, key=scheduler.clave_orden)
        self.preparados.actualizar(preparados, self._sel)
        self.suspendidos.actualizar(s.suspendidos, self._sel)
        self.terminados.actualizar(s.terminados, self._sel)
        for i, (title, queue) in enumerate([("Listos", preparados), ("E/S", s.suspendidos), ("Fin", s.terminados)]):
            self.colas.setTabText(i, f"{title} · {len(queue)}")
        self.cpu.actualizar(s.en_cpu)
        self.bcp_ejecucion.actualizar(s.en_cpu)
        self.bcp_seleccionado.actualizar(s.buscar(self._sel) if self._sel is not None else None)
        self.tabla_preparados.actualizar(preparados)
        self.tabla_suspendidos.actualizar(s.suspendidos)
        self.gantt.refrescar(s.reloj)
        self.summary.actualizar(s)
        hay_trabajo = bool(s.en_cpu or s.preparados or s.suspendidos)
        self.toolbar.set_corriendo(s.corriendo, hay_trabajo)
        self.estado.setText("●  En curso" if s.corriendo else "●  En pausa" if hay_trabajo else "✓  Completado" if s.terminados else "●  Sin procesos")
