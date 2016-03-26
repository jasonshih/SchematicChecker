from src.Analyzer import PathAnalyzer
from collections import defaultdict
from operator import itemgetter
import logging


class Reporter:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass

    def multi_site_check(self, oo):
        self.logger.setLevel(logging.DEBUG)
        az = PathAnalyzer()
        pins_dict = {}
        site_dict = {}
        for pin in az.iter_all_pins_in_symbol('X0', oo):

            if pin.startswith('CDC'):
                # TODO find out why CDC pins are all showing mismatched
                continue

            for i, site in enumerate(az.iter_all_device_symbols(oo)):
                [nut] = oo.get_nodes_with_pin(symbol=site, pin=pin)
                pw = oo.explore(nut)

                if i == 0:
                    az.compile(pw)
                is_symmetrical = az.is_multi_site_ok(pw)

                site_dict.update({site: is_symmetrical})
            pins_dict.update({pin: site_dict.copy()})

        self.logger.setLevel(logging.INFO)
        return pins_dict

    @staticmethod
    def force_and_sense_check(oo):
        pass
        # az = PathAnalyzer()
        # big_list = az.get_uvi_force_sense_merging_point(oo.SYMBOL_DICT, oo.NETS_DICT)

    def create_channel_map(self, oo):
        az = PathAnalyzer()

        cm = defaultdict(list)
        cm_lists = []

        # for site in ['X0', 'X1']:
        for site in az.iter_all_device_symbols(oo):
            for pin in az.iter_all_pins_in_symbol('X0', oo):

                if pin.startswith('CDC'):
                    # TODO find out why CDC_LO_M and _P are messed up.
                    continue

                [nut] = oo.get_nodes_with_pin(site, pin)
                this_path = oo.explore(nut)

                resources = this_path.subset.keys()

                if 'MPP' in pin:
                    pass

                if not resources:
                    self.logger.warn('no tester channel assigned for pin: %s', pin)
                    cm[(pin, 'N/C')].append('_')
                else:
                    for resource in resources:
                        # TODO fix the 0 0 -1 -1 below.
                        edge_obj = this_path.subset[resource][0][0][-1][-1]
                        if resource == 'AGND' and len(resources) == 1:
                            cm[(pin, 'GND')].append('_')
                        elif edge_obj.pin_channel:
                            cm[(pin, edge_obj.pin_type)].append(edge_obj.pin_channel)
                        else:
                            self.logger.debug('resource.tester_channel is empty at nets: %s', resource)

        for u, v in cm.items():
            combined = list(u)
            combined.extend(v.copy())
            cm_lists.append(combined)

        cm_lists = sorted(cm_lists, key=itemgetter(1))
        cm_lists = sorted(cm_lists, key=itemgetter(0))
        [print(x) for x in cm_lists]

    @staticmethod
    def create_dni_report(oo):
        pass

    @staticmethod
    def show_component(oo):
        pass
