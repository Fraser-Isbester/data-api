from dataclasses import dataclass, asdict, field

@dataclass
class Data:
    def asdict(self):
        return asdict(self)

    def __post_init__(self):
        if getattr(self, "_validate", None):
            self._validate()


@dataclass
class DynAttribute(Data):
    attribute_name: str  # Dynamo Name of this Attribute
    attribute_type: str  # Dynamo Type of this attribute


@dataclass
class Attribute(DynAttribute):
    facets: list = field(default_factory=list)
    model: str = "Attribute"


@dataclass
class KeyAttribute(DynAttribute):
    alias_map: dict = field(default_factory=dict)
    model: str = "Key"


@dataclass
class LSIAttribute(DynAttribute):
    projection_sources: dict = field(default_factory=dict)
    model: str = "LSI"


@dataclass
class AttributeStruct(Data):
    attributes: list[(Attribute, KeyAttribute, LSIAttribute)]


@dataclass
class Key(Data):
    """Dynamo Key description"""

    attribute_name: str
    key_type: str

    def _validate(self):
        assert self.key_type in ["HASH", "RANGE"], \
            f"Key type must be 'HASH' or 'RANGE' not '{self.key_type}'"


@dataclass
class TableKeySchema(Data):
    attribute_defintions: list[Key]


@dataclass
class KeySchema(Data):
    """Key Schema for LSI and GSI structures"""

    index_name: str
    key_schema: list[Key]
    projection: str = '{"projection_type": "KEYS_ONLY"}'


@dataclass
class IndexStruct(Data):
    """Compiled LSI or GSI struct"""

    indexes: list[KeySchema]

    def __len__(self):
        return len(self.indexes)


@dataclass
class TableMeta(Data):
    attribute_count: int
    entitie_count: int
    lsi_count: int
    gsi_count: int


# Pure structs only
@dataclass
class TableStruct(Data):
    metadata: TableMeta
    keys: TableKeySchema
    local_secondary_indexes: IndexStruct
    global_secondary_indexes: IndexStruct
    attributes: AttributeStruct