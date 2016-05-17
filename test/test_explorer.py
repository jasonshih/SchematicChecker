from pytest import fixture, skip
from src.Explorer import Explorer
from src.SchemComponent import *


@fixture
def e():
    return Explorer()


def test_has_functions(e):
    assert hasattr(e, 'explore')


def test_has_imported_functions_from_another_class(e):
    assert hasattr(e, 'read_xlsx')


def test_has_imported_function_from_component_modules(e):
    assert hasattr(e, 'connector_symbols')
    assert hasattr(e, 'device_symbols')
    assert hasattr(e, 'plane_symbols')
    assert hasattr(e, 'terminal_symbols')
    assert hasattr(e, 'special_nets')


def test_has_imported_functions_from_utility_module(e):
    assert hasattr(e, 'iter_all_pins_in_symbol')
    assert hasattr(e, 'iter_all_device_symbols')
    assert hasattr(e, 'search_pins_or_nets')
    assert hasattr(e, 'get_nodes_from_symbol_and_nets')
    assert hasattr(e, 'get_nodes_from_symbol_and_pin')
    assert hasattr(e, 'get_nodes_from_nets')
    assert hasattr(e, 'get_nets_which_contain')
    assert hasattr(e, 'get_nets_count')


class TestSimpleLink:

    def setup_class(self):

        self.e = Explorer()

        # RESISTOR
        self.r = self.e.SYMBOL_DICT['R01'] = SchematicSymbol('RES_SHORTED_0201', 'R01')
        self.r.pins[('1', 'POS')] = '$0123'
        self.r.pins[('2', 'NEG')] = 'AGND'

        # JUMPER
        self.j = self.e.SYMBOL_DICT['JP01'] = SchematicSymbol('EMBEDDED_SHORTING_BAR', 'JP01')
        self.j.pins[('1', 'IO1')] = '$0123'
        self.j.pins[('2', 'IO2')] = '$1234'

        # RELAY
        self.k = self.e.SYMBOL_DICT['K01'] = SchematicSymbol('300-23460-0237', 'JP01')
        self.k.pins[('1', 'N1')] = '+5V'
        self.k.pins[('2', 'S1')] = 'J2_DC30_1F'
        self.k.pins[('3', 'COM1')] = '$1234'
        self.k.pins[('4', 'S2')] = 'grounded_diode'
        self.k.pins[('5', 'S4')] = None
        self.k.pins[('6', 'COM2')] = None
        self.k.pins[('7', 'S3')] = None
        self.k.pins[('8', 'N2')] = 'AGND'

        # TESTER
        self.t = self.e.SYMBOL_DICT['J01'] = SchematicSymbol('MATE_TO_INTEGRA_FLEX_PROBE_02', 'J01')
        self.t.pins[('Z1', 'IO321')] = 'J2_DC30_1F'

        # DIODE
        self.d = self.e.SYMBOL_DICT['CR1'] = SchematicSymbol('2PSM79X53F', 'CR1')
        self.d.pins[('1', 'NEG')] = 'grounded_diode'
        self.d.pins[('2', 'POS')] = 'AGND'

        # NETS
        self.e.NETS_DICT['$0123'] = [('R01', '1', 'POS'), ('JP01', '1', 'IO1')]
        self.e.NETS_DICT['$1234'] = [('JP01', '2', 'IO2'), ('K01', '3', 'COM1')]
        self.e.NETS_DICT['J2_DC30_1F'] = [('J01', 'Z1', 'IO321'), ('K01', '2', 'S1')]
        self.e.NETS_DICT['grounded_diode'] = [('CR1', '1', 'NEG'), ('K01', '4', 'S2')]

        self.tail = SchematicNode(('R01', '1', 'POS'))

        self.p = self.e.explore(self.tail)

        # print('\v')
        # for i, link in enumerate(self.p.ascii_tree()):
        #     print('[{num:03d}] '.format(num=i) + str(link))
        # print('\v')
        #
        # for i, link in enumerate(sorted(self.p.links, key=lambda x: x.level)):
        #     print('[{num:03d}] '.format(num=i) + str(link))
        # print('\v')

    def test_explorer_vars(self):
        # assert set(self.e.explored_links) == set()
        # assert set(self.e.seen_nodes) == {'R01|1|POS', 'JP01|2|IO2', 'K01|2|S1', 'K01|4|S2'}
        assert self.e._lvl == 0

    def test_returning_schematic_path(self):
        assert isinstance(self.p, SchematicPath)

    def test_links_created(self):
        assert hasattr(self.p, 'links')
        assert isinstance(self.p.links, list)
        assert isinstance(self.p.links[0], SchematicLink)

    def test_links_length(self):
        assert len(self.p.links) == 7

    def test_links_levels(self):
        lut = sorted(self.p.links, key=lambda x: x.level)
        assert lut[0].level == 0
        assert lut[1].level == 1
        assert lut[2].level == 2
        assert lut[3].level == 3
        assert lut[4].level == 3
        assert lut[5].level == 4
        assert lut[6].level == 4

    def test_links_terminals(self):
        for lut in self.p.links:
            if 'J01' in lut.head.name:
                assert lut.head.is_terminal
            else:
                assert not lut.head.is_terminal

    def test_links_internal(self):
        for lut in self.p.links:
            if lut.head.symbol == lut.tail.symbol:
                assert lut.is_internal
            else:
                assert not lut.is_internal

    def test_links_active_heads(self):
        for lut in self.p.links:
            if 'K01' in lut.head.name:
                assert lut.head.is_active
            else:
                assert not lut.head.is_active

    def test_links_active_tails(self):
        for lut in self.p.links:
            if 'K01' in lut.tail.name:
                assert lut.tail.is_active
            else:
                assert not lut.tail.is_active

    def test_links_tester_channel(self):
        for lut in self.p.links:
            if 'J01' in lut.head.name:
                assert lut.edge.channel.ch_map == '2.sense1'
                assert lut.edge.channel.ch_type == 'DCVI'
                assert lut.edge.channel.board_type == 'DC30'
                assert lut.edge.masked_name == 'J2_DC30_1F'
            else:
                assert not lut.edge.channel
