import SchemChecker.SchemComponent as sc
from openpyxl import Workbook, load_workbook


def populate_component():

    COMP_DICT = {
        '300-23460-0237': sc.SchematicComponent(),
        '100-46302-2491': sc.SchematicComponent()
    }

    # 8-pins RELAY
    COMP_DICT['300-23460-0237'].links.update({
        'off':[(('3' 'COM1'), ('2' 'S1')),
              (('6' 'COM2'), ('7' 'S3'))]
    })
    COMP_DICT['300-23460-0237'].links.update({
        'on':[(('3' 'COM1'), ('4' 'S2')),
               (('6' 'COM2'), ('5' 'S4'))]
    })

    # 2-pins RESISTOR
    COMP_DICT['100-46302-2491'].links.update({
        'passive':[(('1' 'POS'), ('2' 'NEG'))]
    })

    return COMP_DICT


if __name__ == "__main__":

    wb = load_workbook('/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx')

    ws = wb.get_active_sheet()

    SYMBOL_DICT = {}
    NETS_DICT = {}
    COMP_DICT = populate_component()
    cc = ''

    for row in ws.rows:
        for cell in row:
            if "COMP:" in str(cell.value):
                ch = str(cell.value).replace('\'', '').split(' ')

                if len(ch) == 3:
                    oo = sc.SchematicSymbol()
                    [_, oo.type, oo.id] = ch

                    if oo.type in COMP_DICT.keys():
                        oo.links = COMP_DICT[oo.type].links
                    else:
                        oo.links = {}

                    SYMBOL_DICT.update({oo.id:oo})

                    cc = oo.id
                    print(ch)

            if "Property:" in str(cell.value):
                pass
                # print(cell.value)

            if "Explicit Pin:" in str(cell.value):
                ep = str(cell.value).strip().replace('\'','').split(' ')

                if len(ep) == 5:
                    [_, _, pin_num, pin_name, nets] = ep

                    SYMBOL_DICT[cc].pins.update({(pin_num, pin_name):nets})

                    if nets in NETS_DICT.keys():
                        NETS_DICT[nets].append((cc, pin_num, pin_name))
                    else:
                        NETS_DICT.update({nets:[(cc, pin_num, pin_name)]})
                    # print(cell.value)

    pass

'''
    SYMBOL_DICT['X0'].pins[('90', 'GPIO6')]     #S0_GPIO6
    NETS_DICT['S0_GPIO6']                       #[('X0', '90', 'GPIO6'), ('R43A', '1', 'POS')]
    --> [('R43A', '1', 'POS')]
    --> [('R43A', '2', 'NEG')]

        SYMBOL_DICT['R43A'].pins[('2', 'NEG')]      #J16_HSD_156
        NETS_DICT['J16_HSD_156']                    #[('J6', 'R12', 'IO68'), ('R43A', '2', 'NEG')]
        --> [('J6', 'R12', 'IO68')]
        --> [done]
        PATH: ['S0_GPIO6', 'J16_HSD_156']

    ==============================================================================================================
    SYMBOL_DICT['X0'].pins['143', 'GPIO7']      #S0_GPIO7
    NETS_DICT['S0_GPIO7']                       #[('X0', '143', 'GPIO7'), ('K1A', '3', 'COM1')]
    --> [('K1A', '3', 'COM1')]
    --> [('K1A', '2', 'S1'), ('K1A', '4', 'S2')]

        SYMBOL_DICT['K1A'].pins['2', 'S1']          #J16_HSD_157
        NETS_DICT['J16_HSD_157']                    #[('K1A', '2', 'S1'), ('J6', 'R10', 'IO67')]
        --> [('J6', 'R10', 'IO67')]
        --> [done]
        PATH: ['S0_GPIO7', 'J16_HSD_157']


        SYMBOL_DICT['K1A'].pins['4', 'S2']          #$5N2423_110
        NETS_DICT['$5N2423_110']                    #[('K1A', '4', 'S2'), ('R121A', '2', 'NEG')]
        --> [('R121A', '2', 'NEG')]
        --> [('R121A', '1', 'POS')]

            SYMBOL_DICT['R121A'].pins['1', 'POS']       #S0_UVI80_GPIO7
            NETS_DICT['S0_UVI80_GPIO7']                 #[('K92', '7', 'S3'), ('K92', '2', 'S1'), ('R121A', '1', 'POS')]
            --> [('K92', '7', 'S3'), ('K92', '2', 'S1')]
            --> [('K92', '6', 'COM2'), ('K92', '3', 'COM1')]

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
