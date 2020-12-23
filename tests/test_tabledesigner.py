import pytest

from TableDesigner.design_dev import Maps, Schema
# from TableDesigner.design_dev import Schema


# Sanity
def test_true():
    assert True

# # Tests # #
def test_type_map():
    assert Maps.PyToDyn["string"] == "S", "'String' should cast to 'S'"
    assert Maps.PyToDyn["number"] == "N", "'Number' should cast to 'N'"
    assert Maps.PyToDyn["dict"] == "M", "'Dict' should cast to 'M'"

# def test_schema_valid():
#     print(Resources.SimpleSchema.valid)
#     _ = Schema(Resources.SimpleSchema.valid)

def test_schema_invalid():
    with pytest.raises(KeyError):
        _ = Schema(Resources.SimpleSchema.missing_prop)
        _ = Schema(Resources.SimpleSchema.bad_prop)
        _ = Schema(Resources.SimpleSchema.missing_title)
        _ = Schema(Resources.SimpleSchema.bad_title)


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