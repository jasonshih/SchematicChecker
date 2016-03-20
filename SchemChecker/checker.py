from SchemChecker.PathFinder import PathFinder
from SchemChecker.DrawingBoard import BlockVisualizer
from SchemChecker.SymbolNetsAnalyzer import PathCruncher

if __name__ == "__main__":

    oo = PathFinder()
    xx = BlockVisualizer()
    ff = PathCruncher()

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

    for i in ['X' + str(i) for i in range(16)]:
        node_under_test = (i, '110', 'MPP3')
        node_under_test = (i, '114', 'CC1')
        node_under_test = (i, '153', 'VREG_L3')
        node_under_test = (i, '143', 'GPIO7')
        node_under_test = (i, '90', 'GPIO6')

        oo.find_path(node_under_test)

        if i == 'X0':
            print('REFERENCE:')
            ff.compile(oo.path)
            ff.get_device_symbols(oo.path)
            ff.get_tester_nets(oo.path)
            print('')
        else:
            print('TESTING :' + i + '...')
            ff.get_device_symbols(oo.path)
            ff.get_tester_nets(oo.path)
            ff.is_multi_site_ok(oo.path)
            print('')

        # combined_path.extend(oo.path)
        # sep_path.update({i: oo.path})

    # xx.path = combined_path
    # xx.SYMBOL_DICT = oo.SYMBOL_DICT
    # xx.draw()

    # for num, nam in oo.SYMBOL_DICT['X0'].pins:
    #     for sym in oo.device_symbols:
    #         oo.find_path(sym, num, nam)
    #         print('|'.join([sym, num, nam]) + ': \t\t' + str(list(oo.get_tester_nets())))
