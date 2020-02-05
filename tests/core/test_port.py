"""Tests for the `Port` class."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import pytest
from marmot import Environment

from ORBIT.core import Port, Cargo
from ORBIT.core.exceptions import ItemNotFound


class TestItem(Cargo):
    def __init__(self):
        pass


def test_port_creation():

    env = Environment()
    port = Port(env)
    item = TestItem()

    port.put(item)
    port.put(item)

    items = [item for item in port.items if item.type == "TestItem"]
    assert len(items) == 2


def test_get_item():

    env = Environment()
    port = Port(env)
    item = TestItem()

    port.put(item)
    port.put(item)

    returned = port.get_item("TestItem")
    assert returned == item
    assert len(port.items) == 1

    port.put({"type": "Not type Cargo"})
    with pytest.raises(ItemNotFound):
        _ = port.get_item("WrongItem")

    _ = port.get_item("TestItem")
    with pytest.raises(ItemNotFound):
        _ = port.get_item("TestItem")
