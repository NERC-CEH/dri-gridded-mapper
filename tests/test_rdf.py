
from rdflib import SDO, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, FOAF, Namespace, RDF, RDFS

from gridded_metadata import mapper, model

FDRI = Namespace("http://fdri.ceh.ac.uk/vocab/metadata/")

ATTR_MAP = {
    "title": { 'type': 'literal', 'predicate': DCTERMS.title },
    "summary": { 'type': 'literal', 'predicate': DCTERMS.description },
    "standard_name": { 'type': 'literal', 'predicate': DCTERMS.identifier },
    "long_name": { 'type': 'literal', 'predicate': DCTERMS.title },
    "comment": { 'type': 'literal', 'predicate': RDFS.comment },
    "EPSG_code": {
        'type': 'annotation',
        'property': URIRef('http://fdri.ceh.ac.uk/ref/common/cop/epsg-code')
    },
    "creator_name": {
        'type': 'agent',
        'predicate': DCTERMS.creator,
        'name': 'creator_name',
        'email': 'creator_email'
    }
}

def test_literal_attributes() -> None:
    ds = model.Dataset()
    ds.add_attr("title", "Test Dataset")
    ds.add_attr("summary", "A dataset for testing")
    g = mapper.build_graph(ds, "http://example.com/dataset", ATTR_MAP)
    ds = URIRef("http://example.com/dataset")
    assert (ds, DCTERMS.title, Literal("Test Dataset")) in g
    assert (ds, DCTERMS.description, Literal("A dataset for testing")) in g

def test_agent_attribute() -> None:
    ds = model.Dataset()
    ds.add_attr("creator_name", "Jane Doe")
    ds.add_attr("creator_email", "jane.doe@example.com")
    g = mapper.build_graph(ds, "http://example.com/dataset", ATTR_MAP)
    ds = URIRef("http://example.com/dataset")
    matches = list(g.triples((ds, DCTERMS.creator, None)))
    assert len(matches) == 1
    agent = matches[0][2]
    assert (ds, DCTERMS.creator, agent) in g
    assert (agent, RDFS.label, Literal("Jane Doe")) in g
    assert (agent, FOAF.mbox, Literal("jane.doe@example.com")) in g

def test_annotation_mapping() -> None:
    ds = model.Dataset()
    ds.add_attr("EPSG_code", "EPSG:4326")
    g = mapper.build_graph(ds, "http://example.com/dataset", ATTR_MAP)
    ds = URIRef("http://example.com/dataset")
    annotation_triples = list(g.triples((ds, FDRI.hasAnnotation, None)))
    assert len(annotation_triples) == 1
    annotation = annotation_triples[0][2]
    assert (annotation, RDF.type, FDRI.Annotation) in g
    assert (annotation, FDRI.property, URIRef("http://fdri.ceh.ac.uk/ref/common/cop/epsg-code")) in g
    annotation_value_triples = list(g.triples((annotation, FDRI.hasValue, None)))
    assert len(annotation_value_triples) == 1
    annotation_value = annotation_value_triples[0][2]
    assert (annotation_value, RDF.type, SDO.PropertyValue) in g
    assert (annotation_value, SDO.value, Literal("EPSG:4326")) in g

def test_dimension_mapping() -> None:
    ds = model.Dataset()
    dim = model.Dimension(name="time", size=10)
    ds.add_dimension(dim)
    g = mapper.build_graph(ds, "http://example.com/dataset", ATTR_MAP)
    ds_node = URIRef("http://example.com/dataset")
    dim_node = URIRef("http://example.com/dataset#dimension-time")
    assert (ds_node, FDRI.contains, dim_node) in g
    assert (dim_node, FDRI.size, Literal(10)) in g

def test_array_mapping() -> None:
    ds = model.Dataset()
    dim = model.Dimension(name="lat", size=5)
    ds.add_dimension(dim)
    array = model.Array(name="lat", dimensions=[180])
    array.add_attr("standard_name", "latitude")
    array.add_reference(dim)
    ds.add_array(array)
    g = mapper.build_graph(ds, "http://example.com/dataset", ATTR_MAP)
    ds_node = URIRef("http://example.com/dataset")
    array_node = URIRef("http://example.com/dataset#lat")
    assert (ds_node, FDRI.contains, array_node) in g
    assert (array_node, RDF.type, FDRI.Array) in g
    assert (array_node, RDFS.label, Literal("lat")) in g
    assert (array_node, DCTERMS.identifier, Literal("latitude")) in g
    shape_triples = list(g.triples((array_node, FDRI.shape, None)))
    assert len(shape_triples) == 1
    collection = Collection(g, shape_triples[0][2])
    assert len(collection) == 1
    assert collection[0] == Literal(180)
    dim_node = URIRef("http://example.com/dataset#dimension-lat")
    assert (array_node, FDRI.references, dim_node) in g
