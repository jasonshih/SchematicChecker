from src.SymbolNetsAnalyzer import PathAnalyzer


class Reporter(object):

    def __init__(self):
        pass

    @staticmethod
    def multi_site_check(oo, num_of_sites):
        az = PathAnalyzer()

        pins_dict = {}
        site_dict = {}
        for pins in ['CC1', 'CC2', 'MPP1', 'MPP2', 'GPIO6', 'GPIO7', 'VIN_GR4', 'VREG_L5', 'VREG_L16']:
            for site in ['X' + str(i) for i in range(num_of_sites)]:
                [nut] = oo.get_nodes_with_pin(symbol=site, pin=pins)

                if site == 'X0':
                    az.compile(oo.find_path(nut))
                else:
                    oo.find_path(nut)

                # print('TESTING :' + site + ' -- ' + pins)
                site_dict.update({site: az.is_multi_site_ok(oo.path_obj)})
            pins_dict.update({pins: site_dict})

        return pins_dict
                # path_to_gnd = az.get_path_to_nets(oo.path_obj, 'AGND')
                # devices = az.get_device_symbols(oo.path_obj)
                # tester = az.get_tester_nets(oo.path_obj)

                # for x in path_to_gnd:
                #     print(str(x))

                # [print(str(x)) for x in devices]
                # [print(str(x)) for x in tester]
                # print('')

    @staticmethod
    def create_channel_map(path_dict):

        az = PathAnalyzer()
        for pin, path in path_dict.items():
            resources = az.get_tester_nets(path)

            for resource in resources:
                if resource.tester_channel:
                    print(pin + ' --> ' + resource.tester_channel)
        pass