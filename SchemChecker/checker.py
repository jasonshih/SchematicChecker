from SchemChecker.PathFinder import PathFinder
from SchemChecker.DrawingBoard import BlockVisualizer
from SchemChecker.SymbolNetsAnalyzer import PathTester

if __name__ == "__main__":

    oo = PathFinder()
    xx = BlockVisualizer()
    ff = PathTester()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    # combined_path = []
    # sep_path = {}

    # node_under_test = ('J6', 'T8', 'IO85')
    # node_under_test = ('J6', 'A15', 'IO8')
    # node_under_test = ('X0', '110', 'MPP3')
    # node_under_test = ('X0', '114', 'CC1')
    # node_under_test = ('X0', '153', 'VREG_L3')
    # node_under_test = ('X0', '143', 'GPIO7')
    # node_under_test = ('X0', '90', 'GPIO6')

    # oo.find_path(node_under_test)
    # ff.get_device_symbols(oo.path)
    # ff.get_tester_nets(oo.path)

    for i in ['X' + str(i) for i in range(4)]:
        # node_under_test = (i, '110', 'MPP3')
        # node_under_test = (i, '114', 'CC1')
        # node_under_test = (i, '153', 'VREG_L3')
        node_under_test = (i, '143', 'GPIO7')
        # node_under_test = (i, '90', 'GPIO6')

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
            # combined_path.extend(oo.path)
            # sep_path.update({i: oo.path})

        print(str(ff.get_path_to_ground(oo.path, 'AGND')))
        print('device :' + str(ff.get_device_symbols(oo.path)))
        print('tester :' + str(ff.get_tester_nets(oo.path)))
        print('')

        xx.SYMBOL_DICT = oo.SYMBOL_DICT
        xx.draw()

        # for num, nam in oo.SYMBOL_DICT['X0'].pins:
        #     for sym in oo.device_symbols:
        #         oo.find_path(sym, num, nam)
        #         print('|'.join([sym, num, nam]) + ': \t\t' + str(list(oo.get_tester_nets())))
