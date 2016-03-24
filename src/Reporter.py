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

                is_symmetrical = az.is_multi_site_ok(oo.path_obj)
                site_dict.update({site: is_symmetrical})
            pins_dict.update({pins: site_dict.copy()})

        return pins_dict

    @staticmethod
    def create_channel_map(path_dict):

        az = PathAnalyzer()
        for pin, path in path_dict.items():
            resources = az.get_tester_nets(path)

            for resource in resources:
                if resource.tester_channel:
                    print(pin + ' --> ' + resource.tester_channel)

    @staticmethod
    def create_dni_report(path_dict):
        pass
