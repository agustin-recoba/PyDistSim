# Form implementation generated from reading ui file 'E:\Damir\FER\Postdiplomski\Doktorat\Istrazivanje\pymote\pymote\gui\simulation.ui'
#
# Created: Fri Sep 30 12:31:55 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_SimulationWindow:
    def setupUi(self, SimulationWindow):
        SimulationWindow.setObjectName(_fromUtf8("SimulationWindow"))
        SimulationWindow.resize(1106, 800)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(SimulationWindow.sizePolicy().hasHeightForWidth())
        SimulationWindow.setSizePolicy(sizePolicy)
        SimulationWindow.setMinimumSize(QtCore.QSize(1096, 800))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/pymote.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        SimulationWindow.setWindowIcon(icon)
        SimulationWindow.setDockOptions(
            QtGui.QMainWindow.AllowTabbedDocks
            | QtGui.QMainWindow.AnimatedDocks
            | QtGui.QMainWindow.VerticalTabs
        )
        self.centralwidget = QtGui.QWidget(SimulationWindow)
        self.centralwidget.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth()
        )
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.leftWidget = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leftWidget.sizePolicy().hasHeightForWidth())
        self.leftWidget.setSizePolicy(sizePolicy)
        self.leftWidget.setObjectName(_fromUtf8("leftWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.leftWidget)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.controlGroupBox = QtGui.QGroupBox(self.leftWidget)
        self.controlGroupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.controlGroupBox.setObjectName(_fromUtf8("controlGroupBox"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.controlGroupBox)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.widget = QtGui.QWidget(self.controlGroupBox)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.stepSize = QtGui.QSpinBox(self.widget)
        self.stepSize.setAccelerated(True)
        self.stepSize.setMaximum(999)
        self.stepSize.setProperty(_fromUtf8("value"), 1)
        self.stepSize.setObjectName(_fromUtf8("stepSize"))
        self.horizontalLayout_2.addWidget(self.stepSize)
        self.verticalLayout_5.addWidget(self.widget)
        self.verticalLayout_3.addWidget(self.controlGroupBox)
        self.viewGroupBox = QtGui.QGroupBox(self.leftWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewGroupBox.sizePolicy().hasHeightForWidth())
        self.viewGroupBox.setSizePolicy(sizePolicy)
        self.viewGroupBox.setObjectName(_fromUtf8("viewGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.viewGroupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.networkViewGroup = QtGui.QGroupBox(self.viewGroupBox)
        self.networkViewGroup.setObjectName(_fromUtf8("networkViewGroup"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.networkViewGroup)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.showNodes = QtGui.QCheckBox(self.networkViewGroup)
        self.showNodes.setChecked(True)
        self.showNodes.setObjectName(_fromUtf8("showNodes"))
        self.verticalLayout_6.addWidget(self.showNodes)
        self.showEdges = QtGui.QCheckBox(self.networkViewGroup)
        self.showEdges.setChecked(True)
        self.showEdges.setObjectName(_fromUtf8("showEdges"))
        self.verticalLayout_6.addWidget(self.showEdges)
        self.showMessages = QtGui.QCheckBox(self.networkViewGroup)
        self.showMessages.setChecked(True)
        self.showMessages.setObjectName(_fromUtf8("showMessages"))
        self.verticalLayout_6.addWidget(self.showMessages)
        self.showLabels = QtGui.QCheckBox(self.networkViewGroup)
        self.showLabels.setChecked(True)
        self.showLabels.setObjectName(_fromUtf8("showLabels"))
        self.verticalLayout_6.addWidget(self.showLabels)
        self.redrawNetworkButton = QtGui.QPushButton(self.networkViewGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.redrawNetworkButton.sizePolicy().hasHeightForWidth()
        )
        self.redrawNetworkButton.setSizePolicy(sizePolicy)
        self.redrawNetworkButton.setObjectName(_fromUtf8("redrawNetworkButton"))
        self.verticalLayout_6.addWidget(self.redrawNetworkButton)
        self.verticalLayout_2.addWidget(self.networkViewGroup)
        self.treeGroupBox = QtGui.QGroupBox(self.viewGroupBox)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeGroupBox.sizePolicy().hasHeightForWidth())
        self.treeGroupBox.setSizePolicy(sizePolicy)
        self.treeGroupBox.setMinimumSize(QtCore.QSize(132, 60))
        self.treeGroupBox.setFlat(False)
        self.treeGroupBox.setCheckable(True)
        self.treeGroupBox.setChecked(True)
        self.treeGroupBox.setObjectName(_fromUtf8("treeGroupBox"))
        self.treeKey = QtGui.QLineEdit(self.treeGroupBox)
        self.treeKey.setGeometry(QtCore.QRect(42, 20, 71, 20))
        self.treeKey.setFrame(True)
        self.treeKey.setObjectName(_fromUtf8("treeKey"))
        self.label = QtGui.QLabel(self.treeGroupBox)
        self.label.setGeometry(QtCore.QRect(10, 22, 31, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.treeGroupBox)
        self.propagationError = QtGui.QGroupBox(self.viewGroupBox)
        self.propagationError.setMinimumSize(QtCore.QSize(132, 70))
        self.propagationError.setCheckable(True)
        self.propagationError.setObjectName(_fromUtf8("propagationError"))
        self.locKey = QtGui.QLineEdit(self.propagationError)
        self.locKey.setGeometry(QtCore.QRect(10, 40, 111, 20))
        self.locKey.setObjectName(_fromUtf8("locKey"))
        self.label2 = QtGui.QLabel(self.propagationError)
        self.label2.setGeometry(QtCore.QRect(10, 20, 46, 13))
        self.label2.setObjectName(_fromUtf8("label2"))
        self.verticalLayout_2.addWidget(self.propagationError)
        self.verticalLayout_3.addWidget(self.viewGroupBox)
        spacerItem = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding
        )
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.leftWidget)
        spacerItem1 = QtGui.QSpacerItem(
            0, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem1)
        self.networkDisplayWidget = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.networkDisplayWidget.sizePolicy().hasHeightForWidth()
        )
        self.networkDisplayWidget.setSizePolicy(sizePolicy)
        self.networkDisplayWidget.setMinimumSize(QtCore.QSize(650, 0))
        self.networkDisplayWidget.setObjectName(_fromUtf8("networkDisplayWidget"))
        self.horizontalLayout.addWidget(self.networkDisplayWidget)
        spacerItem2 = QtGui.QSpacerItem(
            0, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem2)
        SimulationWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(SimulationWindow)
        self.toolBar.setAutoFillBackground(False)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        SimulationWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.menubar = QtGui.QMenuBar(SimulationWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1106, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSimulation = QtGui.QMenu(self.menubar)
        self.menuSimulation.setObjectName(_fromUtf8("menuSimulation"))
        SimulationWindow.setMenuBar(self.menubar)
        self.dockWidget = QtGui.QDockWidget(SimulationWindow)
        self.dockWidget.setMinimumSize(QtCore.QSize(87, 109))
        self.dockWidget.setFeatures(
            QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable
        )
        self.dockWidget.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dockWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.networkInspector = QtGui.QTreeView(self.dockWidgetContents)
        self.networkInspector.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.networkInspector.setFrameShape(QtGui.QFrame.NoFrame)
        self.networkInspector.setProperty(_fromUtf8("showDropIndicator"), False)
        self.networkInspector.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self.networkInspector.setAnimated(True)
        self.networkInspector.setWordWrap(True)
        self.networkInspector.setHeaderHidden(True)
        self.networkInspector.setObjectName(_fromUtf8("networkInspector"))
        self.horizontalLayout_3.addWidget(self.networkInspector)
        self.dockWidget.setWidget(self.dockWidgetContents)
        SimulationWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget)
        self.dockWidget_2 = QtGui.QDockWidget(SimulationWindow)
        self.dockWidget_2.setMinimumSize(QtCore.QSize(105, 377))
        self.dockWidget_2.setFeatures(
            QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable
        )
        self.dockWidget_2.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.dockWidget_2.setObjectName(_fromUtf8("dockWidget_2"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dockWidgetContents_2.sizePolicy().hasHeightForWidth()
        )
        self.dockWidgetContents_2.setSizePolicy(sizePolicy)
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.nodeInspector = QtGui.QTreeView(self.dockWidgetContents_2)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.nodeInspector.sizePolicy().hasHeightForWidth()
        )
        self.nodeInspector.setSizePolicy(sizePolicy)
        self.nodeInspector.setMinimumSize(QtCore.QSize(87, 337))
        self.nodeInspector.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.nodeInspector.setFrameShape(QtGui.QFrame.NoFrame)
        self.nodeInspector.setProperty(_fromUtf8("showDropIndicator"), False)
        self.nodeInspector.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.nodeInspector.setAnimated(True)
        self.nodeInspector.setWordWrap(True)
        self.nodeInspector.setHeaderHidden(True)
        self.nodeInspector.setObjectName(_fromUtf8("nodeInspector"))
        self.horizontalLayout_4.addWidget(self.nodeInspector)
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        SimulationWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_2)
        self.dockWidget_3 = QtGui.QDockWidget(SimulationWindow)
        self.dockWidget_3.setMinimumSize(QtCore.QSize(87, 109))
        self.dockWidget_3.setFeatures(
            QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable
        )
        self.dockWidget_3.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.dockWidget_3.setObjectName(_fromUtf8("dockWidget_3"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dockWidgetContents_3.sizePolicy().hasHeightForWidth()
        )
        self.dockWidgetContents_3.setSizePolicy(sizePolicy)
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.dockWidgetContents_3)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.logListWidget = QtGui.QListWidget(self.dockWidgetContents_3)
        self.logListWidget.setFrameShape(QtGui.QFrame.NoFrame)
        self.logListWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.logListWidget.setLineWidth(0)
        self.logListWidget.setObjectName(_fromUtf8("logListWidget"))
        self.horizontalLayout_5.addWidget(self.logListWidget)
        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        SimulationWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_3)
        self.actionRun = QtGui.QAction(SimulationWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/player_play.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.actionRun.setIcon(icon1)
        self.actionRun.setObjectName(_fromUtf8("actionRun"))
        self.actionStep = QtGui.QAction(SimulationWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/player_fwd.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.actionStep.setIcon(icon2)
        self.actionStep.setObjectName(_fromUtf8("actionStep"))
        self.actionReset = QtGui.QAction(SimulationWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/player_start.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.actionReset.setIcon(icon3)
        self.actionReset.setObjectName(_fromUtf8("actionReset"))
        self.actionCopyInspectorData = QtGui.QAction(SimulationWindow)
        self.actionCopyInspectorData.setShortcutContext(QtCore.Qt.WidgetShortcut)
        self.actionCopyInspectorData.setObjectName(_fromUtf8("actionCopyInspectorData"))
        self.actionSaveNetwork = QtGui.QAction(SimulationWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/filesaveas.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.actionSaveNetwork.setIcon(icon4)
        self.actionSaveNetwork.setObjectName(_fromUtf8("actionSaveNetwork"))
        self.actionOpenNetwork = QtGui.QAction(SimulationWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/icons/fileopen.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.actionOpenNetwork.setIcon(icon5)
        self.actionOpenNetwork.setObjectName(_fromUtf8("actionOpenNetwork"))
        self.actionShowLocalizedSubclusters = QtGui.QAction(SimulationWindow)
        self.actionShowLocalizedSubclusters.setObjectName(
            _fromUtf8("actionShowLocalizedSubclusters")
        )
        self.toolBar.addAction(self.actionOpenNetwork)
        self.toolBar.addAction(self.actionSaveNetwork)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRun)
        self.toolBar.addAction(self.actionStep)
        self.toolBar.addAction(self.actionReset)
        self.menuFile.addAction(self.actionOpenNetwork)
        self.menuFile.addAction(self.actionSaveNetwork)
        self.menuSimulation.addAction(self.actionRun)
        self.menuSimulation.addAction(self.actionStep)
        self.menuSimulation.addAction(self.actionReset)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSimulation.menuAction())

        self.retranslateUi(SimulationWindow)
        QtCore.QMetaObject.connectSlotsByName(SimulationWindow)
        SimulationWindow.setTabOrder(self.stepSize, self.treeKey)

    def retranslateUi(self, SimulationWindow):
        SimulationWindow.setWindowTitle(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Pymote Simulation",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.controlGroupBox.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "Control", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.label_2.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Step size:", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.stepSize.setSpecialValueText(
            QtGui.QApplication.translate(
                "SimulationWindow", "All", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.viewGroupBox.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "View", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.networkViewGroup.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "Network", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.showNodes.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Nodes", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.showEdges.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Edges", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.showMessages.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Messages", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.showLabels.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Labels", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.redrawNetworkButton.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Redraw", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.treeGroupBox.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Enter memory key that has parent and child items.",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.treeGroupBox.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "Tree", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.treeKey.setText(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "treeNeighbors",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.label.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Key:", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.propagationError.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Enter memory key that has stitch location data.",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.propagationError.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Propagation error",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.locKey.setText(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "convergecastLoc",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.label2.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "LocKey:", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.toolBar.setWindowTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuFile.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "File", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuSimulation.setTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "Simulation", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.dockWidget.setWindowTitle(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Network inspector",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.dockWidget_2.setWindowTitle(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Node inspector",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.dockWidget_3.setWindowTitle(
            QtGui.QApplication.translate(
                "SimulationWindow", "Log", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionRun.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Run", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionRun.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Run simulation from beginning",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionRun.setShortcut(
            QtGui.QApplication.translate(
                "SimulationWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionStep.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Step", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionStep.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Run next step",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionStep.setShortcut(
            QtGui.QApplication.translate(
                "SimulationWindow", "Ctrl+Space", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionReset.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Reset", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionReset.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Reset simulation",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionReset.setShortcut(
            QtGui.QApplication.translate(
                "SimulationWindow", "Ctrl+W", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionCopyInspectorData.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Copy", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionCopyInspectorData.setShortcut(
            QtGui.QApplication.translate(
                "SimulationWindow", "Ctrl+C", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionSaveNetwork.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Save", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionSaveNetwork.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Save network in npickle format",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionSaveNetwork.setShortcut(
            QtGui.QApplication.translate(
                "SimulationWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionOpenNetwork.setText(
            QtGui.QApplication.translate(
                "SimulationWindow", "Open", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionOpenNetwork.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Open network from npickle",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionOpenNetwork.setShortcut(
            QtGui.QApplication.translate(
                "SimulationWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionShowLocalizedSubclusters.setText(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Show localized subclusters",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionShowLocalizedSubclusters.setToolTip(
            QtGui.QApplication.translate(
                "SimulationWindow",
                "Show localized subclusters based on memory field that has positions and subclusters items.",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )


from . import icons_rc
