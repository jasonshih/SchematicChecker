import logging
import sys

from PyQt4.QtGui import *

from src.Explorer import *
from src.Reporter import *
from ui import mainwindow_ui


class Launcher(QMainWindow, mainwindow_ui.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        self.setupUi(self)

        self.actionOpen.triggered.connect(self.open_xls)
        self.actionExit.triggered.connect(app.quit)
        self.st_btn_create.clicked.connect(self.create_reports)

        self.report = Reporter()
        self.oo = Explorer()

        self.open_xls()

    def open_xls(self):
        print('opening file')
        xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
        self.oo.read_xlsx(xlsx_file)

    def create_reports(self):

        if self.st_list.item(0).isSelected():
            ms_report = self.report.multi_site_check(self.oo)
            self.st_text_edit.appendPlainText('=== MULTI SITE SYMMETRY CHECK ===')

            if ms_report:
                self.st_text_edit.appendPlainText('WARNING: found %s with possible issues' % len(ms_report))
            else:
                self.st_text_edit.appendPlainText('PASSED: all sites are symmetrical')

            for x in ms_report:
                self.st_text_edit.appendPlainText(' at pin: '.join(x))
            self.st_text_edit.appendPlainText('')

        if self.st_list.item(1).isSelected():
            fs_report = self.report.force_and_sense_check(self.oo)
            self.st_text_edit.appendPlainText('=== UVI80 FORCE & SENSE CHECK ===')

            if fs_report:
                self.st_text_edit.appendPlainText('WARNING: found %s UVI nets disconnected' % len(fs_report))
            else:
                self.st_text_edit.appendPlainText('PASSED: all force & sense are connected')

            for x in fs_report:
                self.st_text_edit.appendPlainText(x)
            self.st_text_edit.appendPlainText('')

        if self.st_list.item(2).isSelected():
            dni_report = self.report.create_dni_report(self.oo)
            self.st_text_edit.appendPlainText('=== LIST OF DNI COMPONENTS ===')

            for x, y in sorted(dni_report.items()):
                z = x + ' at nets: ' + ', '.join(sorted(y))
                self.st_text_edit.appendPlainText(z)
            self.st_text_edit.appendPlainText('')

        if self.st_list.item(3).isSelected():
            pass

app = QApplication(sys.argv)
w = Launcher()
w.show()
sys.exit(app.exec_())
