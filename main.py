from src.Explorer import Explorer
from src.Reporter import Reporter
from pathlib import Path
import logging


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)     # DEBUG INFO WARN ERROR
    logger = logging.getLogger(__name__)

    oo = Explorer()
    report = Reporter()
    folder = Path('/Users/cahyo/Documents/data/schem_checker')
    inp_file = folder / 'P1495_sample.xlsx'
    oo.read_xlsx(str(inp_file))

    # ------------------- #
    # === SEARCH PAGE === #
    # ------------------- #
    search_result = oo.search_pins_or_nets('VIN_GR4')

    print(search_result['pins'])
    for n in search_result['nets']:
        nodes = oo.get_nodes_from_nets(n.name)
        print('{}: {}'.format(n, nodes))
    print('\v')

    report.view_pin_details(oo, 'X0', 'GPIO7')
    print('\v')

    # ----------------------------- #
    # === TOP LEVEL REPORT PAGE === #
    # ----------------------------- #
    # ms_report = report.multi_site_check(oo)
    # [print('ms err: ' + ' at pin: '.join(x)) for x in ms_report]
    # print('\v')

    # cm_report = report.create_channel_map(oo)
    # [print('cm: ' + ', '.join(x)) for x in cm_report]
    # print('\v')

    # fs_report = report.force_and_sense_check(oo)
    # [print('unpaired ' + x) for x in fs_report]
    # print('\v')
    #
    # dni_report = report.create_dni_report(oo)
    # [print('DNI ' + x + ' at nets: ' + ', '.join(sorted(y))) for x, y in sorted(dni_report.items())]
    # print('\v')

    # ------------------------- #
    # === SPECIAL NETS PAGE === #
    # ------------------------- #
    # nets_count = oo.get_nets_count()
    # [print('number of nodes connected to {}: {}'.format(p, c)) for p, c in nets_count[:20]]

    # agnd_report = oo.get_nodes_from_symbol_and_nets(symbol=['X0'], nets='AGND')
    # [print('to agnd: ' + x.name) for x in agnd_report]
    # print('\v')
    #
    # unconnected_report = oo.get_nodes_from_nets('unconnected')
    # [print('unconnected : ' + x.name) for x in unconnected_report if x.symbol not in oo.connector_symbols]
    # print('\v')
    #
    # p5v_report = oo.get_nodes_from_nets('P5V')
    # [print('active comp to p5v: ' + x.name) for x in p5v_report if oo.SYMBOL_DICT[x.symbol].is_active]
    # print('\v')
    #
    # n5v_report = oo.get_nodes_from_nets('N5V')
    # [print('active comp to n5v: ' + x.name) for x in n5v_report if oo.SYMBOL_DICT[x.symbol].is_active]
    # print('\v')
    #
    # p5v_rly_report = oo.get_nodes_from_nets('+5V_RLY')
    # [print('active comp to p5v_rly: ' + x.name) for x in p5v_rly_report if oo.SYMBOL_DICT[x.symbol].is_active]
    # print('\v')
