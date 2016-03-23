from SchemChecker.PathFinder import PathFinder
from SchemChecker.DrawingBoard import BlockVisualizer
from SchemChecker.SymbolNetsAnalyzer import PathTester

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    oo = PathFinder()
    xx = BlockVisualizer()
    ff = PathTester()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)
    # oo.get_nodes_with_pin('X0', 'MPP3')

    # node_under_test = SchematicNode(('J6', 'T8', 'IO85'))
    # node_under_test = SchematicNode(('J6', 'A15', 'IO8'))

    # oo.find_path(node_under_test)
    # ff.get_device_symbols(oo.path)
    # ff.get_tester_nets(oo.path)

    uvi_force_sense = ff.get_uvi_force_sense_merging_point(oo.SYMBOL_DICT, oo.NETS_DICT)

    for i in ['X' + str(i) for i in range(4)]:
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='VIN_GR4')
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='VIN_S1_1') # sense only, no force?
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='GPIO6')
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='GPIO7')
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='VREG_L16')
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='VREG_L05')
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='MPP1')
        # [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='MPP3')
        [node_under_test] = oo.get_nodes_with_pin(symbol=i, pin='CC1')

        oo.find_path(node_under_test)

        if i == 'X0':
            print('')
            print('REFERENCE:')
            ff.compile(oo.path_obj)
            print('')
            print('TESTING :' + i + '...')
            xx.path = oo.path_obj
        else:
            print('TESTING :' + i + '...')
            ff.is_multi_site_ok(oo.path_obj)

        path_to_gnd = ff.get_path_to_plane(oo.path_obj, 'AGND')
        devices = ff.get_device_symbols(oo.path_obj)
        tester = ff.get_tester_nets(oo.path_obj)

        print('')
        [print(str(x)) for x in path_to_gnd]
        print('')
        [print(str(x)) for x in devices]
        print('')
        [print(str(x)) for x in tester]
        print('')

    xx.draw()
