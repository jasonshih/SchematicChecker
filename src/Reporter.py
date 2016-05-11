from src.Analyzer import PathAnalyzer
from collections import defaultdict
from operator import itemgetter
import logging
import re


class Reporter:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass

        # TODO: top level tests: force-sense, multi-site, channel-map, dni-list, dgs-list

    def multi_site_check(self, oo):
        self.logger.info('=== multi site check ===')

        az = PathAnalyzer()

        asymmetrical_list = []

        for pin in oo.iter_all_pins_in_symbol('X0'):

            for i, site in enumerate(oo.iter_all_device_symbols()):
                nut = oo.get_nodes_from_symbol_and_pin(symbol=site, pin=pin)
                this_path = oo.explore(nut)
                if i == 0:
                    az.compile(this_path)
                is_symmetrical = az.is_multi_site_ok(this_path)

                if not is_symmetrical:
                    asymmetrical_list.append((site, pin))

        return asymmetrical_list

    def force_and_sense_check(self, oo):
        self.logger.info('=== force and sense check ===')

        az = PathAnalyzer()
        pat = re.compile('(\w)(\w*)')
        big_list = az.get_uvi_force_sense(oo)
        disconnected = []
        for uvi_group, postfix in sorted(big_list.items()):
            for pf in postfix:
                mo = pat.match(pf)
                pre, pos = mo.group(1), mo.group(2)
                cond_1 = pre.capitalize() == 'F' and ''.join(['S', pos]) in postfix
                cond_2 = pre.capitalize() == 'S' and ''.join(['F', pos]) in postfix

                if cond_1 or cond_2:
                    pass
                else:
                    self.logger.warn('force_and_sense_check: pair not found for %s: found postfixes: %s',
                                     uvi_group + pre + pos, ', '.join(postfix))
                    disconnected.append(uvi_group + pre + pos)

        return disconnected

    def create_channel_map(self, oo):
        self.logger.info('=== creating channel map ===')

        cm = defaultdict(set)
        cm_lists = []
        for site in oo.iter_all_device_symbols():
            for pin in oo.iter_all_pins_in_symbol('X0'):

                if pin.startswith('CDC'):
                    # TODO issues on VPP, and loopback circuitry:
                    # TODO CDC_EAR_M/P, CDC_HPH_L/R, CDC_IN1_M/P, CDC_IN2_P,
                    # TODO CDC_IN3_P, CDC_LO_M/P, CDC_SPKDRV_M/P
                    continue

                nut = oo.get_nodes_from_symbol_and_pin(site, pin)
                this_path = oo.explore(nut)

                terminals = set(this_path.iter_testers_at_links)
                if 'AGND' in [x.edge.name for x in this_path.links if x.level == 0]:
                    terminals.add('AGND')

                if not terminals:
                    self.logger.warn('no tester channel assigned for pin: %s', pin)
                    cm[(pin, 'N/C')].add('_')
                else:
                    for terminal in terminals:
                        if terminal == 'AGND':
                            cm[(pin, 'GND')].add('_')
                        elif terminal.channel:
                            cm[(pin, terminal.channel.ch_type)].add(terminal.channel.ch_map)
                        else:
                            self.logger.debug('terminal.tester_channel is empty at nets: %s', terminal)

        for u, v in cm.items():
            combined = list(u)
            combined.extend(v.copy())
            cm_lists.append(combined)

        cm_lists = sorted(cm_lists, key=itemgetter(1))
        cm_lists = sorted(cm_lists, key=itemgetter(0))
        return cm_lists

    def create_dni_report(self, oo):
        self.logger.info('=== creating dni report ===')

        dni_list = [ss for symbol, ss in sorted(oo.SYMBOL_DICT.items()) if ss.dni]
        dni_dict = defaultdict(list)
        for symbol in dni_list:
            if len(symbol.pins) > 2:
                self.logger.warn('DNI of a non 2 pins component: %s', symbol.id)
            for pin, nets in symbol.pins.items():
                dni_dict[symbol.id].append(nets)
        return dni_dict

    def create_dgs_report(self):
        self.logger.info('=== creating DGS report ===')
        raise Warning('Incomplete Coding')

        # az = PathAnalyzer()
        # many_nets = oo.get_nets_which_contain('DGS')
        # for this_nets in many_nets:
        #     nuts_from_edge = oo.get_nodes_with_nets(this_nets)
        #     nuts_from_edge = [x for x in nuts_from_edge if x.symbol in oo.connector_symbols]
        #     for nut in nuts_from_edge: pass
        #         # this_path = oo.explore(nut)
        #         # self.view_pin_details(this_path)

    # def show_component(self, oo, symbol, pin):
    #     self.logger.info('=== show component ===')
    #
    #     xx = BlockVisualizer()
    #     nut = oo.get_nodes_with_pin(symbol=symbol, pin=pin)
    #     this_path = oo.explore(nut)
    #     xx.draw(this_path)

    @staticmethod
    def view_pin_details(oo, symbol, pin_name):

        def print_with_header(title, args):
            print(title)
            print('=' * 80)
            [print(x) for x in args]
            print('\v\v')

        az = PathAnalyzer()

        nut = oo.get_nodes_from_symbol_and_pin(symbol, pin_name)
        this_path = oo.explore(nut)

        pin_name = this_path.origin.pin_name
        symbol = this_path.origin.symbol
        comp_type = oo.SYMBOL_DICT[symbol].type
        print_with_header('title', [pin_name, symbol, comp_type])

        ms_ok = {}
        az.compile(this_path)
        for s in oo.iter_all_device_symbols():
            ms_nut = oo.get_nodes_from_symbol_and_pin(s, pin_name)
            ms_path = oo.explore(ms_nut)
            ms_ok.update({s: az.is_multi_site_ok(ms_path)})

        out_str = []
        for i, link in enumerate(this_path.ascii_tree()):
            out_str.append('[{num:03d}] '.format(num=i) + str(link))
        testers = set([x.name for x in this_path.iter_testers_at_links])

        print_with_header('links', out_str)
        print_with_header('multi site ok', sorted(ms_ok.items(),
                                                  key=lambda x: int(re.match('[a-zA-Z]+(\d+)', x[0]).group(1))))
        print_with_header('device pins', [x.name for x in this_path.iter_devices_at_links])
        print_with_header('channel assignments', sorted(testers))

        for tester in sorted(testers):
            subsets = this_path.create_subset_path(tester)

            relay_set = set()
            for subset in subsets:
                for k in subset.iter_active_components:
                    relay_set.add(k)

            if relay_set:
                print_with_header('relays to: %s' % tester, relay_set)
