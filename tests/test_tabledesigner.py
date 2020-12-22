import pytest

from design_dev import Maps
from design_dev import Schema


# Sanity
def test_true():
    assert True

# # Tests # #
def test_type_map():
    assert Maps.PyToDyn["string"] == "S", "'String' should cast to 'S'"
    assert Maps.PyToDyn["number"] == "N", "'Number' should cast to 'N'"
    assert Maps.PyToDyn["dict"] == "M", "'Dict' should cast to 'M'"

def test_schema_valid():
    s = Schema(Resources.SimpleSchema.valid)

def test_schema_invalid():
    with pytest.raises(KeyError):
        a = Schema(Resources.SimpleSchema.missing_prop)
        b = Schema(Resources.SimpleSchema.bad_prop)
        c = Schema(Resources.SimpleSchema.missing_title)
        d = Schema(Resources.SimpleSchema.bad_title)


class Resources:

    class SimpleSchema:
        valid = {
            "properties": {},
            "title": "A String"
        }
        missing_prop = {
            "title": "A String"
        }
        bad_prop = {
            "Properties": {},
            "title": "A String"
        }
        missing_title = {
            "properties": {},
        }
        bad_title = {
            "Title": "A String"
        }