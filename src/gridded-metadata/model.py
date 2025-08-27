from rdflib import Graph, URIRef, BNode, Literal
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS, SDO, FOAF, Namespace

class WithAttrs:
    def __init__(self):
        self.attrs = {}

    def add_attr(self, key: str, value: str):
        self.attrs[key] = value

class DatasetElement(WithAttrs):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

class Dimension(DatasetElement):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size

class Array(DatasetElement):
    def __init__(self, name: str, dimensions: tuple[int, ...]):
        super().__init__(name)
        self.dimensions = dimensions
        self.references = []
    
    def add_reference(self, reference: DatasetElement):
        self.references.append(reference)

class Dataset(WithAttrs):
    def __init__(self):
        super().__init__()
        self.dimensions: dict[str, Dimension] = {}
        self.arrays: dict[str, Array] = {}

    def add_dimension(self, dimension: Dimension):
        self.dimensions[dimension.name] = dimension

    def add_array(self, array: Array):
        self.arrays[array.name] = array
    
    def get_data(self):
        return {
            "attrs": self.attrs,
            "dimensions": self.dimensions,
            "arrays": self.arrays
        }

FDRI = Namespace("http://fdri.ceh.ac.uk/vocab/metadata/")

class GraphBuilder:
    def __init__(self, dataset: Dataset, base_uri: str, mappings: dict, g: Graph):
        self.dataset = dataset
        self.base_uri = base_uri
        self.mappings = mappings
        self.g = g

    def build_graph(self) -> URIRef:
        ds_node = URIRef(f"{self.base_uri}")
        # Create properties for dataset attributes
        self.map_attrs(self.dataset, ds_node)
        self.map_dimensions(self.dataset, ds_node)
        self.map_arrays(self.dataset, ds_node)
        return ds_node
    
    def map_attrs(self, element: WithAttrs, element_node: URIRef):
        for key, value in element.attrs.items():
            if key not in self.mappings:
                continue
            mapping = self.mappings[key]
            self.apply_mapping(mapping, element, value, element_node)

    def apply_mapping(self, mapping: dict, element: WithAttrs, value: str, element_node: URIRef):
        if mapping['type'] == 'literal':
            predicate = mapping['predicate']
            self.g.add((element_node, predicate, Literal(value)))
        elif mapping['type'] == 'agent':
            predicate = mapping['predicate']
            name = element.attrs.get(mapping['name'])
            email = element.attrs.get(mapping['email'])
            agent_node = BNode()
            self.g.add((element_node, predicate, agent_node))
            self.g.add((agent_node, RDF.type, FDRI.Agent))
            if name:
                self.g.add((agent_node, RDFS.label, Literal(name)))
            if email:
                self.g.add((agent_node, FOAF.mbox, Literal(email)))
        elif mapping['type'] == 'annotation':
            property_uri = mapping['property']
            annotation_node = BNode()
            self.g.add((annotation_node, RDF.type, FDRI.Annotation))
            self.g.add((annotation_node, FDRI.property, property_uri))
            value_node = BNode()
            self.g.add((annotation_node, FDRI.hasValue, value_node))
            self.g.add((value_node, RDF.type, SDO.PropertyValue))
            self.g.add((value_node, SDO.value, Literal(value)))
            self.g.add((element_node, FDRI.hasAnnotation, annotation_node))

    def map_dimensions(self, dataset: Dataset, ds_node: URIRef):
        for dim in dataset.dimensions.values():
            dim_node = URIRef(f"{self.base_uri}#dimension-{dim.name}")
            self.g.add((ds_node, FDRI.contains, dim_node))
            self.g.add((dim_node, RDF.type, FDRI.Dimension))
            self.g.add((dim_node, RDFS.label, Literal(dim.name)))
            self.g.add((dim_node, FDRI.hasSize, Literal(dim.size)))
    
    def map_arrays(self, dataset: Dataset, ds_node: URIRef):
        for array in dataset.arrays.values():
            array_node = URIRef(f"{self.base_uri}#{array.name}")
            self.g.add((ds_node, FDRI.contains, array_node))
            self.g.add((array_node, RDF.type, FDRI.Array))
            self.g.add((array_node, RDFS.label, Literal(array.name)))
            self.g.add((array_node, FDRI.shape, self.make_shape(array.dimensions)))
            self.map_attrs(array, array_node)
    
    def make_shape(self, shape: tuple[int, ...]) -> BNode:
        shape_node = BNode()
        collection = Collection(self.g, shape_node)
        for dim in shape:
            collection.append(Literal(dim))
        return shape_node

def build_graph(dataset: Dataset, base_uri: str, mappings: dict) -> Graph:
    g = Graph()
    g.namespace_manager.bind("fdri", FDRI)
    builder = GraphBuilder(dataset, base_uri, mappings, g)
    builder.build_graph()
    return g