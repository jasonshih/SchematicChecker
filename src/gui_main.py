from PyQt4.QtCore import *
from PyQt4.QtGui import *
from src import mainwindow_ui
from src.Explorer import *
from src.Reporter import *

import logging
import sys


class Launcher(QMainWindow, mainwindow_ui.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        self.setupUi(self)

        self.actionOpen.triggered.connect(self.open_xls)
        self.actionExit.triggered.connect(app.quit)

        self.report = Reporter()
        self.oo = Explorer()

        self.st_btn_create.clicked.connect(self.create_reports)

        # item = self.st_list.item(0)
        # item.setText(_translate("MainWindow", "multi-site symmetry", None))
        # item = self.st_list.item(1)
        # item.setText(_translate("MainWindow", "force & sense connections", None))
        # item = self.st_list.item(2)
        # item.setText(_translate("MainWindow", "dni component list", None))
        # item = self.st_list.item(3)
        # item.setText(_translate("MainWindow", "grounded device pins", None))

    def open_xls(self):
        print('opening file')
        xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
        self.oo.read_xlsx(xlsx_file)

    def create_reports(self):

        if self.st_list.item(0).isSelected():
            ms_report = self.report.multi_site_check(self.oo)

        if self.st_list.item(1).isSelected():
            fs_report = self.report.force_and_sense_check(self.oo)
            self.st_text_edit.appendPlainText('=== UVI80 FORCE & SENSE CHECK ===')
            if fs_report:
                self.st_text_edit.appendPlainText('WARNING: found %s UVI nets disconnected' % len(fs_report))
            else:
                self.st_text_edit.appendPlainText('PASSED: all force & sense are connected' % len(fs_report))
            for x in fs_report:
                self.st_text_edit.appendPlainText(x)
            self.st_text_edit.appendPlainText('')

        if self.st_list.item(2).isSelected():
            dni_report = self.report.create_dni_report(self.oo)
            self.st_text_edit.appendPlainText('=== LIST OF DNI COMPONENTS ===')
            for x, y in sorted(dni_report.items()):
                z = x + ' --> ' + ', '.join(sorted(y))
                self.st_text_edit.appendPlainText(z)
            self.st_text_edit.appendPlainText('')

        if self.st_list.item(3).isSelected():
            pass

        # ms_report = report.multi_site_check(oo)
        # [print(str(x) + ' --> ' + str(v)) for x, v in ms_report.items() if False in v.values()]
        #
        # cm_report = report.create_channel_map(oo)
        # [print(x) for x in cm_report]
        #
        # fs_report = report.force_and_sense_check(oo)
        # [print(x + ' --> ' + str(y)) for x, y in fs_report.items()]
        #
        # dni_report = report.create_dni_report(oo)
        # [print(x + ' --> ' + str(y)) for x, y in sorted(dni_report.items())]

app = QApplication(sys.argv)
w = Launcher()
w.show()
sys.exit(app.exec_())
