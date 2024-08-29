################################################################################
## Form generated from reading UI file 'simulation.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

import icons_rc
from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDockWidget,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class Ui_SimulationWindow:
    def setupUi(self, SimulationWindow):
        if not SimulationWindow.objectName():
            SimulationWindow.setObjectName("SimulationWindow")
        SimulationWindow.resize(1106, 800)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(SimulationWindow.sizePolicy().hasHeightForWidth())
        SimulationWindow.setSizePolicy(sizePolicy)
        SimulationWindow.setMinimumSize(QSize(1096, 800))
        icon = QIcon()
        icon.addFile(":/icons/pydistsim.png", QSize(), QIcon.Normal, QIcon.Off)
        SimulationWindow.setWindowIcon(icon)
        SimulationWindow.setDockOptions(
            QMainWindow.AllowTabbedDocks | QMainWindow.AnimatedDocks | QMainWindow.VerticalTabs
        )
        self.actionRun = QAction(SimulationWindow)
        self.actionRun.setObjectName("actionRun")
        icon1 = QIcon()
        icon1.addFile(":/icons/player_play.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRun.setIcon(icon1)
        self.actionStep = QAction(SimulationWindow)
        self.actionStep.setObjectName("actionStep")
        icon2 = QIcon()
        icon2.addFile(":/icons/player_fwd.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionStep.setIcon(icon2)
        self.actionReset = QAction(SimulationWindow)
        self.actionReset.setObjectName("actionReset")
        icon3 = QIcon()
        icon3.addFile(":/icons/player_start.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionReset.setIcon(icon3)
        self.actionCopyInspectorData = QAction(SimulationWindow)
        self.actionCopyInspectorData.setObjectName("actionCopyInspectorData")
        self.actionCopyInspectorData.setShortcutContext(Qt.WidgetShortcut)
        self.actionSaveNetwork = QAction(SimulationWindow)
        self.actionSaveNetwork.setObjectName("actionSaveNetwork")
        icon4 = QIcon()
        icon4.addFile(":/icons/filesaveas.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSaveNetwork.setIcon(icon4)
        self.actionOpenNetwork = QAction(SimulationWindow)
        self.actionOpenNetwork.setObjectName("actionOpenNetwork")
        self.actionOpenNetwork.setCheckable(False)
        self.actionOpenNetwork.setChecked(False)
        icon5 = QIcon()
        icon5.addFile(":/icons/fileopen.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionOpenNetwork.setIcon(icon5)
        self.actionShowLocalizedSubclusters = QAction(SimulationWindow)
        self.actionShowLocalizedSubclusters.setObjectName("actionShowLocalizedSubclusters")
        self.centralwidget = QWidget(SimulationWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftWidget = QWidget(self.centralwidget)
        self.leftWidget.setObjectName("leftWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leftWidget.sizePolicy().hasHeightForWidth())
        self.leftWidget.setSizePolicy(sizePolicy2)
        self.verticalLayout_3 = QVBoxLayout(self.leftWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.controlGroupBox = QGroupBox(self.leftWidget)
        self.controlGroupBox.setObjectName("controlGroupBox")
        self.controlGroupBox.setMinimumSize(QSize(0, 0))
        self.verticalLayout_5 = QVBoxLayout(self.controlGroupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.widget = QWidget(self.controlGroupBox)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.stepSize = QSpinBox(self.widget)
        self.stepSize.setObjectName("stepSize")
        self.stepSize.setAccelerated(True)
        self.stepSize.setMaximum(999)
        self.stepSize.setValue(1)

        self.horizontalLayout_2.addWidget(self.stepSize)

        self.verticalLayout_5.addWidget(self.widget)

        self.verticalLayout_3.addWidget(self.controlGroupBox)

        self.viewGroupBox = QGroupBox(self.leftWidget)
        self.viewGroupBox.setObjectName("viewGroupBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.viewGroupBox.sizePolicy().hasHeightForWidth())
        self.viewGroupBox.setSizePolicy(sizePolicy3)
        self.verticalLayout_2 = QVBoxLayout(self.viewGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.networkViewGroup = QGroupBox(self.viewGroupBox)
        self.networkViewGroup.setObjectName("networkViewGroup")
        self.verticalLayout_6 = QVBoxLayout(self.networkViewGroup)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.showNodes = QCheckBox(self.networkViewGroup)
        self.showNodes.setObjectName("showNodes")
        self.showNodes.setChecked(True)

        self.verticalLayout_6.addWidget(self.showNodes)

        self.showEdges = QCheckBox(self.networkViewGroup)
        self.showEdges.setObjectName("showEdges")
        self.showEdges.setChecked(True)

        self.verticalLayout_6.addWidget(self.showEdges)

        self.showMessages = QCheckBox(self.networkViewGroup)
        self.showMessages.setObjectName("showMessages")
        self.showMessages.setChecked(True)

        self.verticalLayout_6.addWidget(self.showMessages)

        self.showLabels = QCheckBox(self.networkViewGroup)
        self.showLabels.setObjectName("showLabels")
        self.showLabels.setChecked(True)

        self.verticalLayout_6.addWidget(self.showLabels)

        self.redrawNetworkButton = QPushButton(self.networkViewGroup)
        self.redrawNetworkButton.setObjectName("redrawNetworkButton")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.redrawNetworkButton.sizePolicy().hasHeightForWidth())
        self.redrawNetworkButton.setSizePolicy(sizePolicy4)

        self.verticalLayout_6.addWidget(self.redrawNetworkButton)

        self.verticalLayout_2.addWidget(self.networkViewGroup)

        self.treeGroupBox = QGroupBox(self.viewGroupBox)
        self.treeGroupBox.setObjectName("treeGroupBox")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.treeGroupBox.sizePolicy().hasHeightForWidth())
        self.treeGroupBox.setSizePolicy(sizePolicy5)
        self.treeGroupBox.setMinimumSize(QSize(132, 60))
        self.treeGroupBox.setFlat(False)
        self.treeGroupBox.setCheckable(True)
        self.treeGroupBox.setChecked(True)
        self.tree_key = QLineEdit(self.treeGroupBox)
        self.tree_key.setObjectName("tree_key")
        self.tree_key.setGeometry(QRect(42, 20, 71, 20))
        self.tree_key.setFrame(True)
        self.label = QLabel(self.treeGroupBox)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 22, 31, 16))

        self.verticalLayout_2.addWidget(self.treeGroupBox)

        self.propagationError = QGroupBox(self.viewGroupBox)
        self.propagationError.setObjectName("propagationError")
        self.propagationError.setMinimumSize(QSize(132, 70))
        self.propagationError.setCheckable(True)
        self.propagationError.setChecked(False)
        self.locKey = QLineEdit(self.propagationError)
        self.locKey.setObjectName("locKey")
        self.locKey.setGeometry(QRect(10, 40, 111, 20))
        self.label2 = QLabel(self.propagationError)
        self.label2.setObjectName("label2")
        self.label2.setGeometry(QRect(10, 20, 46, 13))

        self.verticalLayout_2.addWidget(self.propagationError)

        self.verticalLayout_3.addWidget(self.viewGroupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.horizontalLayout.addWidget(self.leftWidget)

        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.networkDisplayWidget = QWidget(self.centralwidget)
        self.networkDisplayWidget.setObjectName("networkDisplayWidget")
        sizePolicy1.setHeightForWidth(self.networkDisplayWidget.sizePolicy().hasHeightForWidth())
        self.networkDisplayWidget.setSizePolicy(sizePolicy1)
        self.networkDisplayWidget.setMinimumSize(QSize(650, 0))

        self.horizontalLayout.addWidget(self.networkDisplayWidget)

        self.horizontalSpacer_2 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        SimulationWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QToolBar(SimulationWindow)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setAutoFillBackground(False)
        SimulationWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.menubar = QMenuBar(SimulationWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1106, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSimulation = QMenu(self.menubar)
        self.menuSimulation.setObjectName("menuSimulation")
        SimulationWindow.setMenuBar(self.menubar)
        self.dockWidget = QDockWidget(SimulationWindow)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidget.setMinimumSize(QSize(87, 109))
        self.dockWidget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidget.setAllowedAreas(Qt.RightDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy6)
        self.horizontalLayout_3 = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.networkInspector = QTreeView(self.dockWidgetContents)
        self.networkInspector.setObjectName("networkInspector")
        self.networkInspector.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.networkInspector.setFrameShape(QFrame.NoFrame)
        self.networkInspector.setProperty("showDropIndicator", False)
        self.networkInspector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.networkInspector.setAnimated(True)
        self.networkInspector.setWordWrap(True)
        self.networkInspector.setHeaderHidden(True)

        self.horizontalLayout_3.addWidget(self.networkInspector)

        self.dockWidget.setWidget(self.dockWidgetContents)
        SimulationWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget)
        self.dockWidget_2 = QDockWidget(SimulationWindow)
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidget_2.setMinimumSize(QSize(105, 377))
        self.dockWidget_2.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidget_2.setAllowedAreas(Qt.RightDockWidgetArea)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        sizePolicy6.setHeightForWidth(self.dockWidgetContents_2.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents_2.setSizePolicy(sizePolicy6)
        self.horizontalLayout_4 = QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.nodeInspector = QTreeView(self.dockWidgetContents_2)
        self.nodeInspector.setObjectName("nodeInspector")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.nodeInspector.sizePolicy().hasHeightForWidth())
        self.nodeInspector.setSizePolicy(sizePolicy7)
        self.nodeInspector.setMinimumSize(QSize(87, 337))
        self.nodeInspector.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.nodeInspector.setFrameShape(QFrame.NoFrame)
        self.nodeInspector.setProperty("showDropIndicator", False)
        self.nodeInspector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.nodeInspector.setAnimated(True)
        self.nodeInspector.setWordWrap(True)
        self.nodeInspector.setHeaderHidden(True)

        self.horizontalLayout_4.addWidget(self.nodeInspector)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        SimulationWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget_2)
        self.dockWidget_3 = QDockWidget(SimulationWindow)
        self.dockWidget_3.setObjectName("dockWidget_3")
        self.dockWidget_3.setMinimumSize(QSize(87, 109))
        self.dockWidget_3.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidget_3.setAllowedAreas(Qt.RightDockWidgetArea)
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        sizePolicy6.setHeightForWidth(self.dockWidgetContents_3.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents_3.setSizePolicy(sizePolicy6)
        self.horizontalLayout_5 = QHBoxLayout(self.dockWidgetContents_3)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.logListWidget = QListWidget(self.dockWidgetContents_3)
        self.logListWidget.setObjectName("logListWidget")
        self.logListWidget.setFrameShape(QFrame.NoFrame)
        self.logListWidget.setFrameShadow(QFrame.Sunken)
        self.logListWidget.setLineWidth(0)

        self.horizontalLayout_5.addWidget(self.logListWidget)

        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        SimulationWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget_3)
        QWidget.setTabOrder(self.stepSize, self.tree_key)

        self.toolBar.addAction(self.actionOpenNetwork)
        self.toolBar.addAction(self.actionSaveNetwork)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRun)
        self.toolBar.addAction(self.actionStep)
        self.toolBar.addAction(self.actionReset)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSimulation.menuAction())
        self.menuFile.addAction(self.actionOpenNetwork)
        self.menuFile.addAction(self.actionSaveNetwork)
        self.menuSimulation.addAction(self.actionRun)
        self.menuSimulation.addAction(self.actionStep)
        self.menuSimulation.addAction(self.actionReset)

        self.retranslateUi(SimulationWindow)

        QMetaObject.connectSlotsByName(SimulationWindow)

    # setupUi

    def retranslateUi(self, SimulationWindow):
        SimulationWindow.setWindowTitle(QCoreApplication.translate("SimulationWindow", "PyDistSim Simulation", None))
        self.actionRun.setText(QCoreApplication.translate("SimulationWindow", "Run", None))
        # if QT_CONFIG(tooltip)
        self.actionRun.setToolTip(QCoreApplication.translate("SimulationWindow", "Run simulation from beginning", None))
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionRun.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+R", None))
        # endif // QT_CONFIG(shortcut)
        self.actionStep.setText(QCoreApplication.translate("SimulationWindow", "Step", None))
        # if QT_CONFIG(tooltip)
        self.actionStep.setToolTip(QCoreApplication.translate("SimulationWindow", "Run next step", None))
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionStep.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+Space", None))
        # endif // QT_CONFIG(shortcut)
        self.actionReset.setText(QCoreApplication.translate("SimulationWindow", "Reset", None))
        # if QT_CONFIG(tooltip)
        self.actionReset.setToolTip(QCoreApplication.translate("SimulationWindow", "Reset simulation", None))
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionReset.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+W", None))
        # endif // QT_CONFIG(shortcut)
        self.actionCopyInspectorData.setText(QCoreApplication.translate("SimulationWindow", "Copy", None))
        # if QT_CONFIG(shortcut)
        self.actionCopyInspectorData.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+C", None))
        # endif // QT_CONFIG(shortcut)
        self.actionSaveNetwork.setText(QCoreApplication.translate("SimulationWindow", "Save", None))
        # if QT_CONFIG(tooltip)
        self.actionSaveNetwork.setToolTip(
            QCoreApplication.translate("SimulationWindow", "Save network in npickle format", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionSaveNetwork.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+S", None))
        # endif // QT_CONFIG(shortcut)
        self.actionOpenNetwork.setText(QCoreApplication.translate("SimulationWindow", "Open", None))
        # if QT_CONFIG(tooltip)
        self.actionOpenNetwork.setToolTip(
            QCoreApplication.translate("SimulationWindow", "Open network from npickle", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionOpenNetwork.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+O", None))
        # endif // QT_CONFIG(shortcut)
        self.actionShowLocalizedSubclusters.setText(
            QCoreApplication.translate("SimulationWindow", "Show localized subclusters", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionShowLocalizedSubclusters.setToolTip(
            QCoreApplication.translate(
                "SimulationWindow",
                "Show localized subclusters based on memory field that has positions and subclusters items.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionShowLocalizedSubclusters.setShortcut(QCoreApplication.translate("SimulationWindow", "Ctrl+L", None))
        # endif // QT_CONFIG(shortcut)
        self.controlGroupBox.setTitle(QCoreApplication.translate("SimulationWindow", "Control", None))
        self.label_2.setText(QCoreApplication.translate("SimulationWindow", "Step size:", None))
        self.stepSize.setSpecialValueText(QCoreApplication.translate("SimulationWindow", "All", None))
        self.viewGroupBox.setTitle(QCoreApplication.translate("SimulationWindow", "View", None))
        self.networkViewGroup.setTitle(QCoreApplication.translate("SimulationWindow", "Network", None))
        self.showNodes.setText(QCoreApplication.translate("SimulationWindow", "Nodes", None))
        self.showEdges.setText(QCoreApplication.translate("SimulationWindow", "Edges", None))
        self.showMessages.setText(QCoreApplication.translate("SimulationWindow", "Messages", None))
        self.showLabels.setText(QCoreApplication.translate("SimulationWindow", "Labels", None))
        self.redrawNetworkButton.setText(QCoreApplication.translate("SimulationWindow", "Redraw", None))
        # if QT_CONFIG(tooltip)
        self.treeGroupBox.setToolTip(
            QCoreApplication.translate(
                "SimulationWindow",
                "Enter memory key that has parent and child items.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.treeGroupBox.setTitle(QCoreApplication.translate("SimulationWindow", "Tree", None))
        self.tree_key.setText(QCoreApplication.translate("SimulationWindow", "treeNeighbors", None))
        self.label.setText(QCoreApplication.translate("SimulationWindow", "Key:", None))
        # if QT_CONFIG(tooltip)
        self.propagationError.setToolTip(
            QCoreApplication.translate(
                "SimulationWindow",
                "Enter memory key that has stitch location data.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.propagationError.setTitle(QCoreApplication.translate("SimulationWindow", "Propagation error", None))
        self.locKey.setText(QCoreApplication.translate("SimulationWindow", "convergecastLoc", None))
        self.label2.setText(QCoreApplication.translate("SimulationWindow", "LocKey:", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("SimulationWindow", "toolBar", None))
        self.menuFile.setTitle(QCoreApplication.translate("SimulationWindow", "File", None))
        self.menuSimulation.setTitle(QCoreApplication.translate("SimulationWindow", "Simulation", None))
        self.dockWidget.setWindowTitle(QCoreApplication.translate("SimulationWindow", "Network inspector", None))
        self.dockWidget_2.setWindowTitle(QCoreApplication.translate("SimulationWindow", "Node inspector", None))
        self.dockWidget_3.setWindowTitle(QCoreApplication.translate("SimulationWindow", "Log", None))

    # retranslateUi
