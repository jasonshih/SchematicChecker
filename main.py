from src.Explorer import Explorer
# from src.DrawingBoard import BlockVisualizer
from src.Reporter import Reporter
from src.Analyzer import PathAnalyzer
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)     # DEBUG INFO WARN ERROR
    logger = logging.getLogger(__name__)

    oo = Explorer()
    report = Reporter()
    az = PathAnalyzer()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    nut = oo.get_nodes_with_pin('X0', 'CDC_LO_P')
    this_path = oo.explore(nut)
    az.view_everything(this_path)

    # ms_report = report.multi_site_check(oo)
    # [print('ms err: ' + ' at pin: '.join(x)) for x in ms_report]
    # print('\v')
    #
    # cm_report = report.create_channel_map(oo)
    # [print('cm: ' + ', '.join(x)) for x in cm_report]
    # print('\v')
    #
    # agnd_report = report.get_pins_to_nets(oo, symbol=['X0'], nets='AGND')
    # [print('to agnd: ' + x.name) for x in agnd_report]
    # print('\v')
    #
    # p5v_report = report.get_symbols_to_nets(oo, 'P5V')
    # [print('active comp to p5v: ' + x.name) for x in p5v_report if oo.SYMBOL_DICT[x.symbol].is_active]
    # print('\v')
    #
    # n5v_report = report.get_symbols_to_nets(oo, 'N5V')
    # [print('active comp to n5v: ' + x.name) for x in n5v_report if oo.SYMBOL_DICT[x.symbol].is_active]
    # print('\v')
    #
    # p5v_rly_report = report.get_symbols_to_nets(oo, '+5V_RLY')
    # [print('active comp to p5v_rly: ' + x.name) for x in p5v_rly_report if oo.SYMBOL_DICT[x.symbol].is_active]
    # print('\v')
    #
    # unconnected_report = report.get_symbols_to_nets(oo, 'unconnected')
    # [print('unconnected : ' + x.name) for x in unconnected_report if x.symbol not in oo.connector_symbols]
    # print('\v')
    #
    # fs_report = report.force_and_sense_check(oo)
    # [print('unpaired ' + x) for x in fs_report]
    # print('\v')
    #
    # dni_report = report.create_dni_report(oo)
    # [print('DNI ' + x + ' at nets: ' + ', '.join(sorted(y))) for x, y in sorted(dni_report.items())]
    # print('\v')

    # report.show_component(oo, 'X0', 'VREG_L3')
