from src.Explorer import Explorer
# from src.DrawingBoard import BlockVisualizer
from src.Reporter import Reporter
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    oo = Explorer()
    report = Reporter()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    ms_report = report.multi_site_check(oo)
    [print(' at pin: '.join(x)) for x in ms_report]

    cm_report = report.create_channel_map(oo)
    [print(', '.join(x)) for x in cm_report]

    agnd_report = report.get_pins_to_nets(oo, symbol=['X0'], nets='AGND')
    [print(x.name) for x in agnd_report]

    p5v_report = report.get_symbols_to_nets(oo, 'P5V')
    [print(x.name) for x in p5v_report]

    fs_report = report.force_and_sense_check(oo)
    [print(x) for x in fs_report]

    dni_report = report.create_dni_report(oo)
    [print(x + ' at nets: ' + ', '.join(sorted(y))) for x, y in sorted(dni_report.items())]

    # report.show_component(oo, 'X0', 'VREG_L3')

