import SchemChecker.SchemComponent as sc
from openpyxl import Workbook, load_workbook


if __name__ == "__main__":

    wb = load_workbook('/Users/cahyo/Dropbox/programming/python/SchematicChecker/input_files/P1495_sample.xlsx')

    ws = wb.get_active_sheet()

    COMP_DICT = {}
    NETS_DICT = {}
    cc = ''

    for row in ws.rows:
        for cell in row:
            if "COMP:" in str(cell.value):
                ch = str(cell.value).replace('\'', '').split(' ')

                if len(ch) == 3:
                    oo = sc.SchematicComponent()
                    [_, oo.type, oo.id] = ch
                    cc = oo.id

                    COMP_DICT.update({oo.id:oo})
                    print(ch)

            if "Property:" in str(cell.value):
                pass
                # print(cell.value)

            if "Explicit Pin:" in str(cell.value):
                ep = str(cell.value).strip().replace('\'','').split(' ')

                if len(ep) == 5:
                    [_, _, pin_num, pin_name, nets] = ep

                    COMP_DICT[cc].pins.update({(pin_num, pin_name):nets})


                    if nets in NETS_DICT.keys():
                        NETS_DICT[nets].append((cc, pin_num, pin_name))
                    else:
                        NETS_DICT.update({nets:[(cc, pin_num, pin_name)]})
                    # print(cell.value)

    pass


