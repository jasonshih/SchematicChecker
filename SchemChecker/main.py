from SchemChecker.PathFinder import PathFinder
from SchemChecker.DrawingBoard import BlockVisualizer
from SchemChecker.SymbolNetsAnalyzer import PathTester
from SchemChecker.SchemComponent import *
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    oo = PathFinder()
    xx = BlockVisualizer()
    ff = PathTester()

    # logger.setLevel(logging.DEBUG)

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    # node_under_test = SchematicNode(('J6', 'T8', 'IO85'))
    # node_under_test = SchematicNode(('J6', 'A15', 'IO8'))
    # node_under_test = SchematicNode(('X0', '110', 'MPP3'))
    # node_under_test = SchematicNode(('X0', '114', 'CC1'))
    # node_under_test = SchematicNode(('X0', '153', 'VREG_L3'))
    # node_under_test = SchematicNode(('X0', '143', 'GPIO7'))
    # node_under_test = SchematicNode(('X0', '90', 'GPIO6'))

    # oo.find_path(node_under_test)
    # ff.get_device_symbols(oo.path)
    # ff.get_tester_nets(oo.path)

    for i in ['X' + str(i) for i in range(4)]:
        # node_under_test = SchematicNode((i, '110', 'MPP3'))
        # node_under_test = SchematicNode((i, '114', 'CC1'))
        node_under_test = SchematicNode((i, '153', 'VREG_L3'))
        # node_under_test = SchematicNode((i, '143', 'GPIO7'))
        # node_under_test = SchematicNode((i, '90', 'GPIO6'))

        oo.find_path(node_under_test)

        if i == 'X0':
            print('')
            print('REFERENCE:')
            ff.compile(oo.path)
            print('')
            print('TESTING :' + i + '...')
            xx.path = oo.path
        else:
            print('TESTING :' + i + '...')
            ff.is_multi_site_ok(oo.path)

        gnd = ff.get_path_to_plane(oo.path, 'AGND')
        path_to_gnd = [str(z) for x in gnd for y in x for z in y[:2]]

        print(str(path_to_gnd))
        print('device :' + str([str(x) for x in ff.get_device_symbols(oo.path)]))
        print('tester :' + str([str(x) for x in ff.get_tester_nets(oo.path)]))
        print('')

    xx.draw()
