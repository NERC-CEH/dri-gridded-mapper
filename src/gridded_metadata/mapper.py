import logging

from rdf_mapper.lib.template_processor import TemplateProcessor
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS, XSD, Namespace

from gridded_metadata.model import Array, Dataset, Dimension, WithAttrs

FDRI = Namespace("http://fdri.ceh.ac.uk/vocab/metadata/")
SDO = Namespace("http://schema.org/")

class GraphBuilder:
    def __init__(self, dataset: Dataset, base_uri: str, template_processor: TemplateProcessor):
        self.dataset = dataset
        self.base_uri = base_uri
        self.base_uri_node = URIRef(f"{base_uri}")
        self.template_processor = template_processor
        self.store = template_processor.dataset

    def build_graph(self) -> URIRef:
        ds_node = URIRef(f"{self.base_uri}")
        self.store.add((ds_node, RDF.type, FDRI.GriddedContainer))
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
        logging.info(f"Mapping attributes for {element_node} with {values}")
        self.template_processor.process_row(values)

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
            for ix in range(len(array.references)):
                reference = array.references[ix]
                ref_node = self.node_for(reference)
                item_node = BNode()
                self.store.add((array_node, FDRI.referenceList, item_node))
                self.store.add((item_node, RDF.type, FDRI.GriddedArrayItem))
                self.store.add((item_node, FDRI['index'], Literal(ix, datatype=XSD.nonNegativeInteger)))
                self.store.add((item_node, SDO.valueReference, ref_node))
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
