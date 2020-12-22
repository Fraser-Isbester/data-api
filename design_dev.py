import json


def main():

    entity_schemas = [
        "/Users/fraser/Documents/Dev/personal/data-api/examples/entity_1.json",
        "/Users/fraser/Documents/Dev/personal/data-api/examples/entity_2.json"
    ]

    entities = []
    for fp in entity_schemas:
        with open(fp, "r") as f:
            entity_buffer = EntitySchema(json.loads(f.read()))
        entities.append(entity_buffer)

    table = DynamoTable(entities, strict=True)

    for attr in table.nonkey_attributes():
        print(attr)

    for key in table.key_attributes():
        print(key)

    print(table.infer_lsi())

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

class AccessSchema(Schema):
    pass


class EntitySchema(Schema):

    MaxLSI = 3
    MaxGSI = 3

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

class DynamoTable:

    def __init__(self, entities, facets=None, strict=False):
        # control variables
        self.strict = strict

        # raw data
        self.entities = self._set_listy(entities)

    def _set_listy(self, schema):
        if isinstance(schema, list):
            return schema
        elif isinstance(schema, dict):
            return [schema]
        else:
            raise TypeError(f"Schemas must be of type list or dict not: {type(entities)}")

    def key_attributes(self):

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
            yield value


    def nonkey_attributes(self):

        nonkey_attributes = dict()
        entity_state = dict()

        for entity in self.entities:

            entity_name = entity.schema.get("title")
            entity_state[entity_name] = dict()

            for attribute in entity.attributes():
                attr_name = attribute["attribute_name"]
                attr_type = attribute["attribute_type"]

                # If exists enrich, else add
                if attr_name in nonkey_attributes.keys():
                    if self.strict and attr_type != nonkey_attributes[attr_name]["attribute_type"]:
                        raise TypeError(f"Attribute '{attr_name}' can not be multiple types: '{attr_type}' & '{nonkey_attributes[attr_name]['attribute_type']}'")
                    nonkey_attributes[attr_name]["facets"].append(entity_name)
                else:
                    nonkey_attributes[attr_name] = attribute
                    nonkey_attributes[attr_name]["facets"] = [entity_name]

        for name, value in nonkey_attributes.items():
            yield value

    def infer_lsi(self):

        entity_state = dict()

        for entity in self.entities:

            lsi_seq = self._next_lsi()

            entity_name = entity.schema.get("title")
            entity_state[entity_name] = dict()

            for attribute in entity.attributes():
                if attribute.get("filtersort"):
                    entity_state[entity_name][next(lsi_seq)] = attribute["attribute_name"]

        return entity_state

    @staticmethod
    def _next_lsi():
        for i in range (0,3):
            yield "LSI"+str(i+1)

if __name__ == "__main__":
    main()