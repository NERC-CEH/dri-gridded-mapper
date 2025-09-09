
import json

from rdf_mapper.lib.template_processor import TemplateProcessor
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SDO, Namespace, NamespaceManager

from gridded_metadata.model import Array, Dataset, Dimension, WithAttrs

FDRI = Namespace("http://fdri.ceh.ac.uk/vocab/metadata/")

def _expand_uri(uri_or_curie: str, ns_mgr: NamespaceManager) -> URIRef:
    if isinstance(uri_or_curie, URIRef):
        return uri_or_curie
    if uri_or_curie.startswith("http://") or uri_or_curie.startswith("https://"):
        return URIRef(uri_or_curie)
    return ns_mgr.expand_curie(uri_or_curie)

def _expand_mapping(mapping: dict, ns_mgr: NamespaceManager) -> dict:
    ret = mapping.copy()
    if 'predicate' in mapping:
        ret['predicate'] = _expand_uri(mapping['predicate'], ns_mgr)
    if 'property' in mapping:
        ret['property'] = _expand_uri(mapping['property'], ns_mgr)
    return ret

def read_mappings(file_path: str) -> dict:
    with open(file_path, "r") as f:
        config = json.load(f)
    store = Graph()
    ns_mgr = NamespaceManager(store)
    for prefix, uri in config.get("namespaces", {}).items():
        ns_mgr.bind(prefix, Namespace(uri))
    ret = {}
    src_mappings = config.get("mappings", {})
    for mapping_key, mapping_value in src_mappings.items():
        ret[mapping_key] = _expand_mapping(mapping_value, ns_mgr)
    return ret


class GraphBuilder:
    def __init__(self, dataset: Dataset, base_uri: str, template_processor: TemplateProcessor):
        self.dataset = dataset
        self.base_uri = base_uri
        self.base_uri_node = URIRef(f"{base_uri}")
        self.template_processor = template_processor
        self.store = template_processor.dataset

    def build_graph(self) -> URIRef:
        ds_node = URIRef(f"{self.base_uri}")
        self.store.add((ds_node, RDF.type, FDRI.Container))
        # Create properties for dataset attributes
        self.map_attrs(self.dataset, ds_node)
        self.map_dimensions(self.dataset, ds_node)
        self.map_arrays(self.dataset, ds_node)
        return ds_node

    def map_attrs(self, element: WithAttrs, element_node: URIRef) -> None:
        values = element.attrs.copy()
        values['$base'] = self.base_uri
        values['$resource'] = element_node
        values['$type'] = type(element).__name__
        self.template_processor.process_row(values)

    def apply_mapping(self, mapping: dict, element: WithAttrs, value: str, element_node: URIRef) -> None:
        if mapping['type'] == 'literal':
            predicate = mapping['predicate']
            self.store.add((element_node, predicate, Literal(value)))
        elif mapping['type'] == 'agent':
            predicate = mapping['predicate']
            name = element.attrs.get(mapping['name'])
            email = element.attrs.get(mapping['email'])
            agent_node = BNode()
            self.store.add((element_node, predicate, agent_node))
            self.store.add((agent_node, RDF.type, FDRI.Agent))
            if name:
                self.store.add((agent_node, RDFS.label, Literal(name)))
            if email:
                self.store.add((agent_node, FOAF.mbox, Literal(email)))
        elif mapping['type'] == 'annotation':
            property_uri = mapping['property']
            annotation_node = BNode()
            self.store.add((annotation_node, RDF.type, FDRI.Annotation))
            self.store.add((annotation_node, FDRI.property, property_uri))
            value_node = BNode()
            self.store.add((annotation_node, FDRI.hasValue, value_node))
            self.store.add((value_node, RDF.type, SDO.PropertyValue))
            self.store.add((value_node, SDO.value, Literal(value)))
            self.store.add((element_node, FDRI.hasAnnotation, annotation_node))

    def map_dimensions(self, dataset: Dataset, ds_node: URIRef) -> None:
        for dim in dataset.dimensions.values():
            dim_node = self.node_for(dim)
            self.store.add((ds_node, FDRI.contains, dim_node))
            self.store.add((dim_node, RDF.type, FDRI.Dimension))
            self.store.add((dim_node, RDFS.label, Literal(dim.name)))
            self.store.add((dim_node, FDRI.size, Literal(dim.size)))

    def node_for(self, element: WithAttrs) -> URIRef:
        if isinstance(element, Dataset):
            return URIRef(f"{self.base_uri}")
        if isinstance(element, Dimension):
            return URIRef(f"{self.base_uri}#dimension-{element.name}")
        if isinstance(element, Array):
            return URIRef(f"{self.base_uri}#{element.name}")
        raise ValueError(f"Unknown element type: {type(element)}")

    def map_arrays(self, dataset: Dataset, ds_node: URIRef) -> None:
        for array in dataset.arrays.values():
            array_node = self.node_for(array)
            self.store.add((ds_node, FDRI.contains, array_node))
            self.store.add((array_node, RDF.type, FDRI.Array))
            self.store.add((array_node, RDFS.label, Literal(array.name)))
            if len(array.dimensions):
                self.store.add((array_node, FDRI.shape, self.make_shape(array.dimensions)))
            for reference in array.references:
                ref_node = self.node_for(reference)
                self.store.add((array_node, FDRI.references, ref_node))
            self.map_attrs(array, array_node)

    def make_shape(self, shape: list[int]) -> BNode:
        shape_node = BNode()
        collection = Collection(self.store, shape_node)
        for dim in shape:
            collection.append(Literal(dim))
        return shape_node

def build_graph(dataset: Dataset, base_uri: str, template_processor: TemplateProcessor) -> Graph:
    store = template_processor.dataset
    store.namespace_manager.bind("fdri", FDRI)
    builder = GraphBuilder(dataset, base_uri, template_processor)
    builder.build_graph()
    return store
