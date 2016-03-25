from src.SymbolNetsAnalyzer import PathAnalyzer


class Reporter:

    def __init__(self):
        pass

    @staticmethod
    def multi_site_check(oo, num_of_sites):
        az = PathAnalyzer()
        pins_dict = {}
        site_dict = {}
        for pin in az.iter_all_pins_in_symbol('X0', oo):
            for site in ['X' + str(i) for i in range(num_of_sites)]:
                [nut] = oo.get_nodes_with_pin(symbol=site, pin=pin)

                if site == 'X0':
                    # TODO confirm that oo.find_path here is saving the oo.path_obj
                    az.compile(oo.find_path(nut))
                else:
                    oo.find_path(nut)

                is_symmetrical = az.is_multi_site_ok(oo.path_obj)

                site_dict.update({site: is_symmetrical})
            pins_dict.update({pin: site_dict.copy()})

        return pins_dict

    @staticmethod
    def force_and_sense_check(oo):
        az = PathAnalyzer()
        big_list = az.get_uvi_force_sense_merging_point(oo.SYMBOL_DICT, oo.NETS_DICT)

    @staticmethod
    def create_channel_map(oo):
        az = PathAnalyzer()

        for pin in ['MPP1', 'MPP2', 'MPP3', 'MPP4']:
            [nut] = oo.get_nodes_with_pin('X0', pin)
            this_path = oo.find_path(nut)
            resources = az.get_tester_nets(this_path)

            for resource in resources:
                if resource.tester_channel:
                    print(pin + ' --> ' + resource.tester_channel)

    @staticmethod
    def create_dni_report(oo):
        pass

    @staticmethod
    def show_component(oo):
        pass
