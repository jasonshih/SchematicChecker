from pytest import fixture, skip
from src.Explorer import Explorer
from src.SchemComponent import *

@fixture()
def n():
    return SchematicNode(('symbol', '33', 'pin_name'))


def test_node_default_is_not_dni(n):
    assert not n.dni


def test_node_names(n):
    assert 'symbol|33|pin_name' == n.name
    assert 'symbol @pin_name' == n.short_name


def test_node_name_when_dni(n):
    n.set_dni()
    assert n.dni
    assert 'DNI' in n.short_name

def test_create_symbol():
    s = SchematicSymbol('RES_SHORTED_0201', 'R01')
    assert 'RES_SHORTED_0201' == s.type
    assert 'R01' == s.id
