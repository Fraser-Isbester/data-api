import json
from dataclasses import asdict
from .data import *

class Maps:
    PyToDyn = {
        "string": "S",
        "number": "N",
        "integer": "N",
        "float": "N",
        "list": "L",
        "bool": "BOOL",
        "boolean": "BOOL",
        "dict": "M",
        "object": "M",
        "bytes": "B",
        None: "NULL"
    }


class Schema(object):

    def __init__(self, schema):
        self.schema = schema
        self._validate_schema()

    def _validate_schema(self):
        if not self.schema.get("properties", None):
            raise KeyError("Attribute: 'properties' missing from schema")
        if not self.schema.get("title", None):
            raise KeyError("Attribute: 'title' missing from schema")


class EntitySchema(Schema):

    MaxLSI = 3
    MaxGSI = 10

    def __init__(self, *args, **kwargs):
        super(EntitySchema, self).__init__(*args, **kwargs)
        self._validate_keys()
        self._validate_filtersort()

    def _validate_keys(self):
        if not self.schema["properties"].get("pk", None):
            raise KeyError("Expected 'pk' attribute to use as Key in schema")
        if not self.schema["properties"].get("sk", None):
            raise KeyError("Expected 'sk' attribute to use as Key in schema")

    def _validate_filtersort(self):
        filtersort_count = 0
        for name, meta in self.schema["properties"].items():
            filtersort_count += 1 if meta.get("filtersort") else 0
        assert filtersort_count <= self.MaxLSI, f"Entities may not have more than {self.MaxLSI} filtersorts"

    def keys(self):
        for name, attr in self.schema["properties"].items():
            if not attr.get("key", None):
                continue
            yield {
                "key_name": name,
                "key_type": attr["key"],
                "key_alias": attr.get("alias", None)
            }

    def attributes(self):
        for name, attr in self.schema["properties"].items():

            # Exclude Key attributes from attriubte list
            if attr.get("key", None) in ["HASH", "RANGE"]:
                continue

            return_attribute = {
                "attribute_name": name,
                "attribute_type": Maps.PyToDyn[attr["type"]]
            }

            # NOTE: is := syntax allowed in 3.8?
            # TODO: Assert always true if present?
            if fs := attr.get("filtersort"):
                return_attribute["filtersort"] = fs

            yield return_attribute


class DynamoTable():
    """
    """


    def __init__(self, entities, facets=None, strict=False):
        # control variables
        self.strict = strict

        # Raw data
        self.entities = self._set_listy(entities)
        self.facets = self._set_listy(facets, allow_none=True)

        # persisted data objects
        self.compile()

    def compile(self):
        """Re calculates everything in case entities changed"""
        self.attributes = list(self.key_attributes()) \
                        + list(self.nonkey_attributes()) \
                        + list(self.infer_lsi())

        self.keys = self.get_keys()  # object
        self.lsis = self.get_lsis()  # object
        self.gsis = []  # TODO: this one is hard
        self.meta = TableMeta(
            len(self.attributes),
            len(self.entities),
            len(self.lsis),
            len(self.gsis)
        )

    def _set_listy(self, schema, allow_none=False):
        if allow_none and not schema:
            return None
        if isinstance(schema, list):
            return schema
        elif isinstance(schema, dict):
            return [schema]
        else:
            raise TypeError(f"Schemas must be of type list or dict not: {type(entities)}")

    def asdict(self, refresh=False):
        if refresh:
            self.compile()

        return asdict(TableStruct(
            self.meta,
            self.keys,
            self.lsis,
            self.gsis,
            self.attributes
        ))

    def key_attributes(self):
        """ Iterates over every attribute in every

        :yield: [description]
        :rtype: [type]
        """

        key_attributes = {}
        key_attributes["partition_key"] = {
            "attribute_name": "pk",
            "attribute_type": "S",
            "alias_map": {}
        }
        key_attributes["sort_key"] = {
            "attribute_name": "sk",
            "attribute_type": "S",
            "alias_map": {}
        }

        for entity in self.entities:
            entity_name = entity.schema.get("title")
            for key in entity.keys():
                key_name = key["key_name"]
                if key_name == "pk":
                    key_attributes["partition_key"]["alias_map"][entity_name] \
                        = key["key_alias"]
                elif key_name == "sk":
                    key_attributes["sort_key"]["alias_map"][entity_name] \
                        = key["key_alias"]
                else:
                    KeyError(f"Unexpected key_name '{key_name}' in entity '{entity_name}'")

        for name, value in key_attributes.items():
            yield {
                "model": "key",
                **value
            }

    def nonkey_attributes(self):

        nonkey_attributes = dict()
        entity_state = dict()

        for entity in self.entities:

            entity_name = entity.schema.get("title")
            entity_state[entity_name] = dict()

            for attribute in entity.attributes():
                a = Attribute(attribute["attribute_name"], attribute["attribute_type"])

                # If exists enrich, else add
                if a.attribute_name in nonkey_attributes.keys():
                    if self.strict and a.attribute_type != nonkey_attributes[a.attribute_name]["attribute_type"]:  # TODO: .get -> attribute access
                        raise TypeError(f"Attribute '{a.attribute_name}' can not be multiple types: '{a.attribute_type}' & '{nonkey_attributes[a.attribute_name]['attribute_type']}'")  # # TODO: .get -> attribute access
                    nonkey_attributes[a.attribute_name]["facets"].append(entity_name)
                else:
                    nonkey_attributes[a.attribute_name] = attribute
                    nonkey_attributes[a.attribute_name]["facets"] = [entity_name]

        for name, value in nonkey_attributes.items():
            yield {
                "model": "attribute",
                **value
            }

    def infer_lsi(self) -> set:
        """Creates attr as LSI -> attr projection template
        """

        lsi_map = {}

        for entity in self.entities:

            entity_name = entity.schema["title"]
            lsi_seq = self._next_lsi()

            for attribute in entity.attributes():

                # Attributes with filtersort & are not a key item
                if attribute.get("filtersort") and not attribute.get("key", None):
                    lsi = next(lsi_seq)

                    if not lsi in lsi_map.keys():
                        lsi_map[lsi] = LSIAttribute(lsi, "S").asdict()

                    # TODO: Will I need to include the from 'type' map..?
                    lsi_map[lsi]["projection_sources"][entity_name] = attribute["attribute_name"]

        for key, value in lsi_map.items():
            yield {
                "model": "LSI",
                **value
            }

    @staticmethod
    def _next_lsi():
        for i in range (0,3):
            yield "LSI"+str(i+1)

    def get_keys(self):
        return TableKeySchema([
            Key("pk", "HASH"),
            Key("sk", "RANGE")
        ])

    def get_lsis(self):

        lsi_buffer = list()
        for lsi_attribute in self.infer_lsi():
            hash_key = Key("pk", "HASH")
            range_key = Key(lsi_attribute["attribute_name"], "RANGE")

            lsi = KeySchema(
                lsi_attribute["attribute_name"],
                [hash_key, range_key]
            )
            lsi_buffer.append(lsi)

        return IndexStruct(lsi_buffer)

    def get_gsis(self):
        pass