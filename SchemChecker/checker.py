import SchemChecker.PathFinder as pf

if __name__ == "__main__":

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    oo = pf.PathFinder()
    oo.populate_dictionaries(xlsx_file)

    # print('=' * 80)
    # oo.clear_found_ports()
    # oo.find_path('X0', '90', 'GPIO6')

    print('=' * 80)
    oo.clear_found_ports()
    oo.find_path('X0', '143', 'GPIO7')

    # print('=' * 80)
    # oo.clear_found_ports()
    # oo.find_path('X0', '110', 'MPP3')
    #
    # print('=' * 80)
    # oo.clear_found_ports()
    # oo.find_path('X2', '110', 'MPP3')
    #
    # print('=' * 80)
    # oo.clear_found_ports()
    # oo.find_path('J6', 'T8', 'IO85')

    print('=' * 80)
    oo.clear_found_ports()
    oo.find_path('J6', 'A15', 'IO8')
    pass