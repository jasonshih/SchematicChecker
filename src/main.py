from src.Explorer import Explorer
# from src.DrawingBoard import BlockVisualizer
# from src.SymbolNetsAnalyzer import PathAnalyzer
from src.Reporter import Reporter
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    oo = Explorer()
    report = Reporter()
    # xx = BlockVisualizer()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    ms_report = report.multi_site_check(oo)
    [print(str(x) + ' --> ' + str(v)) for x, v in ms_report.items() if False in v.values()]

    # cm_report = report.create_channel_map(oo)
    #
    # fs_report = report.force_and_sense_check(oo)
    #
    # dni_report = report.create_dni_report(oo)

    # xx.draw()
