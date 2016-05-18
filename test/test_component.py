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


def test_tester_edges():
    e_relay = SchematicEdge('UDB123')
    e_uvi = SchematicEdge('J0_UVI80_80F_A')
    e_dc30 = SchematicEdge('J20_DC30_20S')
    e_hsd = SchematicEdge('J0_HSD_123')

    assert e_relay.masked_name == 'UDB##'
    assert e_relay.channel.board_type == 'Utility'
    assert e_relay.channel.ch_type == 'Utility'
    assert e_relay.channel.ch_map == '7.util123'

    assert e_uvi.masked_name == 'J##_UVI80_##F_A'
    assert e_uvi.channel.board_type == 'DC07'
    assert e_uvi.channel.ch_type == 'DCVI'
    assert e_uvi.channel.ch_map == '0.sense80'

    assert e_dc30.masked_name == 'J##_DC30_##S'
    assert e_dc30.channel.board_type == 'DC30'
    assert e_dc30.channel.ch_type == 'DCVI'
    assert e_dc30.channel.ch_map == '20.sense20'

    assert e_hsd.masked_name == 'J##_HSD_###'
    assert e_hsd.channel.board_type == 'HSD'
    assert e_hsd.channel.ch_type == 'I/O'
    assert e_hsd.channel.ch_map == '0.ch123'


def test_non_tester_edges():

    e_hidden = SchematicEdge('$0123')
    e_site = SchematicEdge('S0_abc_def')
    e_common = SchematicEdge('unconnected')
    e_numbered = SchematicEdge('abcd_0123')

    assert e_hidden.masked_name == 'hidden'
    assert not e_hidden.channel

    assert e_site.masked_name == 'S##_abc_def'
    assert not e_site.channel

    assert e_common.masked_name == 'unconnected'
    assert not e_common.channel

    assert e_numbered.masked_name == 'abcd_'
    assert not e_numbered.channel
