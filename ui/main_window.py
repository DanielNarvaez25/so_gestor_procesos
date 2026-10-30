"""Ventana principal: arma los paneles y los conecta con la simulación."""
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

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
from .widgets.toolbar import Toolbar


class MainWindow(QMainWindow):
    def __init__(self, sim: Simulation | None = None):
        super().__init__()
        self.setWindowTitle("Gestor de procesos")
        self.resize(1400, 900)
        self.sim = sim or Simulation(self)
        self._sel: int | None = None    # pid del proceso seleccionado

        # ---- widgets ----
        self.toolbar = Toolbar()
        self.form = ProcessForm()
        self.preparados = QueuePanel("PREPARADOS", "Sin procesos preparados")
        self.ejecucion = QueuePanel("EJECUCIÓN (CPU)", "CPU libre", conteo=False)
        self.suspendidos = QueuePanel("SUSPENDIDOS", "Sin procesos suspendidos")
        self.cpu = CpuPanel()
        self.gantt = GanttView(self.sim.linea, self.sim.buscar)
        self.bcp_ejecucion = BcpPanel("BCP (EJECUCIÓN)", bcp_campos.EJECUCION)
        self.bcp_seleccionado = BcpPanel("BCP (SELECCIONADO)", bcp_campos.SELECCIONADO, columnas=2)
        #self.tabla_preparados = BcpTable("BCP PREPARADOS", bcp_campos.TABLA_PREPARADOS)
        #self.tabla_suspendidos = BcpTable("BCP SUSPENDIDOS", bcp_campos.TABLA_SUSPENDIDOS)

        self.form.setFixedWidth(230)
        self.bcp_ejecucion.setFixedWidth(250)
        for q in (self.preparados, self.ejecucion, self.suspendidos):
            q.setMinimumHeight(110)
        self.ejecucion.setMaximumHeight(130)
        #self.tabla_preparados.setMinimumHeight(170)
        #self.tabla_suspendidos.setMinimumHeight(170)

        # ---- distribución ----
        colas = QVBoxLayout()
        colas.addWidget(self.preparados, 3)
        colas.addWidget(self.ejecucion, 1)
        colas.addWidget(self.suspendidos, 2)

        centro = QGridLayout()
        centro.addWidget(self.cpu, 0, 0)
        centro.addWidget(self.gantt, 1, 0)
        centro.addWidget(self.bcp_ejecucion, 0, 1, 2, 1)
        centro.addWidget(self.bcp_seleccionado, 2, 0, 1, 2)
        centro.setRowStretch(1, 1)

        cuerpo = QHBoxLayout()
        cuerpo.addWidget(self.form)
        cuerpo.addLayout(colas, 1)
        cuerpo.addLayout(centro, 3)

        tablas = QHBoxLayout()
        #tablas.addWidget(self.tabla_preparados)
        #tablas.addWidget(self.tabla_suspendidos)

        raiz = QWidget()
        raiz.setObjectName("Root")
        principal = QVBoxLayout(raiz)
        principal.addWidget(self.toolbar)
        principal.addLayout(cuerpo, 1)
        principal.addLayout(tablas)
        self.setCentralWidget(raiz)

        # ---- conexiones ----
        t = self.toolbar
        t.alternar_form.connect(lambda: self.form.setVisible(not self.form.isVisible()))
        t.agregar.connect(self._agregar)
        t.iniciar.connect(self._iniciar)
        t.pausar.connect(self._pausar)
        t.reiniciar.connect(self.sim.reiniciar)
        t.rata_cambiada.connect(self.sim.set_rata)
        self.form.enviar.connect(self._agregar)
        self.form.aleatorio.connect(self._agregar_aleatorio)
        for w in (self.preparados, self.ejecucion, self.suspendidos,
                  ):
            w.seleccionado.connect(self._seleccionar)
#self.tabla_preparados, self.tabla_suspendidos
        self.sim.cambio.connect(self._refrescar)
        self.sim.reiniciado.connect(self._al_reiniciar)
        self.sim.evento.connect(lambda msg: self.statusBar().showMessage(msg))
        self._refrescar()

    # ---------- acciones ----------
    def _agregar(self):
        p = self.sim.agregar_proceso(self.form.nombre(), self.form.prioridad())
        self._sel = p.pid
        self.form.limpiar()
        self._refrescar()

    def _agregar_aleatorio(self):
        p = self.sim.agregar_proceso(self.form.nombre(), **datos_aleatorios())
        self._sel = p.pid
        self.form.limpiar()
        self._refrescar()

    def _iniciar(self):
        self.sim.iniciar()
        self.toolbar.set_corriendo(True)

    def _pausar(self):
        self.sim.pausar()
        self.toolbar.set_corriendo(False)

    def _seleccionar(self, pid: int):
        self._sel = pid
        self._refrescar()

    def _al_reiniciar(self):
        self._sel = None
        self.toolbar.set_corriendo(False)

    # ---------- refresco ----------
    def _refrescar(self):
        s = self.sim
        preparados = sorted(s.preparados, key=scheduler.clave_orden)   # el primero es el próximo en CPU
        en_cpu = [s.en_cpu] if s.en_cpu else []

        self.preparados.actualizar(preparados, self._sel)
        self.ejecucion.actualizar(en_cpu, self._sel)
        self.suspendidos.actualizar(s.suspendidos, self._sel)
        self.cpu.actualizar(s.en_cpu)
        self.bcp_ejecucion.actualizar(s.en_cpu)
        self.bcp_seleccionado.actualizar(s.buscar(self._sel) if self._sel is not None else None)
        #self.tabla_preparados.actualizar(preparados)
        #self.tabla_suspendidos.actualizar(s.suspendidos)
        self.gantt.refrescar(s.reloj)
