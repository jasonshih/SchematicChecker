from src.Analyzer import PathAnalyzer
from src.SchemComponent import *
import logging


class Reporter:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass

    @staticmethod
    def multi_site_check(oo):
        az = PathAnalyzer()
        pins_dict = {}
        site_dict = {}
        for pin in az.iter_all_pins_in_symbol('X0', oo):
            # for site in ('X' + str(i) for i in range(4)):
            for site in az.iter_all_device_symbols(oo):
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

    def create_channel_map(self, oo):
        az = PathAnalyzer()

        for pin in az.iter_all_pins_in_symbol('X0', oo):
            for site in az.iter_all_device_symbols(oo):

                if pin.startswith('CDC'):
                    continue

                [nut] = oo.get_nodes_with_pin(site, pin)
                this_path = oo.find_path(nut)

                if 'MPP' in pin:
                    zz = SchematicPath(this_path)
                    zz.populate_subset(az)
                    pass
                # TODO consider returning an iterator
                resources = az.get_tester_nets(this_path)
                resources = list(filter(lambda x: x.pin_type != 'N/C', resources))

                if not resources:
                    self.logger.warn('no tester channel assigned for pin: %s', pin)

                for resource in resources:
                    if resource.pin_channel:
                        print('\t\t'.join([pin, site, resource.pin_type, resource.pin_channel]))
                    else:
                        self.logger.warn('resource.tester_channel is empty at nets: %s', resource)
        # {vbt_pin: [pin_name, pin_type, site0, *]}

    @staticmethod
    def create_dni_report(oo):
        pass

    @staticmethod
    def show_component(oo):
        pass
