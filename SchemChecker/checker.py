import SchemChecker.PathFinder as pF
import SchemChecker.DrawingBoard as bV
import SchemChecker.PathAnalyzer as pA

if __name__ == "__main__":

    oo = pF.PathFinder()
    xx = bV.BlockVisualizer()
    ff = pA.PathCruncher()

    ff.is_multi_site_ok()

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo.read_xlsx(xlsx_file)
    #
    # combined_path = []
    # sep_path = {}
    #
    # # oo.find_path('X0', '90', 'GPIO6')
    # # oo.find_path('X0', '143', 'GPIO7')
    # # oo.find_path('X0', '153', 'VREG_L3')
    # # oo.find_path('X2', '110', 'MPP3')
    # # oo.find_path('J6', 'T8', 'IO85')
    # # oo.find_path('J6', 'A15', 'IO8')
    #
    # for i in ['X0', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X8']:
    #     # oo.find_path(i, '153', 'VREG_L3')
    #     oo.find_path((i, '90', 'GPIO6'))
    #     # oo.find_path((i, '143', 'GPIO7'))
    #     # oo.find_path(i, '110', 'MPP3')
    #     combined_path.extend(oo.path)
    #     sep_path.update({i: oo.path})


    # def dashrepl(matchobj):
    # ...     if matchobj.group(0) == '-': return ' '
    # ...     else: return '-'
    # >>> re.sub('-{1,2}', dashrepl, 'pro----gram-files')
    # 'pro--gram files'

    pass

    # xx.path = combined_path
    # xx.SYMBOL_DICT = oo.SYMBOL_DICT
    # xx.draw()

    # for num, nam in oo.SYMBOL_DICT['X0'].pins:
    #     for sym in oo.device_symbols:
    #         oo.find_path(sym, num, nam)
    #         print('|'.join([sym, num, nam]) + ': \t\t' + str(list(oo.get_tester_nets())))
