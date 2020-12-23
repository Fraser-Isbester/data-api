import pytest

from TableDesigner.data import (
    DynAttribute
)

def test_DynAttribute():
    assert DynAttribute("MyStringAttibute", "S").asdict() == Resources.dyn_attribute_valid

class Resources:

    dyn_attribute_valid = {
        "attribute_name": "MyStringAttibute",
        "attribute_type": "S"
    }