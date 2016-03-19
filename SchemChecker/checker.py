import SchemChecker.PathFinder as pF
import SchemChecker.DrawingBoard as bV
import SchemChecker.SymbolNetsAnalyzer as pA

if __name__ == "__main__":

    oo = pF.PathFinder()
    xx = bV.BlockVisualizer()
    ff = pA.PathCruncher()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)

    # combined_path = []
    # sep_path = {}

    # oo.find_path('J6', 'T8', 'IO85')
    # oo.find_path('J6', 'A15', 'IO8')

    for i in ['X' + str(i) for i in range(16)]:

        # oo.find_path((i, '110', 'MPP3'))
        # oo.find_path((i, '114', 'CC1'))
        # oo.find_path((i, '153', 'VREG_L3'))
        # oo.find_path((i, '143', 'GPIO7'))
        oo.find_path((i, '90', 'GPIO6'))

        if i == 'X0':
            print('REFERENCE:')
            ff.create_reference(oo.path)
            print('')
        else:
            print('TESTING :' + i + '...')
            ff.set_path_under_test(oo.path)
            ff.is_multi_site_ok()
            ff.set_path_under_test([])
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
