from src.PathFinder import PathFinder
from src.DrawingBoard import BlockVisualizer
from src.SymbolNetsAnalyzer import PathTester
from src.Reporter import Reporter

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    oo = PathFinder()
    xx = BlockVisualizer()
    ff = PathTester()
    rp = Reporter()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)
    # oo.get_nodes_with_pin('X0', 'MPP3')

    # node_under_test = SchematicNode(('J6', 'T8', 'IO85'))
    # node_under_test = SchematicNode(('J6', 'A15', 'IO8'))

    # oo.find_path(node_under_test)
    # ff.get_device_symbols(oo.path)
    # ff.get_tester_nets(oo.path)

    PATH_DICT = {}
    for j in ['MPP1', 'MPP2', 'MPP3', 'MPP4']:
        [nut] = oo.get_nodes_with_pin('X0', j)
        PATH_DICT.update({j: oo.find_path(nut)})

    rp.create_channel_map(PATH_DICT)

    # rp.check_all_sites(oo, ff, xx)
    # uvi_force_sense = ff.get_uvi_force_sense_merging_point(oo.SYMBOL_DICT, oo.NETS_DICT)
    # xx.draw()
