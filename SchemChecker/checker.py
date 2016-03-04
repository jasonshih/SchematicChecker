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
                comp_header = str(cell.value).replace('\'', '').split(' ')

                oo = sc.SchematicComponent()

                oo.id = comp_header[2]
                oo.type = comp_header[1]

                cc = comp_header[2]

                COMP_DICT.update({oo.id:oo})

                print(comp_header)
                pass

            if "Property:" in str(cell.value):
                pass
                # print(cell.value)

            if "Explicit Pin:" in str(cell.value):
                ep = str(cell.value).strip().replace('\'','').split(' ')
                COMP_DICT[cc].pins.update({(ep[2], ep[3]):ep[4]})
                NETS_DICT.update({ep[4]:{cc:COMP_DICT[cc].id}})

                pass
                # print(cell.value)

    pass


