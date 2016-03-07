import SchemChecker.SchemComponent as sc
from openpyxl import load_workbook


class PathFinder(object):

    def __init__(self):
        self.SYMBOL_DICT = {}
        self.NETS_DICT = {}
        self.COMP_DICT = {}
        self.seen = []

    def populate_dictionaries(self, file_name):
        wb = load_workbook(file_name)
        ws = wb.get_active_sheet()

        self.SYMBOL_DICT = {}
        self.NETS_DICT = {}
        self.COMP_DICT = self.populate_component()
        cc = ''

        for row in ws.rows:
            for cell in row:
                if "COMP:" in str(cell.value):
                    ch = str(cell.value).replace('\'', '').split(' ')

                    if len(ch) == 3:
                        oo = sc.SchematicSymbol()
                        [_, oo.type, oo.id] = ch

                        if oo.type in self.COMP_DICT.keys():
                            oo.links = self.COMP_DICT[oo.type].links
                        else:
                            oo.links = {}

                        self.SYMBOL_DICT.update({oo.id: oo})

                        cc = oo.id
                        print(ch)

                if "Property:" in str(cell.value):
                    pass

                if "Explicit Pin:" in str(cell.value):
                    ep = str(cell.value).strip().replace('\'', '').split(' ')
                    if len(ep) == 5:
                        [_, _, pin_num, pin_name, nets] = ep
                        self.SYMBOL_DICT[cc].pins.update({(pin_num, pin_name): nets})

                        if nets in self.NETS_DICT.keys():
                            self.NETS_DICT[nets].append((cc, pin_num, pin_name))
                        else:
                            self.NETS_DICT.update({nets: [(cc, pin_num, pin_name)]})

    def populate_component(self):

        comp_dict = {
            '300-23460-0237': sc.SchematicComponent(),
            '100-46302-2491': sc.SchematicComponent(),
            '100-46312-0000': sc.SchematicComponent(),
            'EMBEDDED_SHORTING_BAR': sc.SchematicComponent()
        }

        # 8-pins RELAY
        comp_dict['300-23460-0237'].links.update({
            'off': {('1', 'N1'): [('8', 'N2')],
                    ('2', 'S1'): [('3', 'COM1')],
                    ('3', 'COM1'): [('2', 'S1')],
                    ('4', 'S2'): [],
                    ('5', 'S4'): [],
                    ('6', 'COM2'): [('7', 'S3')],
                    ('7', 'S3'): [('6', 'COM2')],
                    ('8', 'N2'): [('1', 'N1')]}
            })
        comp_dict['300-23460-0237'].links.update({
            'on': {('1', 'N1'): [('8', 'N2')],
                   ('2', 'S1'): [],
                   ('3', 'COM1'): [('4', 'S2')],
                   ('4', 'S2'): [('3', 'COM1')],
                   ('5', 'S4'): [('6', 'COM2')],
                   ('6', 'COM2'): [('5', 'S4')],
                   ('7', 'S3'): [],
                   ('8', 'N2'): [('1', 'N1')]}
            })

        # 2-pins RESISTOR
        comp_dict['100-46302-2491'].links.update({
            'passive': {('1', 'POS'): [('2', 'NEG')],
                        ('2', 'NEG'): [('1', 'POS')]}
        })

        comp_dict['100-46312-0000'].links.update({
            'passive': {('1', 'POS'): [('2', 'NEG')],
                        ('2', 'NEG'): [('1', 'POS')]}
        })
        # jumper
        comp_dict['EMBEDDED_SHORTING_BAR'].links.update({
            'passive': {('1', 'IO1'): [('2', 'IO2')],
                        ('2', 'IO2'): [('1', 'IO1')]}
        })

        return comp_dict

    def find_path(self, symbol, pin_num_and_name, state=None, path=None):
        if path is None:
            path = []

        if state is None:
            state = 'passive'

        (pin_num, pin_name) = pin_num_and_name
        self.seen.append((symbol, pin_num, pin_name))

        nets = self.SYMBOL_DICT[symbol].pins[pin_num_and_name]                  #S0_GPIO6
        ports_at_nets = self.NETS_DICT[nets]                                    #[('X0', '90', 'GPIO6'),
                                                                                # ('R43A', '1', 'POS')]
        filtered_ports = self.remove_previous_ports(ports_at_nets, self.seen)   #[('R43A', '1', 'POS')]
        processed_ports = self.process_ports(filtered_ports)                    #[('R43A', '2', 'NEG')]

        path.append(nets)

        if processed_ports:
            for (symbol, _, pin_num, pin_name) in processed_ports:
                self.find_path(symbol, (pin_num, pin_name), path=path)
        else:
            pass
            #freeze this path
        pass

    def remove_previous_ports(self, ports, seen=None):
        if seen is None:
            seen = []
        return [x for x in ports if x not in seen]

    def process_ports(self, ports):

        all_linked_ports = []
        for each_port in ports:
            (symbol, port_num, port_name) = each_port

            states = self.SYMBOL_DICT[symbol].links.keys()

            for state in states:
                linked_ports = self.SYMBOL_DICT[symbol].links[state][(port_num, port_name)]
                linked_ports = [(symbol, state, x, y) for (x, y) in linked_ports]
                all_linked_ports.extend(linked_ports)

        return all_linked_ports


def populate_component():

    COMP_DICT = {
        '300-23460-0237': sc.SchematicComponent(),
        '100-46302-2491': sc.SchematicComponent(),
        '100-46312-0000': sc.SchematicComponent(),
        'EMBEDDED_SHORTING_BAR': sc.SchematicComponent()
    }

    # 8-pins RELAY
    COMP_DICT['300-23460-0237'].links.update({
        'off': {('1', 'N1'): [('8', 'N2')],
                ('2', 'S1'): [('3', 'COM1')],
                ('3', 'COM1'): [('2', 'S1')],
                ('4', 'S2'): [],
                ('5', 'S4'): [],
                ('6', 'COM2'): [('7', 'S3')],
                ('7', 'S3'): [('6', 'COM2')],
                ('8', 'N2'): [('1', 'N1')]}
        })
    COMP_DICT['300-23460-0237'].links.update({
        'on': {('1', 'N1'): [('8', 'N2')],
               ('2', 'S1'): [],
               ('3', 'COM1'): [('4', 'S2')],
               ('4', 'S2'): [('3', 'COM1')],
               ('5', 'S4'): [('6', 'COM2')],
               ('6', 'COM2'): [('5', 'S4')],
               ('7', 'S3'): [],
               ('8', 'N2'): [('1', 'N1')]}
        })

    # 2-pins RESISTOR
    COMP_DICT['100-46302-2491'].links.update({
        'passive': {('1', 'POS'): [('2', 'NEG')],
                    ('2', 'NEG'): [('1', 'POS')]}
    })

    COMP_DICT['100-46312-0000'].links.update({
        'passive': {('1', 'POS'): [('2', 'NEG')],
                    ('2', 'NEG'): [('1', 'POS')]}
    })
    # jumper
    COMP_DICT['EMBEDDED_SHORTING_BAR'].links.update({
        'passive': {('1', 'IO1'): [('2', 'IO2')],
                    ('2', 'IO2'): [('1', 'IO1')]}
    })

    return COMP_DICT


if __name__ == "__main__":

    # wb = load_workbook('/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx')
    #
    # ws = wb.get_active_sheet()
    #
    # SYMBOL_DICT = {}
    # NETS_DICT = {}
    # COMP_DICT = populate_component()
    # cc = ''
    #
    # for row in ws.rows:
    #     for cell in row:
    #         if "COMP:" in str(cell.value):
    #             ch = str(cell.value).replace('\'', '').split(' ')
    #
    #             if len(ch) == 3:
    #                 oo = sc.SchematicSymbol()
    #                 [_, oo.type, oo.id] = ch
    #
    #                 if oo.type in COMP_DICT.keys():
    #                     oo.links = COMP_DICT[oo.type].links
    #                 else:
    #                     oo.links = {}
    #
    #                 SYMBOL_DICT.update({oo.id: oo})
    #
    #                 cc = oo.id
    #                 print(ch)
    #
    #         if "Property:" in str(cell.value):
    #             pass
    #             # print(cell.value)
    #
    #         if "Explicit Pin:" in str(cell.value):
    #             ep = str(cell.value).strip().replace('\'', '').split(' ')
    #
    #             if len(ep) == 5:
    #                 [_, _, pin_num, pin_name, nets] = ep
    #
    #                 SYMBOL_DICT[cc].pins.update({(pin_num, pin_name): nets})
    #
    #                 if nets in NETS_DICT.keys():
    #                     NETS_DICT[nets].append((cc, pin_num, pin_name))
    #                 else:
    #                     NETS_DICT.update({nets: [(cc, pin_num, pin_name)]})
    #                 # print(cell.value)

    xlsx_file = '/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx'
    pf = PathFinder()
    pf.populate_dictionaries(xlsx_file)
    pf.find_path('X0', ('90', 'GPIO6'))
    pass

'''
    SYMBOL_DICT['X0'].pins[('90', 'GPIO6')]     #S0_GPIO6
    NETS_DICT['S0_GPIO6']                       #[('X0', '90', 'GPIO6'), ('R43A', '1', 'POS')]
    --> [('R43A', '1', 'POS')]
    --> [('R43A', 'passive', '2', 'NEG')]

        SYMBOL_DICT['R43A'].pins[('2', 'NEG')]      #J16_HSD_156
        NETS_DICT['J16_HSD_156']                    #[('J6', 'R12', 'IO68'), ('R43A', '2', 'NEG')]
        --> [('J6', 'R12', 'IO68')]
        --> [done]
        PATH: ['S0_GPIO6', 'J16_HSD_156']

    ==============================================================================================================
    SYMBOL_DICT['X0'].pins['143', 'GPIO7']      #S0_GPIO7
    NETS_DICT['S0_GPIO7']                       #[('X0', '143', 'GPIO7'), ('K1A', '3', 'COM1')]
    remove_prev_ports() --> [('K1A', '3', 'COM1')]
    process_ports() --> [('K1A', '2', 'S1'), ('K1A', '4', 'S2')]
    seen_ports --> [('X0', '143', 'GPIO7'), ('K1A', '3', 'COM1'),
                    ('K1A', '2', 'S1'), ('K1A', '4', 'S2')]

        SYMBOL_DICT['K1A'].pins['2', 'S1']          #J16_HSD_157
        NETS_DICT['J16_HSD_157']                    #[('K1A', '2', 'S1'), ('J6', 'R10', 'IO67')]
        remove_prev_ports()--> [('J6', 'R10', 'IO67')]
        --> [done]
        seen_ports --> [('X0', '143', 'GPIO7'), ('K1A', '3', 'COM1'),
                        ('K1A', '2', 'S1'), ('J6', 'R10', 'IO67')]

        PATH: ['S0_GPIO7', 'J16_HSD_157']


        SYMBOL_DICT['K1A'].pins['4', 'S2']          #$5N2423_110
        NETS_DICT['$5N2423_110']                    #[('K1A', '4', 'S2'), ('R121A', '2', 'NEG')]
        remove_prev_ports() --> [('R121A', '2', 'NEG')]
        --> [('R121A', '1', 'POS')]
        seen_ports --> [('X0', '143', 'GPIO7'), ('K1A', '3', 'COM1'),
                        ('K1A', '4', 'S2'), ('R121A', '2', 'NEG'),
                        ('R121A', '1', 'POS')]

            SYMBOL_DICT['R121A'].pins['1', 'POS']       #S0_UVI80_GPIO7
            NETS_DICT['S0_UVI80_GPIO7']                 #[('K92', '7', 'S3'), ('K92', '2', 'S1'), ('R121A', '1', 'POS')]
            --> [('K92', '7', 'S3'), ('K92', '2', 'S1')]
            --> [('K92', '6', 'COM2'), ('K92', '3', 'COM1')]
            seen_ports --> [('X0', '143', 'GPIO7'), ('K1A', '3', 'COM1'),
                            ('K1A', '4', 'S2'), ('R121A', '2', 'NEG'),
                            ('R121A', '1', 'POS'),
                            ('K92', '7', 'S3'), ('K92', '2', 'S1'), ('R121A', '1', 'POS'),
                            ('K92', '6', 'COM2'), ('K92', '3', 'COM1')]


                SYMBOL_DICT['K92'].pins['6', 'COM2']        #J20_UVI80_4F
                NETS_DICT['J20_UVI80_4F']                   #[('K92', '6', 'COM2'),
                                                             ('K92', '3', 'COM1'),
                                                             ('JP601', '2', 'IO2'),
                                                             ('J6', 'A15', 'IO8'),
                                                             ('J6', 'A13', 'IO7')]

                -->[('JP601', '2', 'IO2'), ('J6', 'A15', 'IO8'), ('J6', 'A13', 'IO7')]
                -->[('JP601', '1', 'IO1'), done, done]
                PATH: ['S0_GPIO7', '$5N2423_110', 'S0_UVI80_GPIO7', 'J20_UVI80_4F' ]

                    SYMBOL_DICT['JP601'].pins['1', 'IO1']       #J20_UVI80_4S
                    NETS_DICT['J20_UVI80_4S']                   #[('JP601', '1', 'IO1'), ('J6', 'B14', 'IO17')]
                    --> [('J6', 'B14', 'IO17')]
                    --> [done]
                    PATH: ['S0_GPIO7', '$5N2423_110', 'S0_UVI80_GPIO7', 'J20_UVI80_4F', 'J20_UVI80_4S' ]

                SYMBOL_DICT['K92'].pins['3', 'COM1']        #J20_UVI80_4F
                NETS_DICT['J20_UVI80_4F']                   #[('K92', '6', 'COM2'),
                                                             ('K92', '3', 'COM1'),
                                                             ('JP601', '2', 'IO2'),
                                                             ('J6', 'A15', 'IO8'),
                                                             ('J6', 'A13', 'IO7')]
                --> []
                --> loop



'''
