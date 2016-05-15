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
    assert hasattr(e, 'search_pins_or_nets')


def test_simple_link(e):
    r = e.SYMBOL_DICT['R01'] = SchematicSymbol('RES_SHORTED_0201', 'R01')
    r.pins[('1', 'POS')] = '$0123'
    r.pins[('2', 'NEG')] = 'AGND'

    j = e.SYMBOL_DICT['JP01'] = SchematicSymbol('EMBEDDED_SHORTING_BAR', 'JP01')
    j.pins[('1', 'IO1')] = '$0123'
    j.pins[('2', 'IO2')] = 'AGND'

    e.NETS_DICT['$0123'] = [('R01', '1', 'POS'), ('JP01', '1', 'IO1')]

    assert isinstance(e.explore(SchematicNode(('R01', '1', 'POS'))), SchematicPath)
