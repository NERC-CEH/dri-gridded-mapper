from rdflib import URIRef
from rdflib.namespace import DCTERMS, Namespace

from gridded_metadata.mapper import read_mappings

FDRI = Namespace("http://fdri.ceh.ac.uk/vocab/metadata/")

def test_read_mappings() -> None:
    mappings = read_mappings("tests/data/mappings.json")
    assert mappings == {
        "title": {
            "predicate": FDRI.title,
            "type": "literal"
        },
        "creator": {
            "predicate": DCTERMS.creator,
            "type": "agent",
            "name": "creator_name",
            "email": "creator_email"
        },
        "annotation": {
            "type": "annotation",
            "property": URIRef("http://fdri.ceh.ac.uk/ref/common/cop/some-property")
        }
    }
