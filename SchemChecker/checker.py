import SchemChecker.PathFinder as pf
import SchemChecker.BlockVisualizer as bv

if __name__ == "__main__":

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo = pf.PathFinder()
    xx = bv.BlockVisualizer()
    oo.populate_dictionaries(xlsx_file)

    # print('=' * 80)
    # oo.find_path('X0', '90', 'GPIO6')
    #
    # print('=' * 80)
    # oo.find_path('X0', '143', 'GPIO7')


    pass
    # print('=' * 80)
    oo.find_path('X0', '110', 'MPP3')
    xx.path = oo.path
    xx.SYMBOL_DICT = oo.SYMBOL_DICT
    xx.draw()
    #
    # print('=' * 80)
    # oo.find_path('X0', '153', 'VREG_L3')
    #
    # print('=' * 80)
    # oo.find_path('X2', '110', 'MPP3')
    #
    # print('=' * 80)
    # oo.find_path('J6', 'T8', 'IO85')
    #
    # print('=' * 80)
    # oo.find_path('J6', 'A15', 'IO8')
    #
    # pass


    # for num, nam in oo.SYMBOL_DICT['X0'].pins:
    #
    #     for sym in oo.device_symbols:
    #         oo.find_path(sym, num, nam)
    #         print('|'.join([sym, num, nam]) + ': \t\t' + str(list(oo.get_tester_connections())))