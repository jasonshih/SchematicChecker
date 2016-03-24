from src.Explorer import Explorer
from src.DrawingBoard import BlockVisualizer
from src.SymbolNetsAnalyzer import PathAnalyzer
from src.Reporter import Reporter

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    oo = Explorer()
    # xx = BlockVisualizer()
    report = Reporter()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    aa = report.multi_site_check(oo, 4)
    pass


    # node_under_test = SchematicNode(('J6', 'T8', 'IO85'))
    # node_under_test = SchematicNode(('J6', 'A15', 'IO8'))

    # oo.find_path(node_under_test)
    # ff.get_device_symbols(oo.path)
    # ff.get_tester_nets(oo.path)

    # # [nut] = oo.get_nodes_with_pin('X0', 'MPP3')
    # [nut] = oo.get_nodes_with_pin('X0', 'VIN_GR4')
    # put = oo.find_path(nut)
    # path_to_nets = ff.get_path_to_nets(put, 'J20_UVI80_25S')
    # # path_to_nets = ff.get_path_to_nets(put, 'AGND')
    #
    # [print(x) for x in path_to_nets]
    # pass

    # PATH_DICT = {}
    # for j in ['MPP1', 'MPP2', 'MPP3', 'MPP4']:
    #     [nut] = oo.get_nodes_with_pin('X0', j)
    #     PATH_DICT.update({j: oo.find_path(nut)})
    #
    # rp.create_channel_map(PATH_DICT)

    # uvi_force_sense = ff.get_uvi_force_sense_merging_point(oo.SYMBOL_DICT, oo.NETS_DICT)
    # xx.draw()
