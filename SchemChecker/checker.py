import SchemChecker.SchemComponent as sc
from openpyxl import Workbook, load_workbook


def populate_component():

    COMP_DICT = {
        '300-23460-0237': sc.SchematicComponent(),
        '100-46302-2491': sc.SchematicComponent()
    }

    # 8-pins RELAY
    COMP_DICT['300-23460-0237'].links.update({
        'on':[(('5' 'S4'), ('6' 'COM2')),
              (('5' 'S4'), ('6' 'COM2'))]
    })
    COMP_DICT['300-23460-0237'].links.update({
        'off':[(('5' 'S4'), ('6' 'COM2')),
               (('5' 'S4'), ('6' 'COM2'))]
    })

    # 2-pins RESISTOR
    COMP_DICT['100-46302-2491'].links.update({
        'passive':[(('5' 'S4'), ('6' 'COM2'))]
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


