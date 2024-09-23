import os  # @Reimport
import sys
from datetime import datetime

import numpy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from networkx.drawing.nx_pylab import draw_networkx_edges
from PySide6.QtCore import SIGNAL, QEvent, QRect, QSize, QThread
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMenu, QMessageBox

from pydistsim import Simulation
from pydistsim.algorithm import NodeAlgorithm
from pydistsim.algorithm.base_algorithm import BaseAlgorithm
from pydistsim.observers import AlgorithmObserver, SimulationObserver
from pydistsim.utils.npickle import read_pickle, write_pickle

try:
    from .dictionarytreemodel import DictionaryTreeModel
    from .simulationui import Ui_SimulationWindow
except ImportError:
    from pydistsim.gui.dictionarytreemodel import DictionaryTreeModel
    from pydistsim.gui.simulationui import Ui_SimulationWindow

from copy import deepcopy

from pydistsim import logger
from pydistsim.gui.drawing import draw_current_state
from pydistsim.utils.localization.helpers import align_clusters, get_rms
from pydistsim.utils.memory.positions import Positions


class QThreadObserver(AlgorithmObserver, SimulationObserver):
    def __init__(self, q_thread: QThread, *args, **kwargs) -> None:
        self.q_thread = q_thread
        super().__init__(*args, **kwargs)

    def on_step_done(self, algorithm: "BaseAlgorithm") -> None:
        self.q_thread.emit(
            SIGNAL("updateLog(QString)"),
            "[{}] Step {} finished",
            algorithm.name,
            algorithm.simulation.algorithmState["step"],
        )

    def on_state_changed(self, simulation: Simulation) -> None:
        self.q_thread.emit(SIGNAL("redraw()"))

    def on_algorithm_finished(self, algorithm: "BaseAlgorithm") -> None:
        self.q_thread.emit(SIGNAL("updateLog(QString)"), "[%s] Algorithm finished" % (algorithm.name))

    def on_network_changed(self, simulation: Simulation) -> None:
        self.q_thread.emit(SIGNAL("updateLog(QString)"), "Network loaded")
        self.q_thread.emit(SIGNAL("redraw()"))


class SimulationThread(Simulation, QThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_observers(QThreadObserver(self))

    def __del__(self):
        self.exiting = True
        self.wait()


class SimulationGui(QMainWindow):
    def __init__(self, net=None, parent=None, fname=None):
        super().__init__()

        self.ui = Ui_SimulationWindow()
        self.ui.setupUi(self)

        if fname:
            self.set_title(fname)

        # context menu
        self.ui.nodeInspector.addAction(self.ui.actionCopyInspectorData)
        self.ui.nodeInspector.addAction(self.ui.actionShowLocalizedSubclusters)
        # callbacks
        self.ui.actionCopyInspectorData.triggered.connect(self.on_actionCopyInspectorData_triggered)
        self.ui.actionShowLocalizedSubclusters.triggered.connect(self.on_actionShowLocalizedSubclusters_triggered)

        self.dpi = 72
        # take size of networDisplayWidget
        self.fig = Figure((700 / self.dpi, 731 / self.dpi), self.dpi, facecolor="0.9")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.networkDisplayWidget)
        self.nav = NavigationToolbar(self.canvas, self.ui.networkDisplayWidget, coordinates=True)
        self.nav.setGeometry(QRect(0, 0, 651, 36))
        self.nav.setIconSize(QSize(24, 24))

        self.axes = self.fig.add_subplot(111)
        # matplotlib.org/api/figure_api.html#matplotlib.figure.SubplotParams
        self.fig.subplots_adjust(left=0.03, right=0.99, top=0.92)

        if net:
            self.init_sim(net)

        self.connect(self.ui.showNodes, SIGNAL("stateChanged(int)"), self.refresh_visibility)
        self.connect(self.ui.showEdges, SIGNAL("stateChanged(int)"), self.refresh_visibility)
        self.connect(self.ui.showMessages, SIGNAL("stateChanged(int)"), self.refresh_visibility)
        self.connect(self.ui.showLabels, SIGNAL("stateChanged(int)"), self.refresh_visibility)
        self.connect(self.ui.redrawNetworkButton, SIGNAL("clicked(bool)"), self.redraw)
        self.connect(self.ui.treeGroupBox, SIGNAL("toggled(bool)"), self.refresh_visibility)
        self.connect(self.ui.tree_key, SIGNAL("textEdited(QString)"), self.redraw)
        self.connect(self.ui.propagationError, SIGNAL("toggled(bool)"), self.refresh_visibility)
        self.connect(self.ui.locKey, SIGNAL("textEdited(QString)"), self.redraw)
        # callbacks
        self.ui.actionOpenNetwork.triggered.connect(self.on_actionOpenNetwork_triggered)
        self.ui.actionSaveNetwork.triggered.connect(self.on_actionSaveNetwork_triggered)
        self.ui.actionRun.triggered.connect(self.on_actionRun_triggered)
        self.ui.actionStep.triggered.connect(self.on_actionStep_triggered)
        self.ui.actionReset.triggered.connect(self.on_actionReset_triggered)

        self.canvas.mpl_connect("pick_event", self.on_pick)

    def handleInspectorMenu(self, pos):
        menu = QMenu()
        menu.addAction("Add")
        menu.addAction("Delete")
        menu.exec_(QCursor.pos())

    def init_sim(self, net):
        self.net = net
        self.sim = Simulation(net)
        self.connect(self.sim, SIGNAL("redraw()"), self.redraw)
        self.connect(self.sim, SIGNAL("updateLog(QString)"), self.update_log)
        self.redraw()

    def update_log(self, text):
        """Add item to list widget"""
        logger.debug("Added item to list widget: " + text)
        self.ui.logListWidget.insertItem(0, text)
        # self.ui.logListWidget.sortItems()

    def redraw(self):
        self.refresh_network_inspector()
        self.draw_network()
        self.reset_zoom()
        self.refresh_visibility()

    def draw_network(self):
        draw_current_state(
            self.sim, self.axes, clear=True, tree_key=self.ui.tree_key.text(), locKey=self.ui.locKey.text()
        )

    def refresh_visibility(self):
        try:
            self.node_collection.set_visible(self.ui.showNodes.isChecked())
            self.edge_collection.set_visible(self.ui.showEdges.isChecked())
            for label in list(self.label_collection.values()):
                label.set_visible(self.ui.showLabels.isChecked())
            self.tree_collection.set_visible(self.ui.treeGroupBox.isChecked())
            self.ini_error_collection.set_visible(self.ui.propagationError.isChecked())
            self.propagation_error_collection.set_visible(self.ui.propagationError.isChecked())
            # sould be last, sometimes there are no messages
            self.message_collection.set_visible(self.ui.showMessages.isChecked())
        except AttributeError:
            logger.warning("Refresh visibility warning.")
        self.canvas.draw()

    def reset_zoom(self):
        self.axes.set_xlim((0, self.net.environment.image.shape[1]))
        self.axes.set_ylim((0, self.net.environment.image.shape[0]))

    def set_title(self, fname):
        new = " - ".join([str(self.windowTitle()).split(" - ")[0], str(fname)])
        self.setWindowTitle(new)

    def refresh_network_inspector(self):
        niModel = DictionaryTreeModel(dic=self.net.get_dic())
        self.ui.networkInspector.setModel(niModel)
        self.ui.networkInspector.expandToDepth(0)

    """
    Callbacks
    """

    def on_actionRun_triggered(self):
        self.ui.logListWidget.clear()
        logger.debug("running on_actionRun_triggered")
        self.sim.stepping = True
        self.sim.run()

    def on_actionStep_triggered(self):
        logger.debug("running on_actionStep_triggered")
        self.sim.run(self.ui.stepSize.value())

    def on_actionReset_triggered(self):
        logger.debug("running on_actionReset_triggered")
        self.sim.reset()
        self.redraw()

    def on_actionCopyInspectorData_triggered(self):
        string = "Node inspector data\n-------------------"
        # raise()
        for qModelIndex in self.ui.nodeInspector.selectedIndexes():
            string += "\n" + qModelIndex.internalPointer().toString("    ")

        clipboard = app.clipboard()
        clipboard.setText(string)
        event = QEvent(QEvent.Clipboard)
        app.sendEvent(clipboard, event)

    def on_actionShowLocalizedSubclusters_triggered(self):
        if len(self.ui.nodeInspector.selectedIndexes()) == 1:
            qModelIndex = self.ui.nodeInspector.selectedIndexes()[0]
            treeItem = qModelIndex.internalPointer()
            assert isinstance(treeItem.itemDataValue, Positions)

            estimated = deepcopy(treeItem.itemDataValue)
            estimatedsub = estimated.subclusters[0]
            # rotate, translate and optionally scale
            # w.r.t. original positions (pos)
            align_clusters(Positions.create(self.net.pos), estimated, True)
            net = self.net.subnetwork(list(estimatedsub.keys()), pos=estimatedsub)

            self.draw_network(net=net, drawMessages=False)

            edge_pos = numpy.asarray([(self.net.pos[node], estimatedsub[node][:2]) for node in net])
            error_collection = LineCollection(edge_pos, colors="r")
            self.axes.add_collection(error_collection)

            rms = get_rms(self.net.pos, estimated, scale=False)
            self.update_log("rms = %.3f" % rms)
            self.update_log(
                "localized = %.2f%% (%d/%d)"
                % (
                    len(estimatedsub) * 1.0 / len(self.net.pos) * 100,
                    len(estimatedsub),
                    len(self.net.pos),
                )
            )

    def on_actionSaveNetwork_triggered(self, *args):
        default_filetype = "gz"
        start = datetime.now().strftime("%Y%m%d") + default_filetype

        filters = ["Network pickle (*.gz)", "All files (*)"]
        selectedFilter = "Network pickle (gz)"
        filters = ";;".join(filters)

        fname = QFileDialog.getSaveFileName(self, "Choose a filename", start, filters, selectedFilter)[0]
        if fname:
            try:
                write_pickle(self.net, fname)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error saving file",
                    str(e),
                    QMessageBox.Ok,
                    QMessageBox.NoButton,
                )
            else:
                self.set_title(fname)

    def on_actionOpenNetwork_triggered(self, *args):
        default_filetype = "gz"
        start = datetime.now().strftime("%Y%m%d") + default_filetype

        filters = ["Network pickle (*.gz)", "All files (*)"]
        selectedFilter = "Network pickle (gz)"
        filters = ";;".join(filters)

        fname = QFileDialog.getOpenFileName(self, "Choose a file to open", start, filters, selectedFilter)[0]
        if fname:
            try:
                logger.debug("opening " + fname)
                net = read_pickle(fname)
                self.init_sim(net)
            except Exception as e:
                logger.exception("Error opening file %s" % str(e))
                QMessageBox.critical(
                    self,
                    "Error opening file",
                    str(e),
                    QMessageBox.Ok,
                    QMessageBox.NoButton,
                )
            else:
                self.set_title(fname)

    def on_pick(self, event):
        if (
            event.artist == self.node_collection
            or event.artist == self.propagation_error_collection
            or event.artist == self.ini_error_collection
        ):
            for ind in event.ind:
                self.on_pick_node(self.drawnNet.nodes()[ind])
        elif event.artist == self.message_collection:
            for ind in event.ind:
                self.on_pick_message(self.messages[ind])
        self.canvas.draw()

    def on_pick_node(self, node):
        niModel = DictionaryTreeModel(dic=node.get_dic())
        # TODO: self.ui.nodeInspectorLabel.setText('Node inspector: node %d' % node._internal_id)
        self.ui.nodeInspector.setModel(niModel)
        self.ui.nodeInspector.expandToDepth(0)

    def on_pick_message(self, message):
        self.ui.logListWidget.insertItem(0, "Pick message %s " % repr(message))


from IPython.lib.guisupport import get_app_qt4, start_event_loop_qt4


def create_window(window_class, **kwargs):
    """Create a QT window in Python, or interactively in IPython with QT GUI
    event loop integration.
    """
    global app

    app = get_app_qt4(sys.argv)
    app.references = set()

    net = None
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if os.path.exists(fname):
            net = read_pickle(fname)
        else:
            QMessageBox.critical(
                None,
                "Error opening file %s",
                fname,
                QMessageBox.Ok,
                QMessageBox.NoButton,
            )

    window = window_class(net, fname)
    app.references.add(window)
    window.show()

    start_event_loop_qt4(app)
    return window


def main():
    global simgui
    simgui = create_window(SimulationGui)
