# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Tue Apr  5 09:13:29 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(624, 436)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.centralWidget)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.schematic_tests = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.schematic_tests.sizePolicy().hasHeightForWidth())
        self.schematic_tests.setSizePolicy(sizePolicy)
        self.schematic_tests.setObjectName(_fromUtf8("schematic_tests"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.schematic_tests)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.st_groupbox = QtGui.QGroupBox(self.schematic_tests)
        self.st_groupbox.setObjectName(_fromUtf8("st_groupbox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.st_groupbox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.st_list = QtGui.QListWidget(self.st_groupbox)
        self.st_list.setAlternatingRowColors(True)
        self.st_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.st_list.setObjectName(_fromUtf8("st_list"))
        item = QtGui.QListWidgetItem()
        self.st_list.addItem(item)
        item = QtGui.QListWidgetItem()
        self.st_list.addItem(item)
        item = QtGui.QListWidgetItem()
        self.st_list.addItem(item)
        item = QtGui.QListWidgetItem()
        self.st_list.addItem(item)
        self.verticalLayout_2.addWidget(self.st_list)
        self.st_btn_create = QtGui.QPushButton(self.st_groupbox)
        self.st_btn_create.setObjectName(_fromUtf8("st_btn_create"))
        self.verticalLayout_2.addWidget(self.st_btn_create)
        self.verticalLayout.addWidget(self.st_groupbox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.st_text_edit = QtGui.QPlainTextEdit(self.schematic_tests)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Menlo"))
        self.st_text_edit.setFont(font)
        self.st_text_edit.setObjectName(_fromUtf8("st_text_edit"))
        self.horizontalLayout.addWidget(self.st_text_edit)
        self.tabWidget.addTab(self.schematic_tests, _fromUtf8(""))
        self.focus_node = QtGui.QWidget()
        self.focus_node.setObjectName(_fromUtf8("focus_node"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.focus_node)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(-1)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.nd_grpupbox = QtGui.QGroupBox(self.focus_node)
        self.nd_grpupbox.setObjectName(_fromUtf8("nd_grpupbox"))
        self.formLayout = QtGui.QFormLayout(self.nd_grpupbox)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.nd_lb_synbol = QtGui.QLabel(self.nd_grpupbox)
        self.nd_lb_synbol.setObjectName(_fromUtf8("nd_lb_synbol"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.nd_lb_synbol)
        self.nd_symbol = QtGui.QLineEdit(self.nd_grpupbox)
        self.nd_symbol.setObjectName(_fromUtf8("nd_symbol"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.nd_symbol)
        self.nd_pin_name = QtGui.QLineEdit(self.nd_grpupbox)
        self.nd_pin_name.setObjectName(_fromUtf8("nd_pin_name"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.nd_pin_name)
        self.nd_btn_search = QtGui.QPushButton(self.nd_grpupbox)
        self.nd_btn_search.setObjectName(_fromUtf8("nd_btn_search"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.nd_btn_search)
        self.nd_lb_pin_name = QtGui.QLabel(self.nd_grpupbox)
        self.nd_lb_pin_name.setObjectName(_fromUtf8("nd_lb_pin_name"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.nd_lb_pin_name)
        self.verticalLayout_3.addWidget(self.nd_grpupbox)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.nd_graph_view = QtGui.QGraphicsView(self.focus_node)
        self.nd_graph_view.setObjectName(_fromUtf8("nd_graph_view"))
        self.horizontalLayout_2.addWidget(self.nd_graph_view)
        self.horizontalLayout_2.setStretch(1, 1)
        self.tabWidget.addTab(self.focus_node, _fromUtf8(""))
        self.horizontalLayout_4.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 624, 22))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setEnabled(True)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionMulti_Site_Report = QtGui.QAction(MainWindow)
        self.actionMulti_Site_Report.setObjectName(_fromUtf8("actionMulti_Site_Report"))
        self.actionUVI80_Force_Sense = QtGui.QAction(MainWindow)
        self.actionUVI80_Force_Sense.setObjectName(_fromUtf8("actionUVI80_Force_Sense"))
        self.actionMulti_Site_Check = QtGui.QAction(MainWindow)
        self.actionMulti_Site_Check.setObjectName(_fromUtf8("actionMulti_Site_Check"))
        self.actionUVI80_Force_Sense_2 = QtGui.QAction(MainWindow)
        self.actionUVI80_Force_Sense_2.setObjectName(_fromUtf8("actionUVI80_Force_Sense_2"))
        self.actionChannel_Map_2 = QtGui.QAction(MainWindow)
        self.actionChannel_Map_2.setObjectName(_fromUtf8("actionChannel_Map_2"))
        self.actionDNI_Components = QtGui.QAction(MainWindow)
        self.actionDNI_Components.setObjectName(_fromUtf8("actionDNI_Components"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "PTE Schematic Checker", None))
        self.st_groupbox.setTitle(_translate("MainWindow", "Settings", None))
        self.st_list.setSortingEnabled(False)
        __sortingEnabled = self.st_list.isSortingEnabled()
        self.st_list.setSortingEnabled(False)
        item = self.st_list.item(0)
        item.setText(_translate("MainWindow", "multi-site symmetry", None))
        item = self.st_list.item(1)
        item.setText(_translate("MainWindow", "force & sense connections", None))
        item = self.st_list.item(2)
        item.setText(_translate("MainWindow", "dni component list", None))
        item = self.st_list.item(3)
        item.setText(_translate("MainWindow", "grounded device pins", None))
        self.st_list.setSortingEnabled(__sortingEnabled)
        self.st_btn_create.setText(_translate("MainWindow", "Create Report", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.schematic_tests), _translate("MainWindow", "Schematic Tests", None))
        self.nd_grpupbox.setTitle(_translate("MainWindow", "Node", None))
        self.nd_lb_synbol.setText(_translate("MainWindow", "Symbol", None))
        self.nd_symbol.setPlaceholderText(_translate("MainWindow", "e.g. X0", None))
        self.nd_pin_name.setPlaceholderText(_translate("MainWindow", "e.g. AVDD_BYP", None))
        self.nd_btn_search.setText(_translate("MainWindow", "Search", None))
        self.nd_lb_pin_name.setText(_translate("MainWindow", "Pin Name", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.focus_node), _translate("MainWindow", "Focus at Node", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionMulti_Site_Report.setText(_translate("MainWindow", "Multi-Site Report", None))
        self.actionUVI80_Force_Sense.setText(_translate("MainWindow", "Channel Map", None))
        self.actionMulti_Site_Check.setText(_translate("MainWindow", "Multi Site Check", None))
        self.actionUVI80_Force_Sense_2.setText(_translate("MainWindow", "UVI80 Force-Sense", None))
        self.actionChannel_Map_2.setText(_translate("MainWindow", "Channel Map", None))
        self.actionDNI_Components.setText(_translate("MainWindow", "DNI Components", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))

