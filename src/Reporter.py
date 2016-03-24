from src.PathFinder import PathFinder
from src.DrawingBoard import BlockVisualizer
from src.SymbolNetsAnalyzer import PathTester


class Reporter(object):

    def __init__(self):
        pass

    def check_all_sites(self, oo, ff, xx):

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

    def create_channel_map(self, path_dict):

        ff = PathTester()
        for pin, path in path_dict.items():
            resources = ff.get_tester_nets(path)

            for resource in resources:
                if resource.tester_channel:
                    print(pin + ' --> ' + resource.tester_channel)
        pass